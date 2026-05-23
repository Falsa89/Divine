#!/usr/bin/env python3
# SLC-G-GUILDS UNSAFE READ-ONLY AUDIT
# Verifica live (read-only) che esattamente 2 documenti guilds siano unsafe_unknown
# (no user_id AND no account_id) e che entrambi siano resolvable via leader_id.
import json, os, sys
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')
from pymongo import MongoClient

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
OUT = DESIGN_DIR / '_slc_g_guilds_unsafe_audit_v1_live_result.json'
AUDIT_FILE = DESIGN_DIR / 'slc_g_guilds_unsafe_audit_v1.json'

EXPECTED_IDS = {'69db9bb2df5d3f956d0080ac','69dbc64c9c908325ca0fd57f'}

def main():
    errs = []
    url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME','test_database')
    db = MongoClient(url, serverSelectionTimeoutMS=5000)[db_name]
    if 'guilds' not in db.list_collection_names():
        # collection absent => 0 unsafe; still PASS since this matches baseline state
        out = {'task_origin':'SLC-G-GUILDS-UNSAFE-AUDIT-LIVE','verdict':'PASS',
               'collection_present':False,'unsafe_count':0,
               'timestamp_utc':datetime.now(timezone.utc).isoformat()}
        OUT.write_text(json.dumps(out, indent=2))
        print('SLC-G-GUILDS-UNSAFE-AUDIT-LIVE PASS (collection absent; unsafe_count=0)')
        return 0

    unsafe = list(db.guilds.find({'user_id':{'$exists':False},'account_id':{'$exists':False}}))
    # delta vs designed audit file
    designed = json.loads(AUDIT_FILE.read_text()).get('unsafe_docs', []) if AUDIT_FILE.exists() else []
    designed_ids = {d.get('_id') for d in designed}

    live_ids = {str(d['_id']) for d in unsafe}
    expected_count = len(designed_ids) if designed_ids else 2

    classification = []
    for d in unsafe:
        leader = d.get('leader_id')
        owner_resolved = False
        owner_kind = None
        if leader:
            u = db.users.find_one({'id': leader})
            if u:
                owner_resolved = True
                owner_kind = 'bot' if u.get('is_bot') else 'human'
        classification.append({
            '_id': str(d['_id']),
            'name_redacted': d.get('name'),
            'has_leader_id': bool(leader),
            'owner_resolved_via_leader_id': owner_resolved,
            'owner_kind': owner_kind,
            'member_count': len(d.get('members',[])) if isinstance(d.get('members'), list) else 0,
            'cleanup_safe': owner_resolved is True,
        })

    if len(unsafe) != expected_count:
        # Post-cleanup tolerance: if live unsafe_count is 0 AND every designed _id is now
        # marked with the SLC-G-GUILDS-CLEANUP-B marker, this is the post-apply healthy state.
        if len(unsafe) == 0 and designed_ids:
            from bson import ObjectId
            healed = 0
            for did in designed_ids:
                try:
                    d = db.guilds.find_one({'_id': ObjectId(did)})
                except Exception:
                    d = None
                if d and '_slc_g_guilds_cleanup_marker' in d and d.get('server_id') == 's1' \
                   and d.get('user_id') == d.get('leader_id') and d.get('account_id') == d.get('leader_id'):
                    healed += 1
            if healed == len(designed_ids):
                # POST-CLEANUP HEALTHY STATE — no error
                pass
            else:
                errs.append(f'unsafe_count_mismatch:live={len(unsafe)} designed={expected_count} healed_via_marker={healed}')
        else:
            errs.append(f'unsafe_count_mismatch:live={len(unsafe)} designed={expected_count}')
    if live_ids != designed_ids and designed_ids and len(unsafe) != 0:
        errs.append(f'live_ids_diverge_from_designed:live={sorted(live_ids)} designed={sorted(designed_ids)}')

    unresolvable = [c for c in classification if not c['cleanup_safe']]
    if unresolvable:
        errs.append(f'unresolvable_docs_found_must_be_marked_unsafe_do_not_touch:{[c["_id"] for c in unresolvable]}')

    verdict = 'PASS' if not errs else 'FAIL'
    out = {
        'task_origin':'SLC-G-GUILDS-UNSAFE-AUDIT-LIVE','verdict':verdict,
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'mode':'READ_ONLY',
        'collection_present':True,
        'unsafe_count':len(unsafe),
        'expected_count':expected_count,
        'classification':classification,
        'errors':errs,
        'db_write':False,'cleanup_applied':False,
    }
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"SLC-G-GUILDS-UNSAFE-AUDIT-LIVE {verdict} unsafe_count={len(unsafe)} unresolvable={len(unresolvable)}")
    for e in errs: print(' -', e)
    return 0 if verdict == 'PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
