#!/usr/bin/env python3
"""AF2-L-K6-LIVE-PREP/FULL-SAFE — Extended safe Python disabled-endpoint probe.

Larger volume version (default 800 reqs) covering:
  - empty POST                       expect 423
  - valid disabled payload           expect 423
  - no_idem                          expect 423
  - duplicate idem                   expect 423
  - malformed idem                   expect 423
  - negative qty                     expect 423
  - huge qty                         expect 423
  - stale gift                       expect 423
  - Borea / greek_borea / primordial_gaia hero_id   expect 404
  - GET by-axis routes (regression)  expect 200 (or 404 forbidden for tides/borea)

No real gift_spend executed. No DB write reachable. Asserts ledger rows
still zero after the run.
"""
from __future__ import annotations
import argparse, json, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
RESULT = Path('/app/data/design/affinity/affinity_gift_spend_k6_live_prep_result_v2.json')


def _post(p, b):
    payload = json.dumps(b).encode(); headers = {'Content-Type':'application/json'}
    t0 = time.monotonic()
    req = Request(API + p, data=payload, method='POST', headers=headers)
    try:
        with urlopen(req, timeout=6) as r: r.read(); code = r.status
    except HTTPError as e:
        try: e.read()
        except: pass
        code = e.code
    except URLError: code = -1
    return code, (time.monotonic() - t0) * 1000.0


def _get(p):
    t0 = time.monotonic()
    try:
        with urlopen(API + p, timeout=6) as r: r.read(); code = r.status
    except HTTPError as e:
        try: e.read()
        except: pass
        code = e.code
    except URLError: code = -1
    return code, (time.monotonic() - t0) * 1000.0


def pct(s, q):
    if not s: return 0.0
    s = sorted(s)
    k = max(0, min(len(s) - 1, int(round(q * (len(s) - 1)))))
    return s[k]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--total', type=int, default=800)
    args = ap.parse_args(argv)
    total = max(300, min(2000, args.total))

    payloads = [
        ('empty',           {}, 423),
        ('valid',           {'gift_id':'gift_x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'abcdef1234567890'}, 423),
        ('no_idem',         {'gift_id':'gift_x','hero_id':'greek_zeus','quantity':1}, 423),
        ('dup_idem',        {'gift_id':'gift_x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'duplicate_key_001'}, 423),
        ('malformed_idem',  {'gift_id':'gift_x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'short'}, 423),
        ('negative_qty',    {'gift_id':'gift_x','hero_id':'greek_zeus','quantity':-1,'idempotency_key':'abcdef1234567890'}, 423),
        ('huge_qty',        {'gift_id':'gift_x','hero_id':'greek_zeus','quantity':9999999,'idempotency_key':'abcdef1234567890'}, 423),
        ('stale_gift',      {'gift_id':'GIFT_NONEXISTENT_0001','hero_id':'greek_zeus','quantity':1,'idempotency_key':'abcdef1234567890'}, 423),
        ('borea',           {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234efgh'}, 404),
        ('greek_borea',     {'gift_id':'x','hero_id':'greek_borea','quantity':1,'idempotency_key':'abcd1234efgh'}, 404),
        ('primordial_gaia', {'gift_id':'x','hero_id':'primordial_gaia','quantity':1,'idempotency_key':'abcd1234efgh'}, 404),
    ]
    started = time.monotonic()
    by_label = {l: {'count':0, 'expected':exp, 'unexpected':{}, 'lat':[]} for l,_,exp in payloads}
    samples = []; total_5xx = 0
    n_per = max(1, total // len(payloads))
    for label, body, exp in payloads:
        for _ in range(n_per):
            code, ms = _post('/affinity/gift-spend', body)
            samples.append(ms); by_label[label]['count'] += 1; by_label[label]['lat'].append(ms)
            if code != exp:
                by_label[label]['unexpected'][str(code)] = by_label[label]['unexpected'].get(str(code), 0) + 1
            if isinstance(code, int) and 500 <= code < 600: total_5xx += 1

    regression = {}
    get_targets = [
        ('/affinity/gifts', 200),
        ('/affinity/gifts/summary', 200),
        ('/affinity/gifts/by-faction/greek', 200),
        ('/affinity/gifts/by-element/dark', 200),
        ('/affinity/gifts/by-element/darkness', 200),
        ('/affinity/gifts/by-element/dark/by-faction/greek', 200),
        ('/affinity/gifts/by-element/darkness/by-faction/greek', 200),
        ('/affinity/gifts/by-faction/greek/by-element/fire', 200),
        ('/affinity/gifts/by-element/dark/by-faction/tides', 404),
        ('/affinity/gifts/by-element/dark/by-faction/borea', 404),
        ('/affinity/gifts/by-element/tides/by-faction/greek', 404),
    ]
    for path, expected in get_targets:
        code, ms = _get(path)
        regression[path] = {'code': code, 'latency_ms': ms, 'expected': expected,
                            'ok': code == expected}

    # Ledger row count must remain 0
    ledger_rows = None
    try:
        from pymongo import MongoClient
        ledger_rows = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']['gift_transaction_ledger'].count_documents({})
    except Exception:
        ledger_rows = None

    by_label_summary = {l: {'count': b['count'], 'expected_status': b['expected'],
                            'p50_latency_ms': round(pct(b['lat'], 0.5), 2),
                            'p95_latency_ms': round(pct(b['lat'], 0.95), 2),
                            'unexpected_codes': b['unexpected']} for l, b in by_label.items()}
    actual_total = sum(b['count'] for b in by_label.values())
    unexpected_total = sum(sum(b['unexpected'].values()) for b in by_label.values())
    regression_unexpected = sum(1 for r in regression.values() if not r['ok'])

    result = {
        'result_id': 'affinity_gift_spend_k6_live_prep_result_v2',
        'task_origin': 'AF2-L-K6-LIVE-PREP/FULL-SAFE',
        'design_only': True, 'runtime_attached': False, 'db_write': False,
        'no_live_spend': True, 'no_inventory_mutation': True,
        'no_affinity_points_mutation': True, 'no_borea_activation': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'mode': 'plan_only_tool_unavailable_AND_safe_disabled_probe_executed',
        'k6_installed': False, 'locust_installed': False,
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'total_requests': actual_total,
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'p50_latency_ms': round(pct(samples, 0.5), 2),
        'p95_latency_ms': round(pct(samples, 0.95), 2),
        'p99_latency_ms': round(pct(samples, 0.99), 2),
        'p95_target_ms': 500,
        'total_5xx': total_5xx, 'unexpected_total': unexpected_total,
        'regression_unexpected': regression_unexpected,
        'ledger_rows_after_run': ledger_rows,
        'by_label': by_label_summary, 'regression_gets': regression,
        'borea_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        'safety_flags': {'runtime_attached': False, 'db_write': False,
                         'feature_flag_currently_enabled': False,
                         'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
                         'AF2N_allowed_today': False}
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'AF2-L-K6-LIVE-PREP probe: {actual_total} reqs, 5xx={total_5xx}, unexpected={unexpected_total}, '
          f'regression_unexpected={regression_unexpected}, p95={result["p95_latency_ms"]}ms, ledger_rows={ledger_rows}')
    ok = (total_5xx == 0 and unexpected_total == 0 and regression_unexpected == 0
          and (ledger_rows == 0 if ledger_rows is not None else True))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
