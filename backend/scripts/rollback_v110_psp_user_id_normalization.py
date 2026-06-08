#!/usr/bin/env python3
"""
Pack 83 - ROLLBACK SCRIPT per v110 PSP user_id physical normalization.

REFUSE-BY-DEFAULT. NESSUNA esecuzione automatica.
Ripristina `user_id` da uuid -> ObjectId-string legacy SOLO per i PSP
marcati con il batch_id specifico. Nessun delete. Supporta --dry-run.

USO FUTURO (post-execute, in caso di problema):
  python3 rollback_v110_psp_user_id_normalization.py \\
    --batch-id <migration_batch_id> \\
    --approval-string "AUTORIZZO_V110_PSP_USER_ID_PHYSICAL_NORMALIZATION_ROLLBACK_SU_DIVINE_WAIFUS" \\
    --confirm-rollback \\
    --dry-run            # opzionale: simula senza scrivere

Vincoli:
  - NESSUN delete: solo $set per ripristinare user_id legacy + rimuovere marker idempotency.
  - Richiede batch_id esatto.
  - Richiede approval string esatta.
  - Default = DRY-RUN. Per scrivere davvero serve --confirm-rollback E --no-dry-run.
"""
import argparse, asyncio, os, sys, json
sys.path.insert(0, '/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

ROLLBACK_APPROVAL_STRING_REQUIRED = 'AUTORIZZO_V110_PSP_USER_ID_PHYSICAL_NORMALIZATION_ROLLBACK_SU_DIVINE_WAIFUS'


async def main(args):
    if not args.batch_id:
        print('REFUSED: --batch-id required (the v110_psp_user_id_normalization_* batch id from the execute step)')
        sys.exit(2)
    if args.approval_string != ROLLBACK_APPROVAL_STRING_REQUIRED:
        print(f'REFUSED: --approval-string mismatch. Required exactly: {ROLLBACK_APPROVAL_STRING_REQUIRED}')
        sys.exit(2)
    if not args.confirm_rollback:
        print('REFUSED: --confirm-rollback flag required')
        sys.exit(2)
    dry = not args.no_dry_run
    c = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = c.divine_waifus
    q = {'_slc_psp_user_id_normalization_batch_id': args.batch_id}
    affected = await db.player_server_profiles.count_documents(q)
    if affected == 0:
        print(f'NO_PSP_FOUND for batch_id={args.batch_id}; nothing to rollback.')
        sys.exit(0)
    print(f'Affected PSP for batch_id={args.batch_id}: {affected}')
    if dry:
        print('DRY-RUN ONLY. No writes. To execute: pass --no-dry-run')
        # Mostra primi 3 esempi del rollback PIANIFICATO
        sample = []
        async for psp in db.player_server_profiles.find(q).limit(3):
            sample.append({
                'psp_id': str(psp.get('_id')),
                'current_user_id_uuid': psp.get('user_id'),
                'legacy_user_id_to_restore': psp.get('_slc_psp_user_id_legacy_objectid_backup'),
                'server_id': psp.get('server_id'),
            })
        print(json.dumps({'planned_rollback_sample_first_3': sample, 'dry_run': True, 'db_writes': 0}, indent=2))
        sys.exit(0)
    # REAL ROLLBACK (richiede esecuzione futura esplicita)
    print('REAL ROLLBACK MODE ENABLED. Writing $set + $unset to restore legacy user_id...')
    # Per ciascun PSP: setta user_id = _slc_psp_user_id_legacy_objectid_backup, rimuove marker.
    rolled = 0
    async for psp in db.player_server_profiles.find(q):
        legacy = psp.get('_slc_psp_user_id_legacy_objectid_backup')
        if not legacy:
            continue
        await db.player_server_profiles.update_one(
            {'_id': psp['_id']},
            {
                '$set': {'user_id': legacy, '_slc_psp_user_id_namespace': 'objectid_legacy_rolled_back'},
                '$unset': {'_slc_psp_user_id_normalization_batch_id': '', '_slc_psp_user_id_legacy_objectid_backup': ''},
            }
        )
        rolled += 1
    print(json.dumps({'rolled_back': rolled, 'batch_id': args.batch_id, 'dry_run': False}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--batch-id', required=False)
    p.add_argument('--approval-string', required=False, default='')
    p.add_argument('--confirm-rollback', action='store_true')
    p.add_argument('--no-dry-run', action='store_true', help='Real writes ONLY when this flag is passed')
    asyncio.run(main(p.parse_args()))
