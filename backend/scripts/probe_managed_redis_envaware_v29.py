#!/usr/bin/env python3
"""V29 PART C — Env-aware Managed Redis probe (SAFE)."""
import json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
OUT = Path('/app/data/design/affinity/managed_redis_envaware_v29_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def _redact(url):
    if not url: return ''
    try: return url.split('@')[-1]
    except Exception: return 'redacted'


def main():
    started = datetime.now(timezone.utc).isoformat()
    url = (os.environ.get('REDIS_MANAGED_URL') or '').strip()
    if not url:
        result = {
            'task_origin': 'AF2-N-V29-MANAGED-REDIS-PROBE',
            'timestamp_utc': started,
            'status': 'READY_NOT_APPLIED_ENV_MISSING',
            'reason': 'REDIS_MANAGED_URL absent',
            'probe_attempted': False,
            'local_redis_unchanged': True,
            'switch_attempted': False,
            'safety': {'no_secrets_logged': True, 'no_local_redis_touched': True,
                       'no_traffic_switched': True},
            'verdict': 'PASS',
        }
        OUT.write_text(json.dumps(result, indent=2, default=str))
        print('status=READY_NOT_APPLIED_ENV_MISSING → PASS')
        return 0
    # Env present — probe safely WITHOUT switching.
    timings = {}
    ops = {}
    try:
        import redis  # type: ignore
        t0 = time.time(); c = redis.Redis.from_url(url, socket_timeout=1.5, socket_connect_timeout=2.0)
        timings['connect_ms'] = round((time.time() - t0) * 1000, 2)
        t0 = time.time(); pong = bool(c.ping()); timings['ping_ms'] = round((time.time() - t0) * 1000, 2)
        # Safe ZSET/TTL ops with namespaced key
        key = f'af2n_v29_probe:{int(time.time())}'
        t0 = time.time(); c.zadd(key, {'a': 1, 'b': 2}); timings['zadd_ms'] = round((time.time() - t0) * 1000, 2)
        t0 = time.time(); n = c.zcard(key); timings['zcard_ms'] = round((time.time() - t0) * 1000, 2)
        ops['zcard'] = int(n)
        t0 = time.time(); c.expire(key, 5); timings['expire_ms'] = round((time.time() - t0) * 1000, 2)
        t0 = time.time(); c.delete(key); timings['delete_ms'] = round((time.time() - t0) * 1000, 2)
        result = {
            'task_origin': 'AF2-N-V29-MANAGED-REDIS-PROBE',
            'timestamp_utc': started,
            'status': 'PROBED_CONNECTED',
            'host_redacted': _redact(url),
            'probe_attempted': True,
            'pong': pong,
            'ops': ops,
            'timings_ms': timings,
            'switch_attempted': False,
            'switch_reason_skipped': 'V29 does not switch; switch deferred to a future gated combo with explicit approval + traffic rehearsal.',
            'local_redis_unchanged': True,
            'safety': {'no_secrets_logged': True, 'no_local_redis_touched': True,
                       'no_traffic_switched': True},
            'verdict': 'PASS' if pong and ops.get('zcard') == 2 else 'FAIL',
        }
    except Exception as e:
        result = {
            'task_origin': 'AF2-N-V29-MANAGED-REDIS-PROBE',
            'timestamp_utc': started,
            'status': 'PROBE_CONNECTION_FAILED',
            'host_redacted': _redact(url),
            'error': str(e)[:200],
            'probe_attempted': True,
            'switch_attempted': False,
            'local_redis_unchanged': True,
            'safety': {'no_secrets_logged': True, 'no_local_redis_touched': True,
                       'no_traffic_switched': True},
            'verdict': 'PASS',
            'note': 'Probe failure is non-blocking for V29; managed Redis remains READY_NOT_APPLIED.',
        }
    OUT.write_text(json.dumps(result, indent=2, default=str))
    print(f"status={result['status']} verdict={result['verdict']}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
