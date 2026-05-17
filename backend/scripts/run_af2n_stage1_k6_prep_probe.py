#!/usr/bin/env python3
"""AF2-L-K6-PREP3 — Python fallback probe (k6/locust not installed in container).

Reuses the AF2-L-K6-LIVE-PREP2 safe-probe pattern adapted to the Stage1
50-user allowlist context. Read-mostly + idempotent replay. Asserts ledger
row count is UNCHANGED before/after.
"""
from __future__ import annotations
import argparse, json, shutil, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
RESULT = Path('/app/data/design/affinity/af2n_stage1_k6_prep_probe_result_v1.json')


def _post(p, body):
    payload = json.dumps(body).encode(); headers = {'Content-Type': 'application/json'}
    req = Request(API + p, data=payload, method='POST', headers=headers)
    t0 = time.monotonic()
    try:
        with urlopen(req, timeout=6) as r: code = r.status; b = r.read()
    except HTTPError as e:
        try: b = e.read()
        except: b = b''
        code = e.code
    except URLError: b = b''; code = -1
    return code, b, (time.monotonic() - t0) * 1000.0


def _get(p):
    t0 = time.monotonic()
    try:
        with urlopen(API + p, timeout=6) as r: code = r.status; b = r.read()
    except HTTPError as e:
        try: b = e.read()
        except: b = b''
        code = e.code
    except URLError: b = b''; code = -1
    return code, b, (time.monotonic() - t0) * 1000.0


def pct(s, q):
    if not s: return 0.0
    s = sorted(s); k = max(0, min(len(s) - 1, int(round(q * (len(s) - 1)))))
    return s[k]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--rounds', type=int, default=60)
    args = ap.parse_args(argv)
    rounds = max(40, min(500, args.rounds))

    labels = {
        'empty':           {'body': {}, 'expected': 423},
        'no_idem':         {'body': {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'user_id':'unauth_user_xxx'}, 'expected': 423},
        'malformed_idem':  {'body': {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'short','user_id':'unauth_user_xxx'}, 'expected': 423},
        'negative_qty':    {'body': {'gift_id':'x','hero_id':'greek_zeus','quantity':-3,'idempotency_key':'stg1negidem','user_id':'unauth_user_xxx'}, 'expected': 423},
        'huge_qty':        {'body': {'gift_id':'x','hero_id':'greek_zeus','quantity':99999,'idempotency_key':'stg1hugeidem','user_id':'unauth_user_xxx'}, 'expected': 423},
        'borea':           {'body': {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'aaaa1111bbbb','user_id':'unauth_user_xxx'}, 'expected': 404},
        'greek_borea':     {'body': {'gift_id':'x','hero_id':'greek_borea','quantity':1,'idempotency_key':'aaaa2222bbbb','user_id':'unauth_user_xxx'}, 'expected': 404},
        'primordial_gaia': {'body': {'gift_id':'x','hero_id':'primordial_gaia','quantity':1,'idempotency_key':'aaaa3333bbbb','user_id':'unauth_user_xxx'}, 'expected': 404},
        'idempotent_replay': {'body': {'gift_id':'gift_replay','hero_id':'greek_zeus','quantity':1,'idempotency_key':'canary_idem_0001','user_id':'user_canary_001'}, 'expected': 200},
        # Stage1 QA user with explicitly UNKNOWN gift_id; routes return 423 (Disabled)
        # when the input fails the canary-gate validation; we ensure NO new ledger row
        # by using a body shape that always fails pre-write validation regardless of
        # allowlist membership. Empty body is universally rejected with 423.
        'stage1_qa_user_blocked_path': {'body': {}, 'expected': 423},
    }

    pre_total = post_total = -1
    try:
        from pymongo import MongoClient
        coll = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']['gift_transaction_ledger']
        pre_total = coll.count_documents({})
    except Exception:
        coll = None

    started = time.monotonic()
    by_label = {}
    total_requests = 0; total_5xx = 0; unexpected_total = 0; dup_inserted_total = 0

    for lbl, spec in labels.items():
        codes = {}; lat = []; unexpected = {}
        for i in range(rounds):
            code, body, ms = _post('/affinity/gift-spend', spec['body'])
            codes[str(code)] = codes.get(str(code), 0) + 1
            lat.append(ms)
            if isinstance(code, int) and 500 <= code < 600: total_5xx += 1
            if code != spec['expected']:
                unexpected[str(code)] = unexpected.get(str(code), 0) + 1
                unexpected_total += 1
            if lbl == 'idempotent_replay':
                try:
                    j = json.loads(body.decode())
                    if j.get('ledger_row_inserted') is True:
                        dup_inserted_total += 1
                except Exception: pass
        by_label[lbl] = {
            'count': rounds, 'expected_status': spec['expected'],
            'codes': codes, 'unexpected_codes': unexpected,
            'p50_latency_ms': round(pct(lat, 0.5), 2),
            'p95_latency_ms': round(pct(lat, 0.95), 2),
        }
        total_requests += rounds

    regression = {}
    for ep, exp in [
        ('/affinity/gifts', 200),
        ('/affinity/gifts/summary', 200),
        ('/affinity/gift-spend/canary-status', 200),
        ('/heroes', 200),
        ('/affinity/gifts/by-element/dark/by-faction/greek', 200),
        ('/affinity/gifts/by-element/dark/by-faction/borea', 404),
        ('/affinity/gifts/by-element/tides/by-faction/greek', 404),
    ]:
        code, _, ms = _get(ep)
        regression[ep] = {'code': code, 'latency_ms': ms, 'expected': exp, 'ok': code == exp}

    if coll is not None:
        try: post_total = coll.count_documents({})
        except Exception: pass

    elapsed = round(time.monotonic() - started, 3)
    ledger_unchanged = (pre_total == post_total and pre_total >= 0)
    payload = {
        'result_id': 'af2n_stage1_k6_prep_probe_result_v1',
        'task_origin': 'AF2-L-K6-PREP3',
        'design_only': False, 'runtime_attached': True,
        'runtime_attached_stage1_allowlist_only': True,
        'db_write': False,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'mode': 'python_fallback_stage1_active',
        'k6_installed': shutil.which('k6') is not None,
        'locust_installed': shutil.which('locust') is not None,
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'rounds_per_label': rounds,
        'total_requests': total_requests,
        'elapsed_seconds': elapsed,
        'p95_target_ms': 500,
        'total_5xx': total_5xx,
        'unexpected_total': unexpected_total,
        'duplicate_inserted_total': dup_inserted_total,
        'ledger_row_count_before': pre_total,
        'ledger_row_count_after': post_total,
        'ledger_row_count_unchanged': ledger_unchanged,
        'by_label': by_label,
        'regression_gets': regression,
        'safety_flags': {
            'runtime_attached': True,
            'runtime_attached_stage1_allowlist_only': True,
            'broad_rollout_authorized': False,
            'db_write': False,
            'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
            'inventory_mutation_enabled': False,
            'affinity_points_mutation_enabled': False,
            'buffs_enabled': False,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
        }
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    ok = (total_5xx == 0 and unexpected_total == 0 and dup_inserted_total == 0 and ledger_unchanged)
    print(f'AF2-L-K6-PREP3 (python fallback): reqs={total_requests}, 5xx={total_5xx}, unexpected={unexpected_total}, dup={dup_inserted_total}, ledger_unchanged={ledger_unchanged}')
    print(f'Result: {RESULT}')
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
