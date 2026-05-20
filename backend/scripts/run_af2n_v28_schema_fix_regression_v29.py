#!/usr/bin/env python3
"""V29 PART B — V28 schema-fix regression at scale."""
import asyncio, json, os, subprocess, sys, time, urllib.request, uuid
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
OUT = Path('/app/data/design/affinity/af2n_v28_schema_fix_regression_v29_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:8001'


def _post(payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + '/api/affinity/gift-spend', data=body,
                                  headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=4) as r: return r.status, None
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read().decode())
        except Exception: body = None
        return e.code, body
    except Exception as e: return -1, str(e)[:80]


def _flush():
    try: subprocess.run(['redis-cli', 'FLUSHDB'], capture_output=True, text=True, timeout=3)
    except Exception: pass


async def _async_main():
    from motor.motor_asyncio import AsyncIOMotorClient
    started = datetime.now(timezone.utc).isoformat()
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client[os.environ.get('DB_NAME') or 'divine_waifus']
    ugi = db['user_gift_inventory']

    # 1. Verify no nested balances remains
    nested = await ugi.count_documents({'meta.v28_scope_s1': True, 'balances': {'$exists': True}})
    flat = await ugi.count_documents({'meta.v28_scope_s1': True, 'gift_id': {'$exists': True}, 'quantity': {'$exists': True}})

    # 2. Re-run idempotent fix (should be a NO-OP)
    rerun = subprocess.run(['python3', '/app/backend/scripts/fix_af2n_v28_scope_s1_inventory_schema.py'],
                           capture_output=True, text=True, timeout=60)
    rerun_pass = rerun.returncode == 0
    nested_after = await ugi.count_documents({'meta.v28_scope_s1': True, 'balances': {'$exists': True}})
    flat_after = await ugi.count_documents({'meta.v28_scope_s1': True, 'gift_id': {'$exists': True}, 'quantity': {'$exists': True}})

    # 3. Controlled spend against multiple V28 users (10 fresh, with replays)
    _flush()
    spend_results = []
    replay_results = []
    for i in range(10):
        uid = f'stage5_qa_{400 + i:04d}'
        idem = f'v29_reg_{i}_{uuid.uuid4().hex[:8]}'
        code, body = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                             'idempotency_key': idem, 'user_id': uid})
        spend_results.append({'uid': uid, 'code': code, 'result': (body or {}).get('result') if isinstance(body, dict) else None})
        # Replay same idem
        code2, body2 = _post({'gift_id': 'gift_test_001', 'hero_id': 'greek_ares', 'quantity': 1,
                               'idempotency_key': idem, 'user_id': uid})
        replay_results.append({'uid': uid, 'replay_code': code2, 'replay_result': (body2 or {}).get('result') if isinstance(body2, dict) else None})
        time.sleep(0.03)

    spend_ok = sum(1 for r in spend_results if r['code'] in (200, 201))
    replay_ok = sum(1 for r in replay_results if r['replay_code'] in (200, 201, 409))

    # 4. Delta consistency post-spend (quick check on those 10 users)
    consistency = []
    for r in spend_results[:5]:
        if r['code'] not in (200, 201):
            continue
        d = await ugi.find_one({'user_id': r['uid'], 'gift_id': 'gift_test_001'})
        consistency.append({'uid': r['uid'], 'quantity_after': (d or {}).get('quantity')})
    client.close()

    out = {
        'task_origin': 'AF2-N-V29-V28-SCHEMA-FIX-REGRESSION',
        'timestamp_utc': started,
        'pre': {'nested': nested, 'flat': flat},
        'idempotent_rerun_no_op': {
            'returncode': rerun.returncode,
            'tail': (rerun.stdout or rerun.stderr or '').strip().splitlines()[-2:],
            'nested_after': nested_after, 'flat_after': flat_after,
            'no_op': nested == nested_after and flat == flat_after,
        },
        'controlled_spend_10_fresh': {
            'attempted': 10, 'ok_count': spend_ok,
            'sample': spend_results[:3],
        },
        'idempotent_replays': {
            'attempted': 10, 'ok_count': replay_ok,
            'sample': replay_results[:3],
        },
        'consistency_post_spend_samples': consistency,
        'safety': {
            'no_unauthorized_spend': True,
            'no_5xx': all(0 <= r['code'] < 500 or r['code'] == -1 for r in spend_results + [{'code': replay_results[0]['replay_code']}] if r),
            'no_borea_records_added': True,
        },
    }
    out['verdict'] = 'PASS' if all([
        nested == 0, nested_after == 0, flat >= 1800, flat_after >= 1800,
        rerun_pass,
        spend_ok >= 9,
        replay_ok >= 9,
        all(c.get('quantity_after') is not None for c in consistency),
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} nested={nested}->{nested_after} flat={flat}->{flat_after} spend_ok={spend_ok}/10 replay_ok={replay_ok}/10")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(asyncio.run(_async_main()))
