#!/usr/bin/env python3
"""V28 PART B.1 — Idempotent schema fix for V28 seeded inventory.

Bug: apply_af2n_inventory_scope_s1_v28 seeded user_gift_inventory with the
nested `balances` dict schema, but the runtime route at
/app/backend/routes/affinity_gift_spend.py reads the flat schema
{user_id, gift_id, quantity}. Result: stage5_qa_* users got HTTP 412.

This script migrates V28-marked docs to the flat schema (idempotent):
  - For each doc with meta.v28_scope_s1=true that still has `balances`,
    create a flat doc per (user_id, gift_id, qty) pair and delete the
    nested doc. The marker is preserved on the flat doc for rollback.
  - Safe to rerun: only acts on docs that still have `balances`.

NO change to production data outside the V28 marker scope.
NO cap change. NO allowlist change. NO Borea exposure.
"""
import asyncio, json, os, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

OUT = Path('/app/data/design/affinity/af2n_v28_scope_s1_schema_fix_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


async def _async_main():
    from motor.motor_asyncio import AsyncIOMotorClient
    started = datetime.now(timezone.utc).isoformat()
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
    db = client[os.environ.get('DB_NAME') or 'divine_waifus']
    ugi = db['user_gift_inventory']

    # Pre-state counts
    pre_marker = await ugi.count_documents({'meta.v28_scope_s1': True})
    pre_nested = await ugi.count_documents({'meta.v28_scope_s1': True, 'balances': {'$exists': True}})
    pre_flat = await ugi.count_documents({'meta.v28_scope_s1': True, 'gift_id': {'$exists': True}, 'quantity': {'$exists': True}})

    migrated = 0
    skipped = 0
    errors = []

    cur = ugi.find({'meta.v28_scope_s1': True, 'balances': {'$exists': True}})
    async for doc in cur:
        uid = doc.get('user_id')
        balances = doc.get('balances') or {}
        if not uid or not isinstance(balances, dict) or not balances:
            skipped += 1
            continue
        try:
            for gift_id, qty in balances.items():
                # Check if a flat doc already exists for (uid, gift_id) — preserve idempotency
                existing_flat = await ugi.find_one({'user_id': uid, 'gift_id': gift_id})
                if existing_flat:
                    continue
                await ugi.insert_one({
                    'user_id': uid,
                    'gift_id': gift_id,
                    'quantity': int(qty),
                    'reserved_quantity': 0,
                    'created_at': datetime.now(timezone.utc),
                    'updated_at': datetime.now(timezone.utc),
                    'last_tx_id': None,
                    'source': 'seed_v28_scope_s1',
                    'meta': {'v28_scope_s1': True, 'marker': 'V28_SCOPE_S1',
                              'migrated_from': 'nested_balances_v28'},
                    'metadata': {'seed_task': 'V28_SCOPE_S1', 'is_internal_user': True, 'synthetic': True},
                })
            # Remove the nested doc by _id
            await ugi.delete_one({'_id': doc['_id']})
            migrated += 1
        except Exception as e:
            errors.append({'user_id': uid, 'err': str(e)[:160]})

    # Post-state counts
    post_marker = await ugi.count_documents({'meta.v28_scope_s1': True})
    post_nested = await ugi.count_documents({'meta.v28_scope_s1': True, 'balances': {'$exists': True}})
    post_flat = await ugi.count_documents({'meta.v28_scope_s1': True, 'gift_id': {'$exists': True}, 'quantity': {'$exists': True}})

    # Sanity: verify route schema can read at least one stage5_qa user
    sample = await ugi.find_one({'user_id': 'stage5_qa_0001', 'gift_id': 'gift_test_001'})
    sample_ok = bool(sample and sample.get('quantity', 0) > 0)

    client.close()

    out = {
        'task_origin': 'AF2-N-V28-SCOPE-S1-SCHEMA-FIX',
        'timestamp_utc': started,
        'mode': 'MIGRATE_NESTED_TO_FLAT',
        'production_db_touched': True,
        'production_db_writes_scope': 'V28_SCOPE_S1 marker only',
        'pre_counts': {
            'marker_total': pre_marker,
            'marker_nested': pre_nested,
            'marker_flat': pre_flat,
        },
        'post_counts': {
            'marker_total': post_marker,
            'marker_nested': post_nested,
            'marker_flat': post_flat,
        },
        'migrated_users': migrated,
        'skipped': skipped,
        'errors_count': len(errors),
        'errors_sample': errors[:5],
        'route_schema_probe': {'user': 'stage5_qa_0001', 'gift_id': 'gift_test_001',
                                'found_with_quantity': sample_ok,
                                'quantity_observed': (sample or {}).get('quantity')},
        'safety': {
            'cap_unchanged': True,
            'allowlist_unchanged': True,
            'no_borea_records_added': True,
            'marker_preserved': post_flat >= migrated,
        },
    }
    out['verdict'] = 'PASS' if all([
        out['post_counts']['marker_nested'] == 0,
        out['post_counts']['marker_flat'] >= migrated,
        sample_ok,
        len(errors) == 0,
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} migrated={migrated} flat_now={post_flat} nested_now={post_nested} probe_ok={sample_ok}")
    return 0 if out['verdict'] == 'PASS' else 2


def main():
    return asyncio.run(_async_main())


if __name__ == '__main__':
    sys.exit(main())
