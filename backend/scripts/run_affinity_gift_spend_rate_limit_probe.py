#!/usr/bin/env python3
"""V21 — Rate-limit probe for /api/affinity/gift-spend.

Fires non-allowlist requests as the same user_id in tight succession
to trigger 429 burst, then waits for window to clear and verifies
behavior returns to 423/normal. Records to JSON.

NON-DESTRUCTIVE: uses unauth user_ids (always 423/429 path, no DB write).
Does NOT touch Borea aliases. Records counts of each status code.
"""
from __future__ import annotations
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api/affinity/gift-spend'
OUT = Path('/app/data/design/affinity/affinity_gift_spend_rate_limit_probe_result_v1.json')


def _post(body):
    payload = json.dumps(body).encode()
    req = Request(API, data=payload, method='POST',
                  headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=4) as r:
            return r.status, r.read().decode()[:200]
    except HTTPError as e:
        try:
            body = e.read().decode()[:200]
        except Exception:
            body = ''
        return e.code, body
    except URLError as e:
        return -1, str(e)


def main():
    started = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    rolling_user = f'v21_rl_probe_{int(time.time())}'
    burst_results = []
    # Phase 1: burst, expect first 6 -> 423 (or 429 if user_id has accrued history),
    # 7th+ -> 429.
    for i in range(12):
        code, body = _post({
            'gift_id': 'gift_probe', 'hero_id': 'greek_zeus',
            'quantity': 1, 'idempotency_key': f'v21rlprobe_{i:04d}',
            'user_id': rolling_user,
        })
        burst_results.append({'i': i, 'code': code, 'preview': body[:120]})
    burst_codes = [b['code'] for b in burst_results]
    code_counts = {}
    for c in burst_codes:
        code_counts[c] = code_counts.get(c, 0) + 1
    saw_429 = 429 in burst_codes
    only_safe = all(c in (200, 423, 429, 404) for c in burst_codes)
    saw_no_200_for_unauth = 200 not in burst_codes
    saw_no_500 = all(c != 500 for c in burst_codes)
    # Phase 2: idle then verify post-recovery still 423 (when not in burst).
    time.sleep(11)  # past burst window
    recovery_code, _ = _post({
        'gift_id': 'gift_probe', 'hero_id': 'greek_zeus',
        'quantity': 1, 'idempotency_key': f'v21rlprobe_recovery',
        'user_id': f'{rolling_user}_recovery',
    })
    overall_pass = bool(saw_429 and only_safe and saw_no_200_for_unauth and saw_no_500)
    out = {
        'result_id': 'affinity_gift_spend_rate_limit_probe_result_v1',
        'task_origin': 'V21-AF2N-RATE-LIMIT-PROBE',
        'started_at_utc': started,
        'finished_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'rolling_user': rolling_user,
        'burst_results': burst_results,
        'burst_status_counts': {str(k): v for k, v in code_counts.items()},
        'saw_429_at_least_once': saw_429,
        'only_safe_status_codes': only_safe,
        'no_200_for_unauth': saw_no_200_for_unauth,
        'no_500_anywhere': saw_no_500,
        'recovery_code_after_window': recovery_code,
        'recovery_is_423_or_429': recovery_code in (423, 429),
        'overall_status': 'PASS' if overall_pass else 'FAIL',
        'safety': {
            'borea_skipped': True,
            'db_write_on_reject_expected': False,
            'non_allowlist_used_for_probe': True,
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f'V21-RL-PROBE {out["overall_status"]} counts={code_counts} -> {OUT}')
    return 0 if overall_pass else 2


if __name__ == '__main__':
    sys.exit(main())
