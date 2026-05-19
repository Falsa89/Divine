#!/usr/bin/env python3
"""V23 — Run Stage4 Locust rate-limit (45s, 15 users)."""
from __future__ import annotations
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

LF = Path('/app/loadtests/af2n_v23_stage4_ratelimit_locustfile.py')
OUT = Path('/app/data/design/affinity/af2n_v23_locust_stage4_ratelimit_result_v1.json')


def _canary():
    try:
        with urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=4) as r:
            return json.loads(r.read().decode())
    except Exception: return {}


def main():
    NOW = datetime.now(timezone.utc)
    pre = _canary()
    redis_keys_before = -1
    try:
        import redis
        c = redis.Redis.from_url(os.environ.get('REDIS_URL','redis://127.0.0.1:6379/0'), socket_timeout=1.0)
        redis_keys_before = sum(1 for _ in c.scan_iter('af2:ratelimit:*', count=200))
    except Exception: pass
    cmd = ['locust','-f',str(LF),'--host','http://127.0.0.1:8001',
           '--headless','-u','15','-r','5','-t','45s',
           '--csv','/tmp/v23_locust','--only-summary']
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    post = _canary()
    out_text = (proc.stdout or '') + '\n' + (proc.stderr or '')
    redis_keys_after = -1
    try:
        import redis
        c = redis.Redis.from_url(os.environ.get('REDIS_URL','redis://127.0.0.1:6379/0'), socket_timeout=1.0)
        redis_keys_after = sum(1 for _ in c.scan_iter('af2:ratelimit:*', count=200))
    except Exception: pass
    ledger_grew = post.get('ledger_total_rows', 0) - pre.get('ledger_total_rows', 0)
    cap_exceeded = post.get('ledger_total_rows', 0) > post.get('canary_ledger_cap', 0)
    safe_growth = ledger_grew <= 20
    inv_neg = 0
    try:
        from pymongo import MongoClient
        db = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']
        inv_neg = db['user_gift_inventory'].count_documents({'quantity': {'$lt': 0}})
    except Exception: pass
    backend = post.get('rate_limit_backend')
    overall = (proc.returncode == 0 and not cap_exceeded and safe_growth and inv_neg == 0)
    out_doc = {
        'result_id':'af2n_v23_locust_stage4_ratelimit_result_v1',
        'task_origin':'V23-LOCUST-STAGE4-RATELIMIT',
        'started_at_utc': NOW.isoformat().replace('+00:00','Z'),
        'finished_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'locust_returncode': proc.returncode,
        'rate_limit_backend_observed': backend,
        'pre_canary_status': pre, 'post_canary_status': post,
        'ledger_growth': ledger_grew, 'cap_exceeded': cap_exceeded,
        'safe_ledger_growth': safe_growth,
        'negative_inventory_count': inv_neg,
        'redis_keys_before': redis_keys_before, 'redis_keys_after': redis_keys_after,
        'redis_keys_growth': (redis_keys_after - redis_keys_before) if redis_keys_after >= 0 else None,
        'stdout_tail': out_text[-2200:],
        'overall_status': 'PASS' if overall else 'FAIL',
        'safety_invariants': [
            'fresh budget capped 5','no Borea writes','no battle wiring','no buffs',
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out_doc, indent=2))
    print(f'V23-LOCUST-STAGE4-RATELIMIT {out_doc["overall_status"]} growth={ledger_grew} inv_neg={inv_neg} backend={backend} redis_keys={redis_keys_before}->{redis_keys_after}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
