#!/usr/bin/env python3
# SLC-G COMMIT-A ROLLBACK SCRIPT (GATED)
# Inverte la migrazione SLC-G commit-a: $unset di server_id/account_id/_slc_g_commit_marker
# SOLO dove _slc_g_commit_marker.migration_id corrisponde a quello specifico.
# Gating: env SLC_G_COMMIT_A_ROLLBACK_APPROVAL=true E env SLC_G_COMMIT_A_ROLLBACK_MIGRATION_ID=<id>.
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')
from pymongo import MongoClient

ROOT = Path('/app')
REPORTS_DIR = ROOT / 'backend/reports'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
RESULT = REPORTS_DIR / 'slc_g_commit_a_rollback_result.json'
MARKER_FIELD = '_slc_g_commit_marker'
ROLLBACK_APPROVAL_ENV = 'SLC_G_COMMIT_A_ROLLBACK_APPROVAL'
MIGRATION_ID_ENV = 'SLC_G_COMMIT_A_ROLLBACK_MIGRATION_ID'

COLLECTIONS = ['user_heroes','teams','inventory','story_progress','guilds',
               'user_affinity_state','gift_transaction_ledger','user_gift_inventory','users']

def main():
    if os.environ.get(ROLLBACK_APPROVAL_ENV,'').lower() != 'true':
        out = {'task_origin':'SLC-G-COMMIT-A-ROLLBACK','verdict':'ROLLBACK_NOT_APPROVED',
               'reason':f'missing env {ROLLBACK_APPROVAL_ENV}=true','timestamp_utc':datetime.now(timezone.utc).isoformat()}
        RESULT.write_text(json.dumps(out, indent=2))
        print('ROLLBACK_NOT_APPROVED')
        return 2
    mig_id = os.environ.get(MIGRATION_ID_ENV,'').strip()
    if not mig_id:
        out = {'task_origin':'SLC-G-COMMIT-A-ROLLBACK','verdict':'ROLLBACK_NOT_APPROVED',
               'reason':f'missing env {MIGRATION_ID_ENV}','timestamp_utc':datetime.now(timezone.utc).isoformat()}
        RESULT.write_text(json.dumps(out, indent=2))
        print('ROLLBACK_NOT_APPROVED: migration_id missing')
        return 2
    url = os.environ['MONGO_URL']
    db = MongoClient(url, serverSelectionTimeoutMS=5000)[os.environ.get('DB_NAME','test_database')]
    res = {}
    for c in COLLECTIONS:
        if c not in db.list_collection_names(): continue
        r = db[c].update_many({f'{MARKER_FIELD}.migration_id': mig_id},
                              {'$unset': {'server_id':'','account_id':'',MARKER_FIELD:''}})
        res[c] = {'matched':r.matched_count,'modified':r.modified_count}
    out = {'task_origin':'SLC-G-COMMIT-A-ROLLBACK','verdict':'ROLLBACK_APPLIED',
           'migration_id':mig_id,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'results':res}
    RESULT.write_text(json.dumps(out, indent=2))
    print(f'ROLLBACK_APPLIED migration_id={mig_id}')
    for c, r in res.items(): print(f'  {c}: matched={r["matched"]} modified={r["modified"]}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
