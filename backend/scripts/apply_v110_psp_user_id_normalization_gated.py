#!/usr/bin/env python3
"""
Pack 83 - FUTURE EXECUTE SCRIPT (GATED) per v110 PSP user_id physical normalization.

REFUSE-BY-DEFAULT. NESSUNA esecuzione automatica.
Questo script NON viene mai chiamato durante Pack 83.

Uso futuro (richiesto pack dedicato con autorizzazione esplicita):
  python3 apply_v110_psp_user_id_normalization_gated.py \\
    --plan-only                                          # default: solo piano, no writes
  python3 apply_v110_psp_user_id_normalization_gated.py \\
    --execute \\
    --approval-string "AUTORIZZO_V110_PSP_USER_ID_PHYSICAL_NORMALIZATION_SU_DIVINE_WAIFUS" \\
    --mapping-hash-pin <sha256> \\
    --backup-manifest-hash-pin <sha256> \\
    --rollback-plan-pin <sha256> \\
    --commit-hash-pin <git_commit_hash> \\
    --target-db divine_waifus \\
    --batch-id v110_psp_user_id_normalization_<ISO8601>

Gates obbligatori (TUTTI devono essere verdi prima di scrivere):
  1. Approval string esatta
  2. Mapping hash pinned al valore generato dal preflight
  3. Backup manifest hash pinned
  4. Rollback plan hash pinned
  5. Commit hash pinned (per audit trail)
  6. Target DB == 'divine_waifus'
  7. Duplicate (uuid, server_id) collision check passa
  8. Idempotency: PSP gia' marcati con batch_id sono skippati
  9. --execute flag esplicito

DEFAULT: --plan-only. Nessuna scrittura DB.
"""
import argparse, asyncio, os, sys, json, hashlib
sys.path.insert(0, '/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

REQUIRED_APPROVAL_STRING = 'AUTORIZZO_V110_PSP_USER_ID_PHYSICAL_NORMALIZATION_SU_DIVINE_WAIFUS'
REQUIRED_TARGET_DB = 'divine_waifus'

MAPPING_PATH = '/app/data/design/v110_psp_normalization_preflight/v110_psp_normalization_mapping_v1.json'
BACKUP_PATH = '/app/data/design/v110_psp_normalization_preflight/v110_psp_normalization_backup_preflight_v1.json'
ROLLBACK_PATH = '/app/data/design/v110_psp_normalization_preflight/v110_psp_normalization_rollback_plan_v1.json'


def _sha256_of_file_canonical_json(path):
    """Compute sha256 of canonical JSON of the file at path."""
    with open(path) as f:
        d = json.load(f)
    return hashlib.sha256(json.dumps(d, sort_keys=True).encode('utf-8')).hexdigest()


async def main(args):
    plan_only = args.plan_only or not args.execute
    # Gate 1: explicit --execute required
    if not args.execute:
        print('SAFE-DEFAULT: --execute NOT provided. Plan-only mode. NO writes.')
        with open(MAPPING_PATH) as f:
            d = json.load(f)
        print(json.dumps({
            'mode': 'plan_only',
            'mapping_entries_count': d.get('mapping_entries_count'),
            'mapping_hash_sha256_from_preflight': d.get('mapping_hash_sha256'),
            'db_writes': 0,
        }, indent=2))
        return
    # Gate 2: approval string
    if args.approval_string != REQUIRED_APPROVAL_STRING:
        print(f'REFUSED: --approval-string mismatch. Required exactly: {REQUIRED_APPROVAL_STRING}')
        sys.exit(2)
    # Gate 3-5: hash pins
    mapping_doc_hash_internal = json.load(open(MAPPING_PATH))['mapping_hash_sha256']
    if args.mapping_hash_pin != mapping_doc_hash_internal:
        print(f'REFUSED: --mapping-hash-pin mismatch. Expected: {mapping_doc_hash_internal}')
        sys.exit(2)
    backup_doc_hash_internal = json.load(open(BACKUP_PATH))['manifest_hash_sha256']
    if args.backup_manifest_hash_pin != backup_doc_hash_internal:
        print(f'REFUSED: --backup-manifest-hash-pin mismatch. Expected: {backup_doc_hash_internal}')
        sys.exit(2)
    if os.path.exists(ROLLBACK_PATH):
        rb_doc = json.load(open(ROLLBACK_PATH))
        rb_hash = rb_doc.get('rollback_plan_hash_sha256', '')
        if args.rollback_plan_pin != rb_hash:
            print(f'REFUSED: --rollback-plan-pin mismatch. Expected: {rb_hash}')
            sys.exit(2)
    else:
        print('REFUSED: rollback plan file not found at expected path; future execute blocked.')
        sys.exit(2)
    # Gate 6: target DB
    if args.target_db != REQUIRED_TARGET_DB:
        print(f'REFUSED: --target-db must be exactly {REQUIRED_TARGET_DB}')
        sys.exit(2)
    # Gate 7: commit hash
    if not args.commit_hash_pin or len(args.commit_hash_pin) < 7:
        print('REFUSED: --commit-hash-pin required (audit trail)')
        sys.exit(2)
    # Gate 8: batch_id
    if not args.batch_id or 'v110_psp_user_id_normalization_' not in args.batch_id:
        print('REFUSED: --batch-id required and must contain v110_psp_user_id_normalization_ prefix')
        sys.exit(2)
    # All gates open. Perform pre-write duplicate-collision check.
    c = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = c.divine_waifus
    mapping_doc = json.load(open(MAPPING_PATH))
    seen = set()
    for e in mapping_doc.get('entries_full', []):
        key = (e['target_user_id_uuid'], e['server_id'])
        if key in seen:
            print(f'REFUSED: pre-write collision detected for (uuid={e["target_user_id_uuid"]}, server_id={e["server_id"]})')
            sys.exit(2)
        seen.add(key)
    # SAFE: tutte le gate aperte. Esegui update con marker idempotency.
    written = 0
    skipped_idempotent = 0
    for e in mapping_doc.get('entries_full', []):
        # Idempotency: skip se gia' marcato con stesso batch_id (o qualsiasi batch)
        existing = await db.player_server_profiles.find_one({'_id_str_alias': None, 'server_id': e['server_id'], 'user_id': e['target_user_id_uuid'], '_slc_psp_user_id_normalization_batch_id': {'$exists': True}})
        # Trova il PSP per _id (psp_id e' la string di _id; serve ObjectId conversion in future code)
        # Per sicurezza in script gated, lasciamo placeholder; il pack execute futuro fara' la conversion vera.
        skipped_idempotent += 0
    print(json.dumps({
        'mode': 'execute_gated_skeleton',
        'all_gates_open': True,
        'note': 'Skeleton presente ma la scrittura reale e\' delegata al pack execute dedicato futuro con codice di update completo.',
        'db_writes_in_this_skeleton': 0,
        'planned_writes_count': mapping_doc.get('mapping_entries_count'),
    }, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--plan-only', action='store_true')
    p.add_argument('--execute', action='store_true')
    p.add_argument('--approval-string', default='')
    p.add_argument('--mapping-hash-pin', default='')
    p.add_argument('--backup-manifest-hash-pin', default='')
    p.add_argument('--rollback-plan-pin', default='')
    p.add_argument('--commit-hash-pin', default='')
    p.add_argument('--target-db', default='')
    p.add_argument('--batch-id', default='')
    asyncio.run(main(p.parse_args()))
