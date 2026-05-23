#!/usr/bin/env python3
# SLC-G COMMIT-A APPLY (GATED MIGRATION COMMIT)
# Esegue il backfill default `s1` per le collection server-bound classificate da SLC-F/SLC-G.
# set_only_if_missing semantics.
# NO route patch. NO feature flag. NO secondo server. NO delete.
# Gating: richiede env SLC_G_WRITE_GATE_EXPLICIT_APPROVAL=true.
import json, os, sys, hashlib, uuid
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')
from pymongo import MongoClient, UpdateOne

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
SAFETY_DIR = ROOT / 'data/design/system_safety'
BACKUP_DIR = SAFETY_DIR / 'backups'
REPORTS_DIR = ROOT / 'backend/reports'
for d in (BACKUP_DIR, REPORTS_DIR, SAFETY_DIR): d.mkdir(parents=True, exist_ok=True)

RESULT = REPORTS_DIR / 'slc_g_commit_a_apply_result.json'
MIGRATION_MARKER_FILE = SAFETY_DIR / 'slc_g_default_s1_migration_apply_result_v1.json'

MARKER = 'SLC_G_WRITE_GATE_EXPLICIT_APPROVAL'

# Scope per contratto SLC-G
SERVER_BOUND_PRESENT_EXPECTED = [
    'user_heroes','teams','inventory','story_progress',
    'guilds','user_affinity_state','gift_transaction_ledger',
    'user_gift_inventory',
]
SERVER_BOUND_OPTIONAL = [
    'servers','server_profiles','server_wallets_free','gacha_history',
    'arena_rankings','server_cosmetics','equipped_cosmetics','event_progress',
]
MIXED_USERS = 'users'
# AF2-N row count invariants
AF2N_COUNT_CHECKS = ['user_gift_inventory','gift_transaction_ledger','user_affinity_state']

MARKER_DOC_FIELD = '_slc_g_commit_marker'

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def fail_safe(msg, extra=None):
    out = {'task_origin':'SLC-G-COMMIT-A-APPLY','verdict':'FAILED_SAFE','reason':msg,
           'timestamp_utc':datetime.now(timezone.utc).isoformat(),'extra':extra}
    RESULT.write_text(json.dumps(out, indent=2, default=str))
    print(f'FAILED_SAFE: {msg}')
    if extra: print(f'  extra: {extra}')
    sys.exit(2)

