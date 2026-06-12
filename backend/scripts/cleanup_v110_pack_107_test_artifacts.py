#!/usr/bin/env python3
"""Pack 107 — Cleanup test artifacts (default dry-run; --apply destructive)."""
import os, sys, asyncio
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv; load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient
MARKER = 'pack_107_test_artifact'
MONGO = os.getenv('MONGO_URL'); DB_NAME = 'divine_waifus'
async def main(apply_changes):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    users = await db.users.find({MARKER: True}, {'id': 1, 'email': 1}).to_list(1000)
    print(f'[cleanup_pack_107] dry-run targets: {len(users)} users')
    for u in users: print(f'  - {u["id"]}')
    if not apply_changes:
        print('[cleanup_pack_107] DRY-RUN ONLY. Pass --apply to execute.')
        return
    for u in users:
        for col in ('users','player_server_profiles','reward_claim_ledger'):
            if col == 'users': await db.users.delete_one({'id': u['id']})
            else: await db[col].delete_many({'user_id': u['id']})
    print('[cleanup_pack_107] APPLY COMPLETE')
if __name__ == '__main__': asyncio.run(main('--apply' in sys.argv))
