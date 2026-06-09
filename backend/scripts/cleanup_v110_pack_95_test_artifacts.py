#!/usr/bin/env python3
"""Pack 95 — cleanup test artifacts (refuse-by-default).

Usage:
  python3 cleanup_v110_pack_95_test_artifacts.py                # DRY-RUN (default)
  python3 cleanup_v110_pack_95_test_artifacts.py --apply        # esegue cancellazione

Cancella SOLO documenti marcati `pack_95_test_artifact=true`. Mai produzione.
"""
import os, sys, asyncio, argparse
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

MARKER = 'pack_95_test_artifact'
COLLECTIONS = [
    'users', 'player_server_profiles', 'user_heroes',
    'user_equipment', 'inventory', 'wallets',
    'reward_claim_ledger', 'story_progress', 'retirement_history',
    'shop_purchases_special',
]


async def main(apply_mode: bool):
    mongo = os.getenv('MONGO_URL'); db_name = 'divine_waifus'
    c = AsyncIOMotorClient(mongo); db = c[db_name]
    report = {}
    for col in COLLECTIONS:
        cnt = await db[col].count_documents({MARKER: True})
        report[col] = {'matched': cnt, 'deleted': 0}
        if apply_mode and cnt > 0:
            r = await db[col].delete_many({MARKER: True})
            report[col]['deleted'] = r.deleted_count
    print('=' * 60)
    print(f"PACK 95 CLEANUP - {'APPLY' if apply_mode else 'DRY-RUN'} mode")
    print('=' * 60)
    for col, info in report.items():
        print(f"  {col:30s} matched={info['matched']:4d} deleted={info['deleted']:4d}")
    if not apply_mode:
        print('\n[REFUSED BY DEFAULT] Re-run with --apply to delete marked test artifacts.')
    else:
        print('\n[APPLIED] Pack 95 test artifacts removed.')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true', help='Esegue cancellazione (default: dry-run)')
    args = p.parse_args()
    asyncio.run(main(args.apply))
