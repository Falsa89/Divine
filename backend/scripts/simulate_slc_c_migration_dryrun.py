#!/usr/bin/env python3
"""SLC-C — Dry-Run Migration Simulator (NO DB WRITES).

Simulates the mapping user_id → (account_id, server_id=s1) for every
user currently present in the MongoDB instance, using READ-ONLY queries.
Produces an aggregated report at:
  /app/data/design/server_lifecycle/_slc_c_migration_dryrun_simulation_v1_result.json

The report explicitly contains:
  execution_ready=false
  second_server_opening_allowed=false

until a real, approved migration is committed.
"""
from __future__ import annotations
import asyncio, json, os, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import DESIGN_DIR, finish  # noqa: E402

NAME = 'slc_c_migration_dryrun_simulation_v1'
DEFAULT_SERVER_ID = 's1'
MAX_SAMPLE_MAPPINGS = 20

SERVER_BOUND_COLLECTIONS = [
    'user_heroes', 'teams', 'inventory', 'gacha_history', 'story_progress',
    'user_affinity_state', 'gift_transaction_ledger', 'user_gift_inventory',
    'event_progress', 'guilds', 'arena_rankings',
]


async def simulate() -> dict:
    from motor.motor_asyncio import AsyncIOMotorClient
    from dotenv import load_dotenv
    load_dotenv('/app/backend/.env')
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        return {'error': 'MONGO_URL not configured', 'execution_ready': False}
    client = AsyncIOMotorClient(mongo_url)
    try:
        # default db name resolution
        db_name = os.environ.get('DB_NAME') or 'test_database'
        db = client[db_name]
        users_count = await db.users.count_documents({})
        # Sample first N users for the mapping preview (read-only)
        sample_mappings = []
        cur = db.users.find({}, {'_id': 0, 'user_id': 1, 'email': 1}).limit(MAX_SAMPLE_MAPPINGS)
        async for u in cur:
            uid = u.get('user_id') or u.get('email')
            if uid:
                sample_mappings.append({
                    'legacy_user_id': uid,
                    'planned_account_id': uid,
                    'planned_server_id': DEFAULT_SERVER_ID,
                    'would_create_server_profile': True,
                })
        # Per-collection projected counts (NO modification)
        projected_tag_counts = {}
        for col in SERVER_BOUND_COLLECTIONS:
            try:
                projected_tag_counts[col] = await db[col].count_documents({})
            except Exception as ex:
                projected_tag_counts[col] = f'error:{ex}'
        return {
            'mongo_reachable': True,
            'db_name': db_name,
            'users_count': users_count,
            'default_server_id': DEFAULT_SERVER_ID,
            'projected_server_profiles_to_create': users_count,
            'projected_documents_to_tag_with_server_id': projected_tag_counts,
            'sample_mappings': sample_mappings,
        }
    finally:
        client.close()


def main() -> int:
    errs = []
    try:
        sim = asyncio.run(simulate())
    except Exception as ex:
        sim = {'mongo_reachable': False, 'error': str(ex)}

    payload = {
        'task_origin': 'SLC-C-MIGRATION-DRYRUN-SIMULATION',
        'version': 'v1',
        'mode': 'DRY_RUN_NO_DB_WRITE',
        'design_only': True,
        'utc': datetime.now(timezone.utc).isoformat(),
        'simulation': sim,
        'execution_ready': False,
        'second_server_opening_allowed': False,
        'safety': {
            'no_db_write': True,
            'no_collection_creation': True,
            'no_index_creation': True,
            'no_runtime_change': True,
            'no_borea_exposure': True,
            'no_af2n_change': True,
        },
        'notes': [
            'This is a READ-ONLY dry-run. No MongoDB writes were performed.',
            'execution_ready stays false until a real, approved migration is committed.',
            'second_server_opening_allowed stays false until phase-12 acceptance is reached.',
        ],
    }
    out = DESIGN_DIR / f'_{NAME}_full_report.json'
    with out.open('w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    # Validation: never declare execution_ready=true here
    if payload['execution_ready'] is not False:
        errs.append('execution_ready must be false in dry-run')
    if payload['second_server_opening_allowed'] is not False:
        errs.append('second_server_opening_allowed must be false in dry-run')
    return finish(NAME, errs, {
        'mongo_reachable': sim.get('mongo_reachable', False),
        'users_count': sim.get('users_count'),
        'projected_documents_to_tag_with_server_id': sim.get('projected_documents_to_tag_with_server_id'),
        'default_server_id': sim.get('default_server_id'),
        'sample_mapping_count': len(sim.get('sample_mappings', [])) if sim.get('mongo_reachable') else 0,
        'execution_ready': False,
        'second_server_opening_allowed': False,
        'full_report_path': str(out),
    })


if __name__ == '__main__':
    sys.exit(main())
