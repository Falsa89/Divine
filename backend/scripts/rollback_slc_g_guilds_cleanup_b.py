#!/usr/bin/env python3
# SLC-G-GUILDS-CLEANUP-B ROLLBACK SCRIPT (GATED)
# Inverte la micro-bonifica: $unset dei campi aggiunti SOLO sui doc col marker.
# Gating: richiede env SLC_G_GUILDS_UNSAFE_CLEANUP_ROLLBACK_APPROVAL=true.
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')
from pymongo import MongoClient

ROOT = Path('/app')
REPORTS_DIR = ROOT / 'backend/reports'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
RESULT = REPORTS_DIR / 'slc_g_guilds_cleanup_b_rollback_result.json'

MARKER_FIELD = '_slc_g_guilds_cleanup_marker'
ROLLBACK_MARKER_ENV = 'SLC_G_GUILDS_UNSAFE_CLEANUP_ROLLBACK_APPROVAL'
ALLOWED_IDS = {'69db9bb2df5d3f956d0080ac','69dbc64c9c908325ca0fd57f'}

def main():
    if os.environ.get(ROLLBACK_MARKER_ENV,'').lower() != 'true':
        print(f'ROLLBACK_NOT_APPROVED: missing env {ROLLBACK_MARKER_ENV}=true')
        RESULT.write_text(json.dumps({
            'task_origin':'SLC-G-GUILDS-CLEANUP-B-ROLLBACK',
            'verdict':'ROLLBACK_NOT_APPROVED',
            'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        }, indent=2))
        return 2
    url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME','test_database')
    db = MongoClient(url, serverSelectionTimeoutMS=5000)[db_name]
    # find marked docs limited to allowed _id set
    marked = list(db.guilds.find({MARKER_FIELD:{'$exists':True}}))
    res = []
    for d in marked:
        sid = str(d['_id'])
        if sid not in ALLOWED_IDS:
            res.append({'_id':sid,'skipped':True,'reason':'_id not in allowed rollback set'})
            continue
        r = db.guilds.update_one(
            {'_id': d['_id'], MARKER_FIELD:{'$exists':True}},
            {'$unset': {'user_id':'','account_id':'','server_id':'',MARKER_FIELD:'','_slc_g_guilds_cleanup_classification':''}}
        )
        res.append({'_id':sid,'matched':r.matched_count,'modified':r.modified_count})
    out = {
        'task_origin':'SLC-G-GUILDS-CLEANUP-B-ROLLBACK','version':'v1',
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'verdict':'ROLLBACK_APPLIED','results':res,
    }
    RESULT.write_text(json.dumps(out, indent=2))
    print(f'ROLLBACK_APPLIED entries={len(res)}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
