#!/usr/bin/env python3
"""
Pack 92 — Refuse-by-default cleanup di test artifacts marcati Pack 92.

USO:
    python3 cleanup_v110_pack_92_test_artifacts.py            # dry-run (default)
    python3 cleanup_v110_pack_92_test_artifacts.py --apply    # esegue delete

REGOLE:
  - Dry-run è il default. Senza --apply NESSUN delete viene eseguito.
  - Elimina SOLO documenti con `pack_92_test_artifact=true` o email matching
    `pack92_test_user_*@test.com`.
  - NESSUN delete su utenti reali.
"""
import os, sys, asyncio, re
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

MONGO = os.getenv('MONGO_URL')
DB_NAME = 'divine_waifus'
TEST_USER_EMAIL_RE = r'^pack92_test_user_\d+@test\.com$'
MARKER = 'pack_92_test_artifact'


async def main(apply_changes: bool):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
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
    if test_user_ids:
        inv_n = await db.inventory.count_documents({'user_id': {'$in': test_user_ids}})
        psp_n = await db.player_server_profiles.count_documents({'user_id': {'$in': test_user_ids}})
        uh_n = await db.user_heroes.count_documents({'user_id': {'$in': test_user_ids}})
        sp_n = await db.story_progress.count_documents({'user_id': {'$in': test_user_ids}})
        eq_n = await db.user_equipment.count_documents({'user_id': {'$in': test_user_ids}})
    else:
        inv_n = psp_n = uh_n = sp_n = eq_n = 0
    print(f'[CLEANUP DRY-RUN] would_delete users={len(test_user_ids)} inventory={inv_n} psp={psp_n} user_heroes={uh_n} story_progress={sp_n} user_equipment={eq_n}')
    if not apply_changes:
        print('[CLEANUP] dry-run only (no --apply). Refusing to mutate.')
        return 0
    if not test_user_ids:
        return 0
    r1 = await db.users.delete_many({'id': {'$in': test_user_ids}})
    r2 = await db.inventory.delete_many({'user_id': {'$in': test_user_ids}})
    r3 = await db.player_server_profiles.delete_many({'user_id': {'$in': test_user_ids}})
    r4 = await db.user_heroes.delete_many({'user_id': {'$in': test_user_ids}})
    r5 = await db.story_progress.delete_many({'user_id': {'$in': test_user_ids}})
    r6 = await db.user_equipment.delete_many({'user_id': {'$in': test_user_ids}})
    print(f'[CLEANUP APPLIED] users={r1.deleted_count} inv={r2.deleted_count} psp={r3.deleted_count} uh={r4.deleted_count} story={r5.deleted_count} eq={r6.deleted_count}')
    return 0


if __name__ == '__main__':
    apply_flag = ('--apply' in sys.argv)
    rc = asyncio.run(main(apply_flag))
    sys.exit(rc)