def main():
    if os.environ.get(MARKER, '').lower() != 'true':
        fail_safe(f'approval_marker_absent:{MARKER}')

    url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME','test_database')
    db = MongoClient(url, serverSelectionTimeoutMS=5000)[db_name]
    present = set(db.list_collection_names())

    # ---- PRE-STATE SNAPSHOT (AF2-N + per-collection counts) ----
    af2n_pre = {c: db[c].count_documents({}) for c in AF2N_COUNT_CHECKS if c in present}
    pre_counts = {}
    pre_missing = {}
    for c in SERVER_BOUND_PRESENT_EXPECTED + SERVER_BOUND_OPTIONAL:
        if c in present:
            pre_counts[c] = db[c].count_documents({})
            pre_missing[c] = {
                'missing_server_id': db[c].count_documents({'server_id':{'$exists':False}}),
                'missing_account_id_with_user_id': db[c].count_documents({'account_id':{'$exists':False},'user_id':{'$exists':True}}),
                'unsafe_unknown': db[c].count_documents({'user_id':{'$exists':False},'account_id':{'$exists':False}}),
            }
    if MIXED_USERS in present:
        pre_counts[MIXED_USERS] = db[MIXED_USERS].count_documents({})
        pre_missing[MIXED_USERS] = {
            'missing_account_id': db[MIXED_USERS].count_documents({'account_id':{'$exists':False}}),
            'has_id_field': db[MIXED_USERS].count_documents({'id':{'$exists':True}}),
        }

    # ---- SAFETY: refuse to run if any server-bound collection has unsafe_unknown ----
    for c, mm in pre_missing.items():
        if c == MIXED_USERS: continue
        if mm.get('unsafe_unknown',0) > 0:
            fail_safe(f'unsafe_unknown_present_in:{c}_count={mm["unsafe_unknown"]}_must_be_zero_before_commit')

    # ---- FULL BACKUP (full doc dump for each touched collection) ----
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    migration_id = f'slc_g_commit_a_{ts}_{uuid.uuid4().hex[:8]}'
    backup_root = BACKUP_DIR / f'slc_g_commit_a_pre_backup_{ts}'
    backup_root.mkdir(parents=True, exist_ok=True)
    backup_manifest = {
        'migration_id': migration_id,
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'collections': {},
    }
    for c in list(pre_counts.keys()):
        docs = list(db[c].find({}))
        # serialize ObjectId/datetime
        ser = []
        for d in docs:
            d['_id'] = str(d['_id'])
            for k, v in list(d.items()):
                if isinstance(v, datetime):
                    d[k] = v.isoformat()
            ser.append(d)
        col_file = backup_root / f'{c}.json'
        payload = json.dumps(ser, default=str, indent=2)
        col_file.write_text(payload)
        backup_manifest['collections'][c] = {
            'doc_count_pre': len(ser),
            'file': col_file.name,
            'sha256': sha256(payload),
        }
    manifest_file = backup_root / 'manifest.json'
    manifest_payload = json.dumps(backup_manifest, indent=2, default=str)
    backup_manifest['manifest_sha256'] = sha256(manifest_payload)
    manifest_file.write_text(json.dumps(backup_manifest, indent=2, default=str))

    # ---- APPLY: set-only-if-missing per collection ----
    write_log = {}
    marker_payload = {
        'task': 'SLC-G-COMMIT-A-APPLY',
        'version': 'v1',
        'migration_id': migration_id,
        'applied_at_utc': datetime.now(timezone.utc).isoformat(),
    }

    # Server-bound: set server_id=s1 where missing, then set account_id=user_id where missing (aggregation pipeline)
    for c in pre_counts:
        if c == MIXED_USERS: continue
        coll = db[c]
        # 1) server_id backfill
        r1 = coll.update_many({'server_id':{'$exists':False}},
                              {'$set':{'server_id':'s1', MARKER_DOC_FIELD: marker_payload}})
        # 2) account_id = user_id where account_id missing AND user_id exists (aggregation pipeline update)
        r2 = coll.update_many({'account_id':{'$exists':False},'user_id':{'$exists':True}},
                              [{'$set': {'account_id':'$user_id', MARKER_DOC_FIELD: marker_payload}}])
        write_log[c] = {
            'server_id_set_modified': r1.modified_count,
            'account_id_set_modified': r2.modified_count,
        }

    # Mixed users: set account_id=id where missing AND id present; NEVER touch server_id
    if MIXED_USERS in present:
        r3 = db[MIXED_USERS].update_many({'account_id':{'$exists':False},'id':{'$exists':True}},
                                         [{'$set':{'account_id':'$id', MARKER_DOC_FIELD: marker_payload}}])
        write_log[MIXED_USERS] = {
            'server_id_set_modified': 0,  # never
            'account_id_set_modified': r3.modified_count,
        }

    # ---- POST-STATE SNAPSHOT ----
    af2n_post = {c: db[c].count_documents({}) for c in AF2N_COUNT_CHECKS if c in present}
    post_counts = {c: db[c].count_documents({}) for c in pre_counts}
    post_missing = {}
    for c in pre_counts:
        if c == MIXED_USERS:
            post_missing[c] = {
                'missing_account_id': db[c].count_documents({'account_id':{'$exists':False}}),
            }
        else:
            post_missing[c] = {
                'missing_server_id': db[c].count_documents({'server_id':{'$exists':False}}),
                'missing_account_id_with_user_id': db[c].count_documents({'account_id':{'$exists':False},'user_id':{'$exists':True}}),
                'unsafe_unknown': db[c].count_documents({'user_id':{'$exists':False},'account_id':{'$exists':False}}),
            }

    # ---- VERIFY INVARIANTS ----
    errs = []
    # 1) AF2-N row counts preserved exactly
    for c, pre in af2n_pre.items():
        if af2n_post.get(c) != pre:
            errs.append(f'af2n_count_drift:{c}:pre={pre},post={af2n_post.get(c)}')
    # 2) total doc counts unchanged (no inserts/deletes)
    for c, pre in pre_counts.items():
        if post_counts.get(c) != pre:
            errs.append(f'doc_count_drift:{c}:pre={pre},post={post_counts.get(c)}')
    # 3) post: no server-bound missing server_id
    for c in pre_counts:
        if c == MIXED_USERS: continue
        if post_missing[c]['missing_server_id'] != 0:
            errs.append(f'still_missing_server_id_post:{c}={post_missing[c]["missing_server_id"]}')
        if post_missing[c]['unsafe_unknown'] != 0:
            errs.append(f'still_unsafe_unknown_post:{c}={post_missing[c]["unsafe_unknown"]}')
    # 4) users mixed: no missing account_id
    if MIXED_USERS in pre_counts:
        if post_missing[MIXED_USERS]['missing_account_id'] != 0:
            errs.append(f'users_still_missing_account_id={post_missing[MIXED_USERS]["missing_account_id"]}')

    verdict = 'SLC_G_COMMIT_APPLIED_SAFE' if not errs else 'FAILED_SAFE_POST_VERIFICATION'

    # ---- WRITE MIGRATION APPLIED MARKER FILE ----
    marker_file_payload = {
        'task_origin':'SLC-G-COMMIT-A','version':'v1',
        'migration_id': migration_id,
        'applied_at_utc': datetime.now(timezone.utc).isoformat(),
        'migration_applied': verdict == 'SLC_G_COMMIT_APPLIED_SAFE',
        'route_patch_applied': False,
        'second_server_opening_allowed': False,
        'feature_flag_enabled': False,
        'legacy_fallback_removed': False,
        'phase_11_executed': False,
        'verdict': verdict,
        'write_log': write_log,
        'pre_counts': pre_counts,'post_counts': post_counts,
        'pre_missing': pre_missing,'post_missing': post_missing,
        'af2n_pre': af2n_pre, 'af2n_post': af2n_post,
        'backup_root': str(backup_root),
        'backup_manifest_sha256': backup_manifest['manifest_sha256'],
        'rollback_script': '/app/backend/scripts/rollback_slc_g_commit_a.py',
        'errors': errs,
    }
    MIGRATION_MARKER_FILE.write_text(json.dumps(marker_file_payload, indent=2, default=str))
    RESULT.write_text(json.dumps(marker_file_payload, indent=2, default=str))

    total_docs_modified = sum(v['server_id_set_modified'] + v['account_id_set_modified'] for v in write_log.values())
    print(f'[apply_slc_g_commit_a] verdict={verdict}')
    print(f'  migration_id={migration_id}')
    print(f'  total_docs_modified={total_docs_modified}')
    for c, w in write_log.items():
        print(f'  {c}: sid_set={w["server_id_set_modified"]} aid_set={w["account_id_set_modified"]}')
    if errs:
        for e in errs: print(f'  ERR: {e}')
    print(f'  backup_root={backup_root}')
    return 0 if verdict == 'SLC_G_COMMIT_APPLIED_SAFE' else 2

if __name__ == '__main__':
    sys.exit(main())
