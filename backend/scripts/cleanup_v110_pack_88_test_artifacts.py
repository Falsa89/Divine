#!/usr/bin/env python3
"""
Pack 88 — Cleanup script per artefatti di test creati dalla validator/smoke.

REFUSE-BY-DEFAULT. DRY-RUN. NO deletion of real production data.

Uso:
  python3 cleanup_v110_pack_88_test_artifacts.py             # dry-run, refuse
  python3 cleanup_v110_pack_88_test_artifacts.py --dry-run   # esplicito dry-run
  python3 cleanup_v110_pack_88_test_artifacts.py --apply     # esegue cleanup
"""
import os, sys, argparse, asyncio, re
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

TEST_USER_EMAIL_PATTERN = re.compile(r'^pack88_test_user_\d+@test\.com$')

async def main(apply_flag: bool):
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = client.divine_waifus
    test_users = await db.users.find({'email': {'$regex': r'^pack88_test_user_\d+@test\.com$'}}).to_list(None)
    test_user_ids = [u['id'] for u in test_users]
    test_uh = 0
    if test_user_ids:
        test_uh = await db.user_heroes.count_documents({'user_id': {'$in': test_user_ids}})
    test_psp_query = {'$or': [
        {'server_id': {'$regex': r'^s_pack88_'}},
        {'user_id': {'$in': test_user_ids}} if test_user_ids else {'user_id': '__never_match__'},
    ]}
    test_psp = await db.player_server_profiles.count_documents(test_psp_query)
    print('-- PACK 88 CLEANUP DRY-RUN REPORT --')
    print(f'test_users_found = {len(test_user_ids)}')
    print(f'test_user_heroes_in_test_users = {test_uh}')
    print(f'test_psp_found = {test_psp}')
    if not apply_flag:
        print('MODE = DRY-RUN. No deletion executed.')
        return 0
    total = len(test_user_ids) + test_uh + test_psp
    if total == 0:
        print('REFUSE: 0 target artifacts found.')
        return 0
    for u in test_users:
        if not TEST_USER_EMAIL_PATTERN.match(u.get('email', '')):
            print(f'REFUSE: user {u.get("email")} not pattern matched.')
            return 1
    du = await db.users.delete_many({'id': {'$in': test_user_ids}})
    duh = await db.user_heroes.delete_many({'user_id': {'$in': test_user_ids}}) if test_user_ids else None
    dpsp = await db.player_server_profiles.delete_many(test_psp_query)
    print(f'APPLIED: users={du.deleted_count} user_heroes={duh.deleted_count if duh else 0} psp={dpsp.deleted_count}')
    return 0

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    rc = asyncio.get_event_loop().run_until_complete(main(args.apply))
    sys.exit(rc)
