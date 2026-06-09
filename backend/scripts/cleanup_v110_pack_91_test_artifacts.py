#!/usr/bin/env python3
"""
Pack 91 — Refuse-by-default cleanup di test artifacts marcati Pack 91.

USO:
    python3 cleanup_v110_pack_91_test_artifacts.py            # dry-run (default)
    python3 cleanup_v110_pack_91_test_artifacts.py --apply    # esegue delete

REGOLE:
  - Dry-run è il default. Senza --apply NESSUN delete viene eseguito.
  - Elimina SOLO documenti con `pack_91_test_artifact=true` o email matching
    `pack91_test_user_*@test.com`.
  - NESSUN delete su utenti reali, NESSUN unmarked test write.
"""
import os, sys, asyncio, re
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

MONGO = os.getenv('MONGO_URL')
DB_NAME = 'divine_waifus'
TEST_USER_EMAIL_RE = r'^pack91_test_user_\d+@test\.com$'
MARKER = 'pack_91_test_artifact'


async def main(apply_changes: bool):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    # Find candidate test users
    candidates = await db.users.find({
        '$or': [
            {MARKER: True},
            {'email': {'$regex': TEST_USER_EMAIL_RE}},
        ]
    }).to_list(None)
    test_user_ids = [u['id'] for u in candidates]
    print(f'[CLEANUP DRY-RUN] candidate test users: {len(test_user_ids)}')
    for u in candidates:
        print(f'  - {u.get("email")} id={u.get("id")} marker={u.get(MARKER)}')

    # Count what would be deleted
    if test_user_ids:
        inv_n = await db.inventory.count_documents({'user_id': {'$in': test_user_ids}})
        psp_n = await db.player_server_profiles.count_documents({'user_id': {'$in': test_user_ids}})
        uh_n = await db.user_heroes.count_documents({'user_id': {'$in': test_user_ids}})
    else:
        inv_n = psp_n = uh_n = 0
    print(f'[CLEANUP DRY-RUN] would_delete users={len(test_user_ids)} inventory={inv_n} psp={psp_n} user_heroes={uh_n}')

    if not apply_changes:
        print('[CLEANUP] dry-run only (no --apply). Refusing to mutate.')
        return 0

    if not test_user_ids:
        print('[CLEANUP] nothing to delete; exit clean.')
        return 0

    # Apply
    r_users = await db.users.delete_many({'id': {'$in': test_user_ids}})
    r_inv = await db.inventory.delete_many({'user_id': {'$in': test_user_ids}})
    r_psp = await db.player_server_profiles.delete_many({'user_id': {'$in': test_user_ids}})
    r_uh = await db.user_heroes.delete_many({'user_id': {'$in': test_user_ids}})
    print(f'[CLEANUP APPLIED] users={r_users.deleted_count} inventory={r_inv.deleted_count} psp={r_psp.deleted_count} user_heroes={r_uh.deleted_count}')
    return 0


if __name__ == '__main__':
    apply_flag = ('--apply' in sys.argv)
    rc = asyncio.run(main(apply_flag))
    sys.exit(rc)
