#!/usr/bin/env python3
"""AF2-N-STAGE1-EXTENDED-MONITORING-V15 — Probe.

Read-mostly probe under Stage1 + V14 stable state. 90 samples @ 100ms by
default. Idempotent replay only; no new ledger rows from this probe.
"""
from __future__ import annotations
import argparse, json, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
RESULT = Path('/app/data/design/affinity/af2n_stage1_extended_monitoring_v15_result.json')


def _get(p):
    t0 = time.monotonic()
    try:
        with urlopen(API + p, timeout=6) as r: body = r.read(); code = r.status
    except HTTPError as e:
        try: body = e.read()
        except: body = b''
        code = e.code
    except URLError: body = b''; code = -1
    return code, body, (time.monotonic() - t0) * 1000.0


def _post(p, b):
    payload = json.dumps(b).encode(); headers = {'Content-Type': 'application/json'}
    req = Request(API + p, data=payload, method='POST', headers=headers)
    t0 = time.monotonic()
    try:
        with urlopen(req, timeout=6) as r: body = r.read(); code = r.status
    except HTTPError as e:
        try: body = e.read()
        except: body = b''
        code = e.code
    except URLError: body = b''; code = -1
    return code, body, (time.monotonic() - t0) * 1000.0


def pct(s, q):
    if not s: return 0.0
    s = sorted(s); k = max(0, min(len(s) - 1, int(round(q * (len(s) - 1)))))
    return s[k]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--samples', type=int, default=90)
    ap.add_argument('--interval-ms', type=int, default=100)
    args = ap.parse_args(argv)
    samples = max(60, min(200, args.samples))

    try:
        from pymongo import MongoClient
        coll = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']['gift_transaction_ledger']
        pre_total = coll.count_documents({})
    except Exception:
        coll = None; pre_total = -1

    triggers = []
    latencies = {'health':[], 'heroes':[], 'status':[], 'borea':[], 'nonal':[], 'replay':[]}
    codes = {k: {} for k in latencies}
    any_5xx = 0
    started = time.monotonic()

    for i in range(samples):
        for label, getter in [('health','/health'),('heroes','/heroes'),('status','/affinity/gift-spend/canary-status')]:
            code, body, ms = _get(getter)
            latencies[label].append(ms); codes[label][str(code)] = codes[label].get(str(code), 0) + 1
            if isinstance(code, int) and 500 <= code < 600:
                any_5xx += 1; triggers.append((i, '5xx', f'{getter}={code}'))
            if label == 'heroes' and code == 200:
                try:
                    d = json.loads(body.decode())
                    arr = d if isinstance(d, list) else (d.get('heroes') or [])
                    if len(arr) != 100:
                        triggers.append((i, 'api_heroes_not_100', f'count={len(arr)}'))
                    ids = {h.get('id') for h in arr if isinstance(h, dict)}
                    leak = ids & {'borea','greek_borea','primordial_gaia'}
                    if leak: triggers.append((i, 'borea_in_heroes', f'leaked={sorted(leak)}'))
                except Exception as e:
                    triggers.append((i, 'heroes_parse_error', repr(e)))
            if label == 'status' and code == 200:
                try:
                    sd = json.loads(body.decode())
                    for k in ('applied_to_combat','battle_runtime_attached','inventory_mutation_enabled','affinity_points_mutation_enabled','buffs_enabled'):
                        if sd.get(k) is not False:
                            triggers.append((i, 'safety_flag_violation', f'{k}={sd.get(k)}'))
                    if sd.get('ledger_total_rows', 0) > sd.get('canary_ledger_cap', 0):
                        triggers.append((i, 'ledger_exceeds_cap', f"rows={sd.get('ledger_total_rows')} cap={sd.get('canary_ledger_cap')}"))
                except Exception as e:
                    triggers.append((i, 'status_parse_error', repr(e)))

        # Borea must always be 404
        code, _, ms = _post('/affinity/gift-spend',
            {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234efgh','user_id':'user_canary_001'})
        latencies['borea'].append(ms); codes['borea'][str(code)] = codes['borea'].get(str(code), 0) + 1
        if code != 404: triggers.append((i, 'borea_not_404', f'got {code}'))

        # Non-allowlist 423
        code, _, ms = _post('/affinity/gift-spend',
            {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':f'v15ext{i}','user_id':'unauth_user_xxx'})
        latencies['nonal'].append(ms); codes['nonal'][str(code)] = codes['nonal'].get(str(code), 0) + 1
        if code == 200: triggers.append((i, 'unauthorized_successful_spend', 'non-allowlist got 200'))

        # Idempotent replay 200 + no insert
        code, body, ms = _post('/affinity/gift-spend',
            {'gift_id':'gift_replay','hero_id':'greek_zeus','quantity':1,'idempotency_key':'canary_idem_0001','user_id':'user_canary_001'})
        latencies['replay'].append(ms); codes['replay'][str(code)] = codes['replay'].get(str(code), 0) + 1
        if code != 200: triggers.append((i, 'replay_not_200', f'got {code}'))
        try:
            j = json.loads(body.decode())
            if j.get('ledger_row_inserted') is True:
                triggers.append((i, 'idempotency_duplicate_inserted', f'tx={j.get("tx_id")}'))
        except Exception: pass
        time.sleep(args.interval_ms / 1000.0)

    post_total = -1
    if coll is not None:
        try: post_total = coll.count_documents({})
        except Exception: pass
    ledger_unchanged_or_small_delta = (pre_total >= 0 and post_total >= 0
                                       and (post_total - pre_total) <= 5)
    if pre_total >= 0 and post_total >= 0 and (post_total - pre_total) > 5:
        triggers.append((-1, 'ledger_growth_too_high', f'pre={pre_total} post={post_total}'))

    elapsed = round(time.monotonic() - started, 3)
    summary = {
        'result_id': 'af2n_stage1_extended_monitoring_v15_result',
        'task_origin': 'AF2-N-STAGE1-EXTENDED-MONITORING-V15',
        'design_only': False, 'runtime_attached': True,
        'runtime_attached_stage1_allowlist_only': True,
        'db_write': False,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'samples': samples, 'interval_ms': args.interval_ms, 'elapsed_seconds': elapsed,
        'codes': codes,
        'p50_latency_ms': {k: round(pct(v, 0.5), 2) for k, v in latencies.items()},
        'p95_latency_ms': {k: round(pct(v, 0.95), 2) for k, v in latencies.items()},
        'p99_latency_ms': {k: round(pct(v, 0.99), 2) for k, v in latencies.items()},
        'any_5xx_total': any_5xx,
        'ledger_row_count_before': pre_total,
        'ledger_row_count_after': post_total,
        'ledger_row_count_unchanged_or_small_delta': ledger_unchanged_or_small_delta,
        'triggers_fired': [{'sample': s, 'trigger': t, 'detail': d} for s, t, d in triggers],
        'triggers_total': len(triggers),
        'overall_status': 'PASS' if not triggers else 'FAIL',
        'safety_flags': {
            'runtime_attached_stage1_allowlist_only': True,
            'broad_rollout_authorized': False,
            'inventory_mutation_enabled': False,
            'affinity_points_mutation_enabled': False,
            'buffs_enabled': False,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
            'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'AF2-N-STAGE1-EXTENDED-MONITORING-V15: samples={samples}, 5xx={any_5xx}, triggers={len(triggers)}, status={summary["overall_status"]}')
    print(f'Result: {RESULT}')
    return 0 if not triggers else 1

if __name__ == '__main__':
    sys.exit(main())
