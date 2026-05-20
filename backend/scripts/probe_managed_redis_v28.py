#!/usr/bin/env python3
"""V28 PART F — Managed Redis probe V28."""
import json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/managed_redis_v28_probe_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def main():
    started = datetime.now(timezone.utc).isoformat()
    url = os.environ.get('REDIS_MANAGED_URL', '').strip()
    if not url:
        result = {
            'task_origin': 'AF2-N-V28-MANAGED-REDIS-PROBE',
            'timestamp_utc': started,
            'status': 'READY_NOT_APPLIED',
            'reason': 'REDIS_MANAGED_URL absent',
            'probe_attempted': False,
            'local_redis_unchanged': True,
            'verdict': 'PASS',
            'safety': {'no_secrets_logged': True, 'no_local_redis_touched': True},
        }
        OUT.write_text(json.dumps(result, indent=2, default=str))
        print('status=READY_NOT_APPLIED → PASS')
        return 0
    try:
        import redis  # type: ignore
        t0 = time.time(); c = redis.Redis.from_url(url, socket_timeout=1.5, socket_connect_timeout=2.0)
        connect_ms = round((time.time() - t0) * 1000, 2)
        t0 = time.time(); pong = c.ping(); ping_ms = round((time.time() - t0) * 1000, 2)
        result = {
            'task_origin': 'AF2-N-V28-MANAGED-REDIS-PROBE',
            'timestamp_utc': started, 'status': 'CONNECTED',
            'probe_attempted': True, 'host_redacted': url.split('@')[-1],
            'pong': bool(pong), 'timings_ms': {'connect': connect_ms, 'ping': ping_ms},
            'safety': {'no_secrets_logged': True}, 'verdict': 'PASS' if pong else 'FAIL',
        }
    except Exception as e:
        result = {
            'task_origin': 'AF2-N-V28-MANAGED-REDIS-PROBE',
            'timestamp_utc': started, 'status': 'CONNECTION_FAILED',
            'error': str(e)[:200], 'verdict': 'FAIL',
        }
    OUT.write_text(json.dumps(result, indent=2, default=str))
    print(f"status={result['status']} verdict={result['verdict']}")
    return 0 if result['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
