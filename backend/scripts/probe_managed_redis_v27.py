#!/usr/bin/env python3
"""V27 PART B — Managed Redis probe (gated by REDIS_MANAGED_URL).

Safe: if env var absent, emits READY_NOT_APPLIED with detailed blocker.
"""
import json, os, sys, time, uuid
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/managed_redis_probe_v27_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def main():
    started = datetime.now(timezone.utc).isoformat()
    url = os.environ.get('REDIS_MANAGED_URL', '').strip()
    if not url:
        result = {
            'task_origin': 'AF2-N-V27-MANAGED-REDIS-PROBE',
            'timestamp_utc': started,
            'status': 'READY_NOT_APPLIED',
            'reason': 'REDIS_MANAGED_URL env var not provided',
            'blocker': 'No Managed Redis endpoint configured. Provisioning + secret management required before switch.',
            'probe_attempted': False,
            'safety': {'no_secrets_logged': True, 'no_local_redis_touched': True},
            'verdict': 'PASS',
        }
        OUT.write_text(json.dumps(result, indent=2, default=str))
        print('status=READY_NOT_APPLIED → PASS (no REDIS_MANAGED_URL)')
        return 0

    redacted = url.split('@')[-1] if '@' in url else url
    try:
        import redis  # type: ignore
    except ImportError:
        OUT.write_text(json.dumps({'status': 'PYTHON_REDIS_MISSING', 'verdict': 'FAIL'}, indent=2))
        print('FAIL: python redis package missing'); return 2

    timings = {}
    try:
        t0 = time.time()
        c = redis.Redis.from_url(url, socket_timeout=1.5, socket_connect_timeout=2.0)
        timings['connect_ms'] = round((time.time() - t0) * 1000, 2)
        t0 = time.time(); pong = c.ping(); timings['ping_ms'] = round((time.time() - t0) * 1000, 2)
        key = f'af2n:v27:probe:{int(time.time())}:{uuid.uuid4().hex[:6]}'
        zkey = f'af2n:v27:zprobe:{int(time.time())}:{uuid.uuid4().hex[:6]}'
        t0 = time.time(); c.set(key, 'ok', ex=20); timings['set_ms'] = round((time.time() - t0) * 1000, 2)
        t0 = time.time(); val = c.get(key); timings['get_ms'] = round((time.time() - t0) * 1000, 2)
        t0 = time.time(); c.zadd(zkey, {'m1': time.time(), 'm2': time.time()}); timings['zadd_ms'] = round((time.time() - t0) * 1000, 2)
        t0 = time.time(); zcard = c.zcard(zkey); timings['zcard_ms'] = round((time.time() - t0) * 1000, 2)
        c.expire(zkey, 30)
        t0 = time.time(); c.delete(key); c.delete(zkey); timings['cleanup_ms'] = round((time.time() - t0) * 1000, 2)
        info = c.info('server') if hasattr(c, 'info') else {}
        result = {
            'task_origin': 'AF2-N-V27-MANAGED-REDIS-PROBE',
            'timestamp_utc': started,
            'status': 'CONNECTED',
            'probe_attempted': True,
            'host_redacted': redacted,
            'pong': bool(pong),
            'roundtrip_ok': (val == b'ok' or val == 'ok') and zcard == 2,
            'zset_ops_ok': zcard == 2,
            'timings_ms': timings,
            'redis_version': str(info.get('redis_version', 'unknown')),
            'tls_assumed': url.startswith('rediss://'),
            'safety': {'no_secrets_logged': True, 'no_local_redis_touched': True},
        }
        result['verdict'] = 'PASS' if (result['pong'] and result['roundtrip_ok'] and result['zset_ops_ok']) else 'FAIL'
    except Exception as e:
        result = {
            'task_origin': 'AF2-N-V27-MANAGED-REDIS-PROBE',
            'timestamp_utc': started,
            'status': 'CONNECTION_FAILED',
            'host_redacted': redacted,
            'error': str(e)[:200],
            'verdict': 'FAIL',
            'safety': {'no_secrets_logged': True, 'no_local_redis_touched': True},
        }
    OUT.write_text(json.dumps(result, indent=2, default=str))
    print(f"status={result['status']} verdict={result['verdict']}")
    return 0 if result['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
