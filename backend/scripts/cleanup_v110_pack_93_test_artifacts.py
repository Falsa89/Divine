#!/usr/bin/env python3
"""Pack 93 — Cleanup test artifacts."""
import os, sys, asyncio
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

MONGO = os.getenv('MONGO_URL')
DB_NAME = 'divine_waifus'
TEST_USER_EMAIL_RE = r'^pack93_test_user_\d+@test\.com$'
MARKER = 'pack_93_test_artifact'

async def main(apply_changes: bool):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    candidates = await db.users.find({'$or': [{MARKER: True}, {'email': {'$regex': TEST_USER_EMAIL_RE}}]}).to_list(None)
    test_user_ids = [u['id'] for u in candidates]
    print(f'[CLEANUP DRY-RUN] candidate test users: {len(test_user_ids)}')
    for u in candidates:
        print(f'  - {u.get("email")} id={u.get("id")} marker={u.get(MARKER)}')
    if not apply_changes:
        print('[CLEANUP] dry-run only (no --apply). Refusing to mutate.')
        return 0
    if not test_user_ids: return 0
    r1 = await db.users.delete_many({'id': {'$in': test_user_ids}})
    r2 = await db.inventory.delete_many({'user_id': {'$in': test_user_ids}})
    r3 = await db.player_server_profiles.delete_many({'user_id': {'$in': test_user_ids}})
    r4 = await db.user_heroes.delete_many({'user_id': {'$in': test_user_ids}})
    r5 = await db.story_progress.delete_many({'user_id': {'$in': test_user_ids}})
    r6 = await db.user_equipment.delete_many({'user_id': {'$in': test_user_ids}})
    r7 = await db.wallet_spend_ledger.delete_many({'user_id': {'$in': test_user_ids}})
    print(f'[CLEANUP APPLIED] users={r1.deleted_count} inv={r2.deleted_count} psp={r3.deleted_count} uh={r4.deleted_count} story={r5.deleted_count} eq={r6.deleted_count} ledger={r7.deleted_count}')
    return 0

if __name__ == '__main__':
    rc = asyncio.run(main('--apply' in sys.argv))
    sys.exit(rc)
