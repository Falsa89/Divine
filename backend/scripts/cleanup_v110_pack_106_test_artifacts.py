#!/usr/bin/env python3
"""Pack 106 — Cleanup test artifacts (default dry-run; --apply for destructive)."""
import os, sys, asyncio
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

MARKER = 'pack_106_test_artifact'
MONGO = os.getenv('MONGO_URL'); DB_NAME = 'divine_waifus'

async def main(apply_changes: bool):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    users = await db.users.find({MARKER: True}, {'id': 1, 'email': 1}).to_list(1000)
    print(f'[cleanup_pack_106] dry-run targets: {len(users)} users with marker {MARKER}')
    for u in users:
        print(f'  - {u["id"]} ({u.get("email")})')
    if not apply_changes:
        print('[cleanup_pack_106] DRY-RUN ONLY — nothing deleted. Pass --apply to execute.')
        return
    for u in users:
        uid = u['id']
        for col in ('users','player_server_profiles','user_heroes','user_equipment','inventory','wallets','reward_claim_ledger','daily_quest_progress','tower_progress','teams'):
            if col == 'users':
                await db.users.delete_one({'id': uid})
            else:
                await db[col].delete_many({'user_id': uid})
        print(f'  - DELETED uid={uid}')
    print('[cleanup_pack_106] APPLY COMPLETE')

if __name__ == '__main__':
    asyncio.run(main('--apply' in sys.argv))
