#!/usr/bin/env python3
"""V23 — Probe Redis live + record metrics."""
from __future__ import annotations
import json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_v23_redis_live_probe_result_v1.json')


def main():
    now = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    redis_url = os.environ.get('REDIS_URL', '')
    result = {
        'result_id': 'af2n_v23_redis_live_probe_result_v1',
        'task_origin': 'V23-REDIS-LIVE-PROBE',
        'started_at_utc': now,
        'redis_url_set': bool(redis_url),
    }
    if not redis_url:
        result['overall_status'] = 'READY_NOT_APPLIED'
        result['reason'] = 'REDIS_URL not set'
        OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(result, indent=2))
        print('REDIS-LIVE-PROBE READY_NOT_APPLIED'); return 0
    try:
        import redis  # type: ignore
    except ImportError as e:
        result['overall_status'] = 'READY_NOT_APPLIED'
        result['reason'] = f'redis pkg missing: {e}'
        OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(result, indent=2))
        print('REDIS-LIVE-PROBE READY_NOT_APPLIED'); return 0
    try:
        c = redis.Redis.from_url(redis_url, socket_timeout=1.0, socket_connect_timeout=1.0)
        t0 = time.time()
        pong = c.ping()
        ping_ms = (time.time() - t0) * 1000
        info = c.info('server')
        version = info.get('redis_version','?')
        # ephemeral sliding window probe
        pk = f'af2:probe:v23:live:{int(time.time())}'
        latencies = []
        for i in range(16):
            tt = time.time()
            pipe = c.pipeline()
            now_ms = int(time.time()*1000)
            pipe.zadd(pk, {f'{now_ms}_{i}': now_ms})
            pipe.zremrangebyscore(pk, 0, now_ms - 10000)
            pipe.zcard(pk)
            pipe.expire(pk, 12)
            res = pipe.execute()
            latencies.append((time.time()-tt)*1000)
        card = int(res[2])
        c.delete(pk)
        latencies.sort()
        p50 = latencies[len(latencies)//2]
        p95 = latencies[int(len(latencies)*0.95)] if latencies else 0
        # count existing af2:ratelimit keys
        n_keys = 0
        try:
            n_keys = sum(1 for _ in c.scan_iter('af2:ratelimit:*', count=200))
        except Exception: pass
        result.update({
            'overall_status': 'PASS' if (pong and card == 16) else 'FAIL',
            'ping_ok': bool(pong), 'ping_ms_first': ping_ms,
            'redis_server_version': version,
            'pipeline_probe_zcard_after_16_inserts': card,
            'pipeline_p50_ms': p50, 'pipeline_p95_ms': p95,
            'rate_limit_keys_count': n_keys,
            'finished_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        })
    except Exception as e:
        result['overall_status'] = 'FAIL'
        result['reason'] = f'redis probe error: {e}'
        result['finished_at_utc'] = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(result, indent=2))
    print(f'REDIS-LIVE-PROBE {result["overall_status"]}')
    return 0 if result['overall_status'] in ('PASS','READY_NOT_APPLIED') else 2


if __name__ == '__main__':
    sys.exit(main())
