#!/usr/bin/env python3
# SLC-G COMMIT-A POST-APPLY VALIDATOR (READ-ONLY)
# Conferma che la migrazione SLC-G sia stata applicata in modo sicuro.
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')
from pymongo import MongoClient

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
SAFETY_DIR = ROOT / 'data/design/system_safety'
MARKER_FILE = SAFETY_DIR / 'slc_g_default_s1_migration_apply_result_v1.json'
OUT = DESIGN_DIR / '_slc_g_commit_a_post_apply_v1_result.json'

SERVER_BOUND_PRESENT = ['user_heroes','teams','inventory','story_progress','guilds',
                       'user_affinity_state','gift_transaction_ledger','user_gift_inventory']
MIXED = ['users']
AF2N = ['user_gift_inventory','gift_transaction_ledger','user_affinity_state']

def main():
    errs = []
    if not MARKER_FILE.exists():
        errs.append('migration_marker_file_missing')
        OUT.write_text(json.dumps({'verdict':'FAIL','errors':errs}, indent=2))
        print('SLC-G-COMMIT-A-POST-APPLY FAIL marker_file_missing')
        return 1
    m = json.loads(MARKER_FILE.read_text())
    if not m.get('migration_applied'):
        errs.append('migration_applied_not_true_in_marker')
    if m.get('route_patch_applied') is not False:
        errs.append('route_patch_applied_must_be_false')
    if m.get('second_server_opening_allowed') is not False:
        errs.append('second_server_opening_allowed_must_be_false')
    if m.get('feature_flag_enabled') is not False:
        errs.append('feature_flag_enabled_must_be_false')
    if m.get('phase_11_executed') is not False:
        errs.append('phase_11_executed_must_be_false')

    url = os.environ['MONGO_URL']
    db = MongoClient(url, serverSelectionTimeoutMS=5000)[os.environ.get('DB_NAME','test_database')]
    present = set(db.list_collection_names())

    # AF2-N invariants vs marker file
    for c in AF2N:
        if c in present:
            live = db[c].count_documents({})
            pre = (m.get('af2n_pre') or {}).get(c)
            if pre is not None and live != pre:
                errs.append(f'af2n_drift:{c}:pre={pre},live={live}')

    # Server-bound: 0 missing server_id
    per_coll_status = {}
    for c in SERVER_BOUND_PRESENT:
        if c not in present: continue
        miss = db[c].count_documents({'server_id':{'$exists':False}})
        unsafe = db[c].count_documents({'user_id':{'$exists':False},'account_id':{'$exists':False}})
        miss_aid = db[c].count_documents({'account_id':{'$exists':False},'user_id':{'$exists':True}})
        per_coll_status[c] = {'missing_server_id':miss,'unsafe_unknown':unsafe,'missing_aid_with_uid':miss_aid}
        if miss != 0: errs.append(f'{c}:missing_server_id_post:{miss}')
        if unsafe != 0: errs.append(f'{c}:unsafe_unknown_post:{unsafe}')
        if miss_aid != 0: errs.append(f'{c}:account_id_still_missing_with_user_id:{miss_aid}')

    # Users: account_id present on all
    if 'users' in present:
        miss_aid_users = db['users'].count_documents({'account_id':{'$exists':False}})
        if miss_aid_users != 0: errs.append(f'users:missing_account_id_post:{miss_aid_users}')

    # Guild cleanup B markers still present and valid (no regression)
    g_marker = db.guilds.count_documents({'_slc_g_guilds_cleanup_marker':{'$exists':True}})
    if g_marker != 2:
        errs.append(f'guilds_cleanup_b_marker_count_must_be_2_got:{g_marker}')

    verdict = 'PASS' if not errs else 'FAIL'
    out = {'task_origin':'SLC-G-COMMIT-A-POST-APPLY','timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'verdict':verdict,'errors':errs,'migration_id':m.get('migration_id'),
           'per_coll_status':per_coll_status}
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f'SLC-G-COMMIT-A-POST-APPLY {verdict} errors={len(errs)}')
    for e in errs: print(' -', e)
    return 0 if verdict=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
