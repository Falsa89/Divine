#!/usr/bin/env python3
"""V22 — Probe Redis rate-limit backend (read-only).

Non-destructive. Writes only ephemeral keys with TTL <=15s under prefix
`af2:ratelimit:probe:v22:*`. If Redis unavailable, records and returns 0
(PASS_BLOCKED_NO_REDIS).
"""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/affinity_rate_limit_redis_probe_result_v1.json')


def main():
    now = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    redis_url = os.environ.get('REDIS_URL', '')
    result = {
        'result_id': 'affinity_rate_limit_redis_probe_result_v1',
        'task_origin': 'V22-REDIS-RATE-LIMIT-PROBE',
        'started_at_utc': now,
        'redis_url_set': bool(redis_url),
    }
    try:
        import redis  # type: ignore
        result['py_redis_pkg_present'] = True
        result['py_redis_version'] = redis.__version__
    except Exception as e:
        result['py_redis_pkg_present'] = False
        result['py_redis_pkg_import_error'] = str(e)
    if not redis_url:
        result['overall_status'] = 'READY_NOT_APPLIED'
        result['reason'] = 'REDIS_URL not set; cannot probe Redis'
        result['finished_at_utc'] = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
        OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(result, indent=2))
        print('REDIS-PROBE READY_NOT_APPLIED: REDIS_URL not set'); return 0
    try:
        c = redis.Redis.from_url(redis_url, socket_timeout=1.0, socket_connect_timeout=1.0)
        pong = c.ping()
        result['ping_ok'] = bool(pong)
        if not pong:
            result['overall_status'] = 'READY_NOT_APPLIED'
            result['reason'] = 'Redis ping did not return PONG'
            OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(result, indent=2))
            print('REDIS-PROBE READY_NOT_APPLIED: no pong'); return 0
        # ephemeral sliding window probe
        import time
        probe_user = f'probe_user_{int(time.time())}'
        probe_key = f'af2:ratelimit:probe:v22:{probe_user}'
        try:
            for i in range(8):
                pipe = c.pipeline()
                now_ms = int(time.time() * 1000)
                pipe.zadd(probe_key, {f'{now_ms}_{i}': now_ms})
                pipe.zremrangebyscore(probe_key, 0, now_ms - 10000)
                pipe.zcard(probe_key)
                pipe.expire(probe_key, 12)
                res = pipe.execute()
            card = int(res[2])
            result['probe_zcard_after_8_inserts'] = card
            result['probe_ok'] = card == 8
            # cleanup
            c.delete(probe_key)
            result['overall_status'] = 'PASS' if result['probe_ok'] else 'FAIL'
        except Exception as e:
            result['probe_error'] = str(e)
            result['overall_status'] = 'FAIL'
    except Exception as e:
        result['overall_status'] = 'READY_NOT_APPLIED'
        result['reason'] = f'redis init/ping failure: {e}'
    result['finished_at_utc'] = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(result, indent=2))
    print(f'REDIS-PROBE {result["overall_status"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
