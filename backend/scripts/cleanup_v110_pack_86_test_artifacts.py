#!/usr/bin/env python3
"""
Pack 86 — Cleanup script per artefatti di test creati dalla validator/smoke.

REFUSE-BY-DEFAULT. DRY-RUN. NO deletion of real production PSP.

Uso:
  python3 cleanup_v110_pack_86_test_artifacts.py            # dry-run, refuse
  python3 cleanup_v110_pack_86_test_artifacts.py --dry-run  # esplicito dry-run (default)
  python3 cleanup_v110_pack_86_test_artifacts.py --apply    # esegue cleanup degli artefatti Pack 86 marcati

Marcatori:
  - users.email LIKE 'pack86_test_user_%@test.com'
  - user_heroes._slc_pack_86_legacy_dev_only_starter=true
  - player_server_profiles.server_id LIKE 's_pack86_%' (server di test ephemerale)

Production safety:
  - refuse se 0 target trovati (non si esegue cleanup vuoto)
  - refuse se target appare un real user (email non in pattern test)
  - refuse se --apply non passato (default dry-run)
"""
import os, sys, argparse, asyncio, re
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

TEST_USER_EMAIL_PATTERN = re.compile(r'^pack86_test_user_\d+@test\.com$')
TEST_SERVER_ID_PATTERN_PREFIXES = ('s_pack86_',)

async def main(apply_flag: bool):
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = client.divine_waifus
    # 1. Trova test users (solo via pattern email pack86)
    test_users = await db.users.find({'email': {'$regex': r'^pack86_test_user_\d+@test\.com$'}}).to_list(None)
    test_user_ids = [u['id'] for u in test_users]
    # 2. user_heroes marcati come legacy dev-only Pack 86
    legacy_user_heroes = await db.user_heroes.count_documents({'_slc_pack_86_legacy_dev_only_starter': True})
    # 3. test PSP per server pack86
    test_psp = await db.player_server_profiles.count_documents({'$or': [
        {'server_id': {'$regex': r'^s_pack86_'}},
        {'user_id': {'$in': test_user_ids}} if test_user_ids else {'user_id': '__never_match__'},
    ]})
    print('-- PACK 86 CLEANUP DRY-RUN REPORT --')
    print(f'test_users_found = {len(test_user_ids)} (pattern pack86_test_user_*@test.com)')
    print(f'legacy_dev_only_user_heroes_found = {legacy_user_heroes}')
    print(f'test_psp_found = {test_psp} (server_id starts with s_pack86_ OR user_id in test_users)')
    # Production safety: refuse-by-default
    if not apply_flag:
        print('MODE = DRY-RUN (default). No deletion executed.')
        print('To apply cleanup of these test artifacts, re-run with --apply.')
        return 0
    # Production safety: refuse if target count 0
    total = len(test_user_ids) + legacy_user_heroes + test_psp
    if total == 0:
        print('REFUSE: 0 target artifacts found. Aborting cleanup to avoid empty operation.')
        return 0
    # Production safety: verify all test_users are pattern-matched (no real user collateral)
    for u in test_users:
        if not TEST_USER_EMAIL_PATTERN.match(u.get('email', '')):
            print(f'REFUSE: user {u.get("email")} does not match pack86 test pattern. Aborting.')
            return 1
    # Eseguo cleanup
    deleted_users = await db.users.delete_many({'id': {'$in': test_user_ids}})
    deleted_user_heroes = await db.user_heroes.delete_many({'_slc_pack_86_legacy_dev_only_starter': True})
    deleted_test_psp = await db.player_server_profiles.delete_many({'$or': [
        {'server_id': {'$regex': r'^s_pack86_'}},
        {'user_id': {'$in': test_user_ids}} if test_user_ids else {'user_id': '__never_match__'},
    ]})
    print(f'APPLIED: deleted users={deleted_users.deleted_count}, user_heroes={deleted_user_heroes.deleted_count}, test_psp={deleted_test_psp.deleted_count}')
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='execute cleanup (default: dry-run / refuse)')
    parser.add_argument('--dry-run', action='store_true', help='explicit dry-run (default)')
    args = parser.parse_args()
    rc = asyncio.get_event_loop().run_until_complete(main(args.apply))
    sys.exit(rc)
