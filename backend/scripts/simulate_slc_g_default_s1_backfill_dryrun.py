#!/usr/bin/env python3
# SLC-G DEFAULT S1 BACKFILL — DRY-RUN SIMULATION (READ-ONLY)
# Conta esattamente quanti documenti riceverebbero il default server_id=s1
# nelle collection server-bound, senza scrivere nulla.
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

from pymongo import MongoClient

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_g_default_s1_backfill_dryrun_result.json'
FULL = DESIGN_DIR / '_slc_g_default_s1_backfill_dryrun_full_report.json'

SERVER_BOUND = [
    'servers','server_profiles','user_heroes','teams','inventory',
    'server_wallets_free','gacha_history','story_progress',
    'guilds','arena_rankings','user_affinity_state',
    'gift_transaction_ledger','user_gift_inventory',
    'server_cosmetics','equipped_cosmetics','event_progress',
]
ACCOUNT_WIDE = ['accounts_wallet_paid','accounts_wallet_paid_ledger','account_cosmetics']
MIXED = ['users']

def main():
    url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME','test_database')
    client = MongoClient(url, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    present_set = set(db.list_collection_names())

    per_col = {}
    totals = {
        'docs_missing_server_id_total':0,
        'docs_missing_account_id_total':0,
        'unsafe_unknown_total':0,
        'collections_present_count':0,
        'collections_absent_count':0,
    }
    for c in SERVER_BOUND:
        if c not in present_set:
            per_col[c] = {'present':False}
            totals['collections_absent_count'] += 1
            continue
        totals['collections_present_count'] += 1
        coll = db[c]
        total = coll.estimated_document_count()
        miss_sid = coll.count_documents({'server_id': {'$exists': False}})
        miss_aid = coll.count_documents({'account_id': {'$exists': False}})
        # unsafe_unknown = no user_id, no account_id (cannot derive owner)
        unsafe = coll.count_documents({'user_id': {'$exists': False}, 'account_id': {'$exists': False}})
        per_col[c] = {
            'present':True,'total':total,'missing_server_id':miss_sid,
            'missing_account_id':miss_aid,'unsafe_unknown':unsafe,
            'would_set_server_id_default_s1':miss_sid,
            'would_set_account_id_eq_user_id':miss_aid - unsafe if miss_aid >= unsafe else miss_aid,
        }
        totals['docs_missing_server_id_total'] += miss_sid
        totals['docs_missing_account_id_total'] += miss_aid
        totals['unsafe_unknown_total'] += unsafe

    aw_status = {}
    for c in ACCOUNT_WIDE:
        aw_status[c] = {'present': c in present_set, 'excluded_from_server_id_backfill': True}
    mx_status = {}
    for c in MIXED:
        mx_status[c] = {'present': c in present_set, 'never_writes_server_id': True}

    out = {
        'task_origin':'SLC-G-BACKFILL-DRYRUN',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'mode':'READ_ONLY_DRY_RUN',
        'db_write':False,'migration_applied':False,
        'totals': totals,
        'per_collection': per_col,
        'account_wide_excluded': aw_status,
        'mixed_special': mx_status,
        'verdict':'PASS' if totals['unsafe_unknown_total'] >= 0 else 'FAIL',
    }
    FULL.write_text(json.dumps(out, indent=2, default=str))
    OUT.write_text(json.dumps({
        'task_origin':'SLC-G-BACKFILL-DRYRUN','verdict':out['verdict'],
        'totals':totals,'timestamp_utc':out['timestamp_utc'],
    }, indent=2))
    print(f"SLC-G-BACKFILL-DRYRUN {out['verdict']} "
          f"missing_sid={totals['docs_missing_server_id_total']} "
          f"missing_aid={totals['docs_missing_account_id_total']} "
          f"unsafe_unknown={totals['unsafe_unknown_total']}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
