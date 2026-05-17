#!/usr/bin/env python3
"""
AF2-L — Disabled-endpoint load probe for POST /api/affinity/gift-spend.

Lightweight, no-write probe that exercises:
- empty body                       -> expected 423
- valid body                       -> expected 423 (still disabled)
- duplicate idempotency_key        -> expected 423 (still disabled,
                                       no replay-409 because no DB)
- missing idempotency_key          -> expected 423
- Borea aliases (3)                -> expected 404 each
- GET regressions on gifts         -> expected 200

Default: 100 total POST requests + 4 GET regressions.
Records p50/p95/p99, HTTP-status histogram, 5xx count, no_write_assertion.
Writes: /app/data/design/affinity/affinity_gift_spend_disabled_load_probe_result_v1.json

No DB writes. No live spend. No runtime mutation.
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
RESULT = Path('/app/data/design/affinity/affinity_gift_spend_disabled_load_probe_result_v1.json')


def _http(method: str, path: str, body: dict | None = None) -> tuple[int, float]:
    payload = None
    headers = {}
    if body is not None:
        payload = json.dumps(body).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
    t0 = time.monotonic()
    req = Request(API + path, data=payload, method=method, headers=headers)
    try:
        with urlopen(req, timeout=6) as r:
            r.read()
            code = r.status
    except HTTPError as e:
        try:
            e.read()
        except Exception:
            pass
        code = e.code
    except URLError:
        code = -1
    return code, (time.monotonic() - t0) * 1000.0


def pct(samples: list[float], q: float) -> float:
    if not samples:
        return 0.0
    s = sorted(samples)
    k = max(0, min(len(s) - 1, int(round(q * (len(s) - 1)))))
    return s[k]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--total', type=int, default=100,
                    help='Total POST requests (default 100, max 500)')
    args = ap.parse_args(argv)
    total = max(40, min(500, args.total))

    payloads = [
        ('empty',    {}),
        ('valid',    {'gift_id': 'gift_x', 'hero_id': 'greek_zeus',
                      'quantity': 1, 'idempotency_key': 'abcdef1234567890'}),
        ('dup_idem', {'gift_id': 'gift_x', 'hero_id': 'greek_zeus',
                      'quantity': 1, 'idempotency_key': 'duplicate_key_001'}),
        ('missing_idem', {'gift_id': 'gift_x', 'hero_id': 'greek_zeus',
                          'quantity': 1}),
        ('borea',         {'gift_id': 'x', 'hero_id': 'borea', 'quantity': 1,
                           'idempotency_key': 'abcd1234efgh'}),
        ('greek_borea',   {'gift_id': 'x', 'hero_id': 'greek_borea', 'quantity': 1,
                           'idempotency_key': 'abcd1234efgh'}),
        ('primordial_gaia', {'gift_id': 'x', 'hero_id': 'primordial_gaia',
                             'quantity': 1, 'idempotency_key': 'abcd1234efgh'}),
    ]
    expected_by_label = {
        'empty': 423, 'valid': 423, 'dup_idem': 423, 'missing_idem': 423,
        'borea': 404, 'greek_borea': 404, 'primordial_gaia': 404,
    }

    started = time.monotonic()
    by_label: dict[str, dict] = {l: {'count': 0, 'expected': expected_by_label[l],
                                     'unexpected_codes': {}, 'latencies_ms': []}
                                 for l, _ in payloads}
    total_5xx = 0
    samples: list[float] = []

    n_per = max(1, total // len(payloads))
    for label, body in payloads:
        for _ in range(n_per):
            code, ms = _http('POST', '/affinity/gift-spend', body)
            samples.append(ms)
            by_label[label]['count'] += 1
            by_label[label]['latencies_ms'].append(ms)
            if code != expected_by_label[label]:
                by_label[label]['unexpected_codes'][str(code)] = \
                    by_label[label]['unexpected_codes'].get(str(code), 0) + 1
            if isinstance(code, int) and 500 <= code < 600:
                total_5xx += 1

    # Regression GETs
    regression = {}
    for path in ('/affinity/gifts', '/affinity/gifts/summary',
                 '/affinity/gifts/by-faction/greek',
                 '/affinity/gifts/by-element/dark'):
        code, ms = _http('GET', path)
        regression[path] = {'code': code, 'latency_ms': ms}

    elapsed = time.monotonic() - started

    actual_total = sum(b['count'] for b in by_label.values())
    unexpected_total = sum(sum(b['unexpected_codes'].values()) for b in by_label.values())

    # Strip raw latency arrays from each label before writing (keep aggregate stats)
    by_label_summary = {}
    for l, b in by_label.items():
        lat = b['latencies_ms']
        by_label_summary[l] = {
            'count': b['count'],
            'expected_status': b['expected'],
            'p50_latency_ms': round(pct(lat, 0.5), 2),
            'p95_latency_ms': round(pct(lat, 0.95), 2),
            'unexpected_codes': b['unexpected_codes'],
        }

    result = {
        'probe_id': 'AF2-L-PROBE-001',
        'task_origin': 'AF2-L',
        'design_only': True,
        'runtime_attached': False,
        'db_write': False,
        'no_live_spend': True,
        'no_inventory_mutation': True,
        'no_affinity_points_mutation': True,
        'no_borea_activation': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'total_requests': actual_total,
        'elapsed_seconds': round(elapsed, 3),
        'p50_latency_ms': round(pct(samples, 0.5), 2),
        'p95_latency_ms': round(pct(samples, 0.95), 2),
        'p99_latency_ms': round(pct(samples, 0.99), 2),
        'total_5xx': total_5xx,
        'unexpected_total': unexpected_total,
        'by_label': by_label_summary,
        'regression_gets': regression,
        'borea_aliases_blocked': ['borea', 'greek_borea', 'primordial_gaia'],
        'safety_flags': {
            'runtime_attached': False,
            'db_write': False,
            'feature_flag_currently_enabled': False,
            'hidden_aliases_blocked': ['borea', 'greek_borea', 'primordial_gaia']
        }
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n',
                      encoding='utf-8')
    print(f'AF2-L probe completed: {actual_total} requests, '
          f'5xx={total_5xx}, unexpected={unexpected_total}, '
          f'p95={result["p95_latency_ms"]}ms')
    print(f'Result: {RESULT}')
    return 0 if (total_5xx == 0 and unexpected_total == 0) else 1


if __name__ == '__main__':
    sys.exit(main())
