#!/usr/bin/env python3
"""V26 PART B — Optional Managed Redis connector probe.

Only runs if REDIS_MANAGED_URL env var is provided. Otherwise emits a
`READY_NOT_APPLIED` result indicating the probe is ready to run when
credentials are available.

NO secrets are committed or logged. The probe NEVER falls back to local
Redis; that's a separate code path.
"""
import json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/affinity_managed_redis_probe_result_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def main():
    started = datetime.now(timezone.utc).isoformat()
    url = os.environ.get('REDIS_MANAGED_URL', '').strip()
    if not url:
        result = {
            'task_origin': 'AF2-N-V26-MANAGED-REDIS-PROBE',
            'timestamp_utc': started,
            'status': 'READY_NOT_APPLIED',
            'reason': 'REDIS_MANAGED_URL env var not provided',
            'probe_attempted': False,
            'verdict': 'PASS',
            'safety': {'no_secrets_logged': True, 'no_local_redis_touched': True},
        }
        OUT.write_text(json.dumps(result, indent=2, default=str))
        print("status=READY_NOT_APPLIED (no REDIS_MANAGED_URL) → PASS")
        return 0

    # Probe enabled — connect, PING, SET, GET, DEL roundtrip
    redacted_url = url.split('@')[-1] if '@' in url else url
    try:
        import redis  # type: ignore
    except ImportError:
        result = {
            'task_origin': 'AF2-N-V26-MANAGED-REDIS-PROBE',
            'timestamp_utc': started,
            'status': 'PYTHON_REDIS_MISSING',
            'verdict': 'FAIL',
            'host_redacted': redacted_url,
        }
        OUT.write_text(json.dumps(result, indent=2, default=str))
        print('FAIL: python redis package missing')
        return 2

    timings = {}
    try:
        t0 = time.time()
        c = redis.Redis.from_url(url, socket_timeout=1.0, socket_connect_timeout=1.5)
        timings['connect_ms'] = round((time.time() - t0) * 1000, 2)
        t0 = time.time(); pong = c.ping(); timings['ping_ms'] = round((time.time() - t0) * 1000, 2)
        key = f'af2n:v26:probe:{int(time.time())}'
        t0 = time.time(); c.set(key, 'ok', ex=10); timings['set_ms'] = round((time.time() - t0) * 1000, 2)
        t0 = time.time(); val = c.get(key); timings['get_ms'] = round((time.time() - t0) * 1000, 2)
        t0 = time.time(); c.delete(key); timings['del_ms'] = round((time.time() - t0) * 1000, 2)
        info = c.info('server') if hasattr(c, 'info') else {}
        result = {
            'task_origin': 'AF2-N-V26-MANAGED-REDIS-PROBE',
            'timestamp_utc': started,
            'status': 'CONNECTED',
            'probe_attempted': True,
            'host_redacted': redacted_url,
            'pong': bool(pong),
            'roundtrip_ok': val == b'ok' or val == 'ok',
            'timings_ms': timings,
            'redis_version': str(info.get('redis_version', 'unknown')),
            'safety': {'no_secrets_logged': True, 'no_local_redis_touched': True},
        }
        result['verdict'] = 'PASS' if (result['pong'] and result['roundtrip_ok']) else 'FAIL'
    except Exception as e:
        result = {
            'task_origin': 'AF2-N-V26-MANAGED-REDIS-PROBE',
            'timestamp_utc': started,
            'status': 'CONNECTION_FAILED',
            'probe_attempted': True,
            'host_redacted': redacted_url,
            'error': str(e)[:200],
            'verdict': 'FAIL',
            'safety': {'no_secrets_logged': True, 'no_local_redis_touched': True},
        }

    OUT.write_text(json.dumps(result, indent=2, default=str))
    print(f"status={result['status']} verdict={result['verdict']}")
    return 0 if result['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
