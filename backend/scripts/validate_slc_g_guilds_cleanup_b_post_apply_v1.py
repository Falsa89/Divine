#!/usr/bin/env python3
# SLC-G-GUILDS-CLEANUP-B POST-APPLY VERIFICATION (READ-ONLY)
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')
from pymongo import MongoClient

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_g_guilds_cleanup_b_post_apply_v1_result.json'

EXPECTED_IDS = {'69db9bb2df5d3f956d0080ac','69dbc64c9c908325ca0fd57f'}

def main():
    errs = []
    url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME','test_database')
    db = MongoClient(url, serverSelectionTimeoutMS=5000)[db_name]

    # Check: unsafe_unknown count is now 0
    unsafe = db.guilds.count_documents({'user_id':{'$exists':False},'account_id':{'$exists':False}})
    if unsafe != 0:
        errs.append(f'unsafe_unknown_must_be_0_got:{unsafe}')

    # Check: total guilds unchanged at 2
    total = db.guilds.count_documents({})
    if total != 2:
        errs.append(f'total_guilds_must_be_2_got:{total}')

    # Check: each target now has user_id, account_id, server_id=s1, marker
    summary = []
    for sid in EXPECTED_IDS:
        from bson import ObjectId
        d = db.guilds.find_one({'_id': ObjectId(sid)})
        if not d:
            errs.append(f'target_doc_missing:{sid}')
            continue
        info = {
            '_id': sid,
            'user_id_present': 'user_id' in d,
            'account_id_present': 'account_id' in d,
            'server_id_value': d.get('server_id'),
            'has_marker': '_slc_g_guilds_cleanup_marker' in d,
            'user_id_equals_leader_id': d.get('user_id') == d.get('leader_id'),
            'account_id_equals_leader_id': d.get('account_id') == d.get('leader_id'),
            'leader_id': d.get('leader_id'),
        }
        summary.append(info)
        if not info['user_id_present']: errs.append(f'{sid}:user_id_missing')
        if not info['account_id_present']: errs.append(f'{sid}:account_id_missing')
        if info['server_id_value'] != 's1': errs.append(f'{sid}:server_id_not_s1')
        if not info['has_marker']: errs.append(f'{sid}:cleanup_marker_missing')
        if not info['user_id_equals_leader_id']: errs.append(f'{sid}:user_id_not_equal_leader_id')
        if not info['account_id_equals_leader_id']: errs.append(f'{sid}:account_id_not_equal_leader_id')

    out = {
        'task_origin':'SLC-G-GUILDS-CLEANUP-B-POST-APPLY',
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'mode':'READ_ONLY_POST_APPLY_VERIFICATION',
        'unsafe_unknown_count': unsafe,
        'total_guilds': total,
        'summary': summary,
        'errors': errs,
        'verdict':'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"SLC-G-GUILDS-CLEANUP-B-POST-APPLY {out['verdict']} unsafe={unsafe} total={total} errors={len(errs)}")
    for e in errs: print(' -', e)
    return 0 if out['verdict']=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
