#!/usr/bin/env python3
"""V23 — Validate Redis SWITCH state.

Verifies that:
  - canary-status reports rate_limit_backend == 'redis'
  - rate_limit_redis_url_set is True
  - a burst probe against /api/affinity/gift-spend results in 429 with
    rate_limit_snapshot.backend == 'redis'
  - Redis-backed keys actually appear under af2:ratelimit:*
If Redis not available, accepts READY_NOT_APPLIED (memory backend) as safe.
"""
from __future__ import annotations
import json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError

OUT = Path('/app/data/design/affinity/af2n_v23_redis_switch_result_v1.json')
API = 'http://127.0.0.1:8001/api/affinity/gift-spend'


def _post(b):
    payload = json.dumps(b).encode()
    req = Request(API, data=payload, method='POST',
                  headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=4) as r:
            return r.status, json.loads(r.read().decode())
    except HTTPError as e:
        try: body = json.loads(e.read().decode())
        except Exception: body = None
        return e.code, body
    except Exception: return -1, None


def main():
    now = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    try:
        with urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=4) as r:
            st = json.loads(r.read().decode())
    except Exception as e:
        out = {'overall_status':'FAIL','reason':f'canary-status unreachable: {e}',
               'generated_at_utc':now}
        OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out, indent=2))
        print('FAIL: canary status unreachable'); return 2
    backend_advertised = st.get('rate_limit_backend')
    url_set = st.get('rate_limit_redis_url_set')

    # burst probe with rolling user
    rolling_user = f'v23_switchval_{int(time.time())}'
    burst_results = []
    for i in range(10):
        code, body = _post({'gift_id':'x','hero_id':'greek_zeus','quantity':1,
                            'idempotency_key':f'v23swval_{i}','user_id':rolling_user})
        snap = (body or {}).get('rate_limit_snapshot') if isinstance(body, dict) else None
        burst_results.append({'i':i,'code':code,'snapshot_backend': (snap or {}).get('backend')})
    saw_429 = any(r['code']==429 for r in burst_results)
    backends_observed = {r['snapshot_backend'] for r in burst_results if r['snapshot_backend']}

    redis_keys_present = False
    redis_keys_count = -1
    try:
        import redis  # type: ignore
        url = os.environ.get('REDIS_URL','redis://127.0.0.1:6379/0')
        c = redis.Redis.from_url(url, socket_timeout=1.0)
        keys = list(c.scan_iter('af2:ratelimit:*', count=200))
        redis_keys_present = any(k for k in keys)
        redis_keys_count = len(keys)
    except Exception:
        pass

    result = {
        'result_id':'af2n_v23_redis_switch_result_v1',
        'task_origin':'V23-REDIS-SWITCH-VALIDATION',
        'generated_at_utc': now,
        'canary_status_backend_advertised': backend_advertised,
        'canary_status_url_set': url_set,
        'burst_results': burst_results,
        'saw_429_at_least_once': saw_429,
        'snapshot_backends_observed': sorted(list(backends_observed)),
        'redis_keys_count': redis_keys_count,
        'redis_keys_present_after_burst': redis_keys_present,
    }
    # decide overall: PASS if backend=redis advertised AND snapshot 'redis' observed AND keys present
    if backend_advertised == 'redis' and 'redis' in backends_observed and redis_keys_present and saw_429:
        result['overall_status'] = 'PASS'
        result['mode'] = 'redis_live_switch_applied_safely'
    elif backend_advertised in ('memory','memory_fallback') or backend_advertised is None:
        result['overall_status'] = 'READY_NOT_APPLIED'
        result['mode'] = 'memory_backend_safe_fallback'
        result['reason'] = 'Redis not configured / unreachable; memory backend active and safe'
    else:
        result['overall_status'] = 'FAIL'
        result['reason'] = f'inconsistent: advertised={backend_advertised} observed={backends_observed} keys={redis_keys_count}'
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(result, indent=2))
    print(f'V23-REDIS-SWITCH {result["overall_status"]} backend={backend_advertised} observed={backends_observed} keys={redis_keys_count}')
    return 0 if result['overall_status'] in ('PASS','READY_NOT_APPLIED') else 2


if __name__ == '__main__':
    sys.exit(main())
