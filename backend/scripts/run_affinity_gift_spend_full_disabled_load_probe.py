#!/usr/bin/env python3
"""AF2-L-FULL — full disabled-endpoint load probe (300 reqs default).
No live spend. No DB writes. Records p50/p95/p99 and 5xx count."""
from __future__ import annotations
import argparse, json, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
RESULT = Path('/app/data/design/affinity/affinity_gift_spend_full_disabled_load_result_v1.json')

def _http(method, path, body=None):
    payload = None; headers = {}
    if body is not None:
        payload = json.dumps(body).encode('utf-8'); headers = {'Content-Type': 'application/json'}
    t0 = time.monotonic()
    req = Request(API + path, data=payload, method=method, headers=headers)
    try:
        with urlopen(req, timeout=6) as r: r.read(); code = r.status
    except HTTPError as e:
        try: e.read()
        except: pass
        code = e.code
    except URLError:
        code = -1
    return code, (time.monotonic() - t0) * 1000.0

def pct(s, q):
    if not s: return 0.0
    s = sorted(s)
    k = max(0, min(len(s) - 1, int(round(q * (len(s) - 1)))))
    return s[k]

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--total', type=int, default=300)
    args = ap.parse_args(argv)
    total = max(120, min(1000, args.total))

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
            code, ms = _http('POST', '/affinity/gift-spend', body)
            samples.append(ms); by_label[label]['count'] += 1; by_label[label]['lat'].append(ms)
            if code != exp:
                by_label[label]['unexpected'][str(code)] = by_label[label]['unexpected'].get(str(code), 0) + 1
            if isinstance(code, int) and 500 <= code < 600: total_5xx += 1

    regression = {}
    for path in ('/affinity/gifts','/affinity/gifts/summary',
                 '/affinity/gifts/by-faction/greek','/affinity/gifts/by-element/dark',
                 '/affinity/gifts/by-element/darkness'):
        code, ms = _http('GET', path); regression[path] = {'code': code, 'latency_ms': ms}

    by_label_summary = {l: {'count': b['count'], 'expected_status': b['expected'],
                            'p50_latency_ms': round(pct(b['lat'], 0.5), 2),
                            'p95_latency_ms': round(pct(b['lat'], 0.95), 2),
                            'unexpected_codes': b['unexpected']} for l, b in by_label.items()}
    actual_total = sum(b['count'] for b in by_label.values())
    unexpected_total = sum(sum(b['unexpected'].values()) for b in by_label.values())

    result = {
        'probe_id': 'AF2-L-FULL-PROBE-001',
        'task_origin': 'AF2-L-FULL',
        'design_only': True, 'runtime_attached': False, 'db_write': False,
        'no_live_spend': True, 'no_inventory_mutation': True,
        'no_affinity_points_mutation': True, 'no_borea_activation': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'total_requests': actual_total,
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'p50_latency_ms': round(pct(samples, 0.5), 2),
        'p95_latency_ms': round(pct(samples, 0.95), 2),
        'p99_latency_ms': round(pct(samples, 0.99), 2),
        'p95_target_ms': 500,
        'total_5xx': total_5xx, 'unexpected_total': unexpected_total,
        'by_label': by_label_summary, 'regression_gets': regression,
        'borea_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        'safety_flags': {'runtime_attached': False, 'db_write': False,
                         'feature_flag_currently_enabled': False,
                         'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia']}
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'AF2-L-FULL probe: {actual_total} reqs, 5xx={total_5xx}, unexpected={unexpected_total}, p95={result["p95_latency_ms"]}ms')
    return 0 if (total_5xx == 0 and unexpected_total == 0) else 1

if __name__ == '__main__':
    sys.exit(main())
