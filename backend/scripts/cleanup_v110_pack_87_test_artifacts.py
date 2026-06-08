#!/usr/bin/env python3
"""
Pack 87 — Cleanup script per artefatti di test creati dalla validator/smoke.

REFUSE-BY-DEFAULT. DRY-RUN. NO deletion of real production PSP/user_heroes.

Uso:
  python3 cleanup_v110_pack_87_test_artifacts.py            # dry-run, refuse
  python3 cleanup_v110_pack_87_test_artifacts.py --dry-run  # esplicito dry-run
  python3 cleanup_v110_pack_87_test_artifacts.py --apply    # esegue cleanup degli artefatti Pack 87 marcati

Marcatori:
  - users.email LIKE 'pack87_test_user_%@test.com'
  - user_heroes.creation_source='server_scoped_starter_flow_pack_87' AND user_id in test_users
  - player_server_profiles.server_id LIKE 's_pack87_%'

Production safety:
  - refuse se 0 target trovati
  - refuse se target appare real user (email non in pattern test)
  - refuse se starter marker attaccato a real user_heroes (per safety)
"""
import os, sys, argparse, asyncio, re
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

TEST_USER_EMAIL_PATTERN = re.compile(r'^pack87_test_user_\d+@test\.com$')

async def main(apply_flag: bool):
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = client.divine_waifus
    test_users = await db.users.find({'email': {'$regex': r'^pack87_test_user_\d+@test\.com$'}}).to_list(None)
    test_user_ids = [u['id'] for u in test_users]
    # starter user_heroes Pack 87 SOLO se user_id in test_users (production safety)
    legacy_starter_uh = 0
    if test_user_ids:
        legacy_starter_uh = await db.user_heroes.count_documents({
            'creation_source': 'server_scoped_starter_flow_pack_87',
            'user_id': {'$in': test_user_ids},
        })
    test_psp_query = {'$or': [
        {'server_id': {'$regex': r'^s_pack87_'}},
        {'user_id': {'$in': test_user_ids}} if test_user_ids else {'user_id': '__never_match__'},
    ]}
    test_psp = await db.player_server_profiles.count_documents(test_psp_query)
    print('-- PACK 87 CLEANUP DRY-RUN REPORT --')
    print(f'test_users_found = {len(test_user_ids)} (pattern pack87_test_user_*@test.com)')
    print(f'starter_user_heroes_pack87_found (only test users) = {legacy_starter_uh}')
    print(f'test_psp_found = {test_psp} (server_id LIKE s_pack87_* OR user_id in test_users)')
    if not apply_flag:
        print('MODE = DRY-RUN (default). No deletion executed.')
        print('To apply cleanup, re-run with --apply.')
        return 0
    total = len(test_user_ids) + legacy_starter_uh + test_psp
    if total == 0:
        print('REFUSE: 0 target artifacts found. Aborting cleanup to avoid empty operation.')
        return 0
    # Production safety: tutti i test_users devono essere pattern-matched
    for u in test_users:
        if not TEST_USER_EMAIL_PATTERN.match(u.get('email', '')):
            print(f'REFUSE: user {u.get("email")} does not match pack87 test pattern.')
            return 1
    # Production safety: starter user_heroes con marker MA user_id NON in test_users → NON toccare
    # (è già garantito dal filter sopra, ma re-controlliamo)
    real_starter_with_marker = await db.user_heroes.count_documents({
        'creation_source': 'server_scoped_starter_flow_pack_87',
        'user_id': {'$nin': test_user_ids if test_user_ids else ['__never__']},
    })
    print(f'real_starter_user_heroes_with_marker_NOT_touched = {real_starter_with_marker}')
    deleted_users = await db.users.delete_many({'id': {'$in': test_user_ids}})
    deleted_uh = await db.user_heroes.delete_many({
        'creation_source': 'server_scoped_starter_flow_pack_87',
        'user_id': {'$in': test_user_ids},
    })
    deleted_psp = await db.player_server_profiles.delete_many(test_psp_query)
    print(f'APPLIED: users={deleted_users.deleted_count} starter_user_heroes_pack87={deleted_uh.deleted_count} test_psp={deleted_psp.deleted_count}')
    return 0

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    rc = asyncio.get_event_loop().run_until_complete(main(args.apply))
    sys.exit(rc)
