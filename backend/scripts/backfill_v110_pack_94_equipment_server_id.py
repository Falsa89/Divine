#!/usr/bin/env python3
"""
Pack 94 — Equipment server_id backfill (controllato, idempotente).

GATES (pre-apply):
  1. Approval string present in env or argv
  2. Dry-run preview produces non-empty diff
  3. Backup snapshot of user_equipment to /app/data/backups/pack_94_user_equipment_backup_<ts>.json
  4. Only docs WITHOUT server_id are touched
  5. Mapping: per ogni user_id senza server_id, usare PSP esistente. Se utente ha 1 PSP -> usalo. Se multipli -> usa il PSP piu' vecchio (created_at). Se zero PSP -> skip (deferred per user).

USO:
    python3 backfill_v110_pack_94_equipment_server_id.py            # dry-run
    python3 backfill_v110_pack_94_equipment_server_id.py --apply    # apply (richiede approval)
"""
import os, sys, json, asyncio, time
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

MONGO = os.getenv('MONGO_URL')
DB_NAME = 'divine_waifus'
APPROVAL = 'AUTORIZZO_V110_EQUIPMENT_SERVER_SCOPE_BACKFILL_EXECUTE_PACK_94'
TS = int(time.time())


async def main(apply_changes: bool, approval_present: bool):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    # Audit
    n_total = await db.user_equipment.count_documents({})
    n_with = await db.user_equipment.count_documents({'server_id': {'$exists': True, '$ne': None, '$ne': ''}})
    n_without = n_total - n_with
    print(f'[AUDIT] user_equipment total={n_total} with_server_id={n_with} without_server_id={n_without} coverage={(n_with/n_total*100) if n_total else 0:.1f}%')
    # Build mapping plan
    docs_to_fix = await db.user_equipment.find({
        '$or': [{'server_id': {'$exists': False}}, {'server_id': None}, {'server_id': ''}]
    }).to_list(None)
    plan = []
    skipped_no_psp = 0
    for d in docs_to_fix:
        uid = d.get('user_id')
        psps = await db.player_server_profiles.find({'user_id': uid}).sort('created_at', 1).to_list(None)
        if not psps:
            skipped_no_psp += 1
            continue
        target_sid = psps[0].get('server_id')
        plan.append({'doc_id': d.get('id') or str(d.get('_id')), 'user_id': uid, 'target_server_id': target_sid})
    print(f'[PLAN] candidates_to_fix={len(plan)} skipped_no_psp={skipped_no_psp}')

    # Backup snapshot
    backup_path = f'/app/data/backups/pack_94_user_equipment_backup_{TS}.json'
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    all_docs = await db.user_equipment.find({}).to_list(None)
    for d in all_docs:
        d.pop('_id', None)
        for k, v in list(d.items()):
            try:
                json.dumps(v)
            except Exception:
                d[k] = str(v)
    with open(backup_path, 'w') as f:
        json.dump({'ts': TS, 'docs_count': len(all_docs), 'docs': all_docs}, f, default=str)
    print(f'[BACKUP] snapshot saved: {backup_path}')

    if not apply_changes:
        print('[DRY-RUN] no --apply, refusing to mutate. Use --apply with approval to execute.')
        return {'mode': 'dry_run', 'plan_size': len(plan), 'skipped_no_psp': skipped_no_psp, 'backup_path': backup_path}

    if not approval_present:
        print(f'[ABORT] approval string missing: {APPROVAL}. Refusing apply.')
        return {'mode': 'aborted_no_approval'}

    # Apply (idempotent: only update docs that still lack server_id)
    n_updated = 0
    for p in plan:
        r = await db.user_equipment.update_one(
            {'id': p['doc_id'], '$or': [{'server_id': {'$exists': False}}, {'server_id': None}, {'server_id': ''}]},
            {'$set': {
                'server_id': p['target_server_id'],
                '_slc_pack_94_equipment_server_id_backfill': True,
                '_slc_pack_94_equipment_server_id_backfill_ts': TS,
            }}
        )
        n_updated += r.modified_count
    # Verify coverage
    n_with_post = await db.user_equipment.count_documents({'server_id': {'$exists': True, '$ne': None, '$ne': ''}})
    coverage_post = (n_with_post / n_total * 100) if n_total else 0
    # Ledger entry
    await db.equipment_backfill_ledger.insert_one({
        'id': f'pack_94_{TS}',
        'pack': 'MEGA_RELEASE_ACCELERATION_94_EQUIPMENT_BACKFILL_STRICT_SCOPE_AND_LEGACY_CURRENCY_QUARANTINE',
        'approval': APPROVAL,
        'ts': TS,
        'docs_total': n_total,
        'docs_updated': n_updated,
        'skipped_no_psp': skipped_no_psp,
        'coverage_pct_pre': (n_with/n_total*100) if n_total else 0,
        'coverage_pct_post': coverage_post,
        'backup_path': backup_path,
        '_slc_pack_94_equipment_backfill_ledger': True,
    })
    print(f'[APPLIED] docs_updated={n_updated} coverage_post={coverage_post:.1f}%')
    return {
        'mode': 'applied', 'docs_total': n_total, 'docs_updated': n_updated,
        'skipped_no_psp': skipped_no_psp, 'coverage_pct_post': coverage_post,
        'backup_path': backup_path, 'ledger_id': f'pack_94_{TS}',
    }


if __name__ == '__main__':
    apply_flag = ('--apply' in sys.argv)
    approval = (APPROVAL in ' '.join(sys.argv)) or (os.getenv('PACK_94_APPROVAL') == APPROVAL)
    result = asyncio.run(main(apply_flag, approval))
    out = {'pack': 'MEGA_RELEASE_ACCELERATION_94_EQUIPMENT_BACKFILL_STRICT_SCOPE_AND_LEGACY_CURRENCY_QUARANTINE',
           'result': result, 'approval_required': APPROVAL, 'approval_present': approval}
    out_path = '/app/data/design/v110_pack_94_equipment_backfill_strict_currency_quarantine/v110_pack_94_backfill_apply_result_v1.json'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
