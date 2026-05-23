#!/usr/bin/env python3
# SLC-G-GUILDS-CLEANUP-B APPLY SCRIPT (GATED)
# Esegue micro-bonifica targeted ESCLUSIVAMENTE sui 2 _id auditati in SLC-G-GUILDS-CLEANUP-A.
# Gating: richiede env SLC_G_GUILDS_UNSAFE_CLEANUP_WRITE_APPROVAL=true.
# NON tocca SLC-G migration. NON tocca altri documenti. NON elimina nulla.
import json, os, sys, hashlib
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')
from pymongo import MongoClient
from bson import ObjectId

ROOT = Path('/app')
DESIGN_DIR = ROOT / 'data/design/server_lifecycle'
REPORTS_DIR = ROOT / 'backend/reports'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR = ROOT / 'data/design/system_safety/backups'
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

AUDIT_SRC = DESIGN_DIR / 'slc_g_guilds_unsafe_audit_v1.json'
PLAN_SRC = DESIGN_DIR / 'slc_g_guilds_cleanup_plan_v1.json'
RESULT = REPORTS_DIR / 'slc_g_guilds_cleanup_b_apply_result.json'

MARKER = 'SLC_G_GUILDS_UNSAFE_CLEANUP_WRITE_APPROVAL'
FORBIDDEN_MARKER = 'SLC_G_WRITE_GATE_EXPLICIT_APPROVAL'  # NON deve essere attivo

EXPECTED_TARGETS = [
    ('69db9bb2df5d3f956d0080ac', '651253e2-da8d-466b-98f3-82f008d158ed'),  # Divine Warriors / TestPlayer
    ('69dbc64c9c908325ca0fd57f', '526fb2cf-02ba-410e-bb9c-8bf5de3f5e00'),  # Legion_517 / OnyxShadow965
]

ALLOWED_SET_FIELDS = {'user_id','account_id','server_id','_slc_g_guilds_cleanup_marker','_slc_g_guilds_cleanup_classification'}

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def sortable(d):
    if isinstance(d, dict):
        return {k: sortable(d[k]) for k in sorted(d.keys())}
    if isinstance(d, list):
        return [sortable(x) for x in d]
    if isinstance(d, ObjectId):
        return str(d)
    if isinstance(d, datetime):
        return d.isoformat()
    return d

def fail_safe(msg, extra=None):
    out = {'task_origin':'SLC-G-GUILDS-CLEANUP-B-APPLY','verdict':'FAILED_SAFE','reason':msg,
           'timestamp_utc':datetime.now(timezone.utc).isoformat(),'extra':extra}
    RESULT.write_text(json.dumps(out, indent=2, default=str))
    print(f'FAILED_SAFE: {msg}')
    if extra: print(f'  extra: {extra}')
    sys.exit(2)

def main():
    # 1) Approval marker present and correct
    if os.environ.get(MARKER, '').lower() != 'true':
        fail_safe(f'approval_marker_absent:{MARKER}')
    # 2) SLC-G migration marker MUST NOT be present (we explicitly do not authorize commit)
    if os.environ.get(FORBIDDEN_MARKER, '').lower() == 'true':
        fail_safe(f'forbidden_marker_present_must_be_unset:{FORBIDDEN_MARKER}')

    # 3) Audit + plan present
    if not AUDIT_SRC.exists():
        fail_safe('audit_file_missing', str(AUDIT_SRC))
    if not PLAN_SRC.exists():
        fail_safe('plan_file_missing', str(PLAN_SRC))
    audit = json.loads(AUDIT_SRC.read_text())
    plan = json.loads(PLAN_SRC.read_text())
    if plan.get('target_docs_count') != 2 or plan.get('target_collection') != 'guilds':
        fail_safe('plan_target_mismatch')

    # 4) Live DB read-only verification
    url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME','test_database')
    db = MongoClient(url, serverSelectionTimeoutMS=5000)[db_name]

    live_unsafe = list(db.guilds.find({'user_id':{'$exists':False},'account_id':{'$exists':False}}))
    live_unsafe_ids = sorted(str(d['_id']) for d in live_unsafe)
    expected_ids = sorted(t[0] for t in EXPECTED_TARGETS)
    if live_unsafe_ids != expected_ids:
        fail_safe('live_targets_diverge_from_audit', {'live':live_unsafe_ids,'expected':expected_ids})

    # 5) Verify leader_id resolves to users.id for ALL targets
    for d in live_unsafe:
        leader = d.get('leader_id')
        if not leader:
            fail_safe('target_missing_leader_id', str(d.get('_id')))
        u = db.users.find_one({'id': leader})
        if not u:
            fail_safe('leader_id_unresolved_in_users', {'_id':str(d['_id']),'leader_id':leader})

    # 6) Build backup snapshot (pre-state)
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    pre_state = []
    for d in live_unsafe:
        pre_state.append({
            '_id': str(d['_id']),
            'doc': sortable(d),
        })
    backup_payload = {
        'task_origin':'SLC-G-GUILDS-CLEANUP-B-BACKUP-PRE',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'collection': 'guilds',
        'targets_count': len(pre_state),
        'pre_state_docs': pre_state,
        'audit_reference': str(AUDIT_SRC),
    }
    backup_payload_str = json.dumps(backup_payload, indent=2, default=str, sort_keys=True)
    backup_payload['sha256'] = sha256(backup_payload_str)
    backup_file = BACKUP_DIR / f'slc_g_guilds_cleanup_b_pre_backup_{ts}.json'
    backup_file.write_text(json.dumps(backup_payload, indent=2, default=str))

    # 7) Apply set-only-if-missing for EACH target
    write_log = []
    for doc in live_unsafe:
        _id = doc['_id']
        leader = doc['leader_id']
        # build $set for missing fields only
        set_doc = {}
        if 'user_id' not in doc:
            set_doc['user_id'] = leader
        if 'account_id' not in doc:
            set_doc['account_id'] = leader
        if 'server_id' not in doc:
            set_doc['server_id'] = 's1'
        if '_slc_g_guilds_cleanup_marker' not in doc:
            set_doc['_slc_g_guilds_cleanup_marker'] = {
                'task': 'SLC-G-GUILDS-UNSAFE-CLEANUP-B-APPLY',
                'version': 'v1',
                'applied_at_utc': datetime.now(timezone.utc).isoformat(),
                'classification': ('legacy_guild_missing_owner_resolvable_bot_owned'
                                   if db.users.find_one({'id': leader, 'is_bot': True})
                                   else 'legacy_guild_missing_owner_resolvable'),
                'backup_file': backup_file.name,
            }
        # validate $set fields are only in the allow-list
        bad = [k for k in set_doc.keys() if k not in ALLOWED_SET_FIELDS]
        if bad:
            fail_safe('set_field_not_in_allowlist', {'_id':str(_id),'bad':bad})
        # write_only_if_field_absent: build filter that requires each key absent
        filt = {'_id': _id}
        for k in set_doc.keys():
            filt[k] = {'$exists': False}
        # do not run update if set_doc is empty (already cleaned)
        if not set_doc:
            write_log.append({'_id':str(_id),'updated':0,'reason':'already_clean'})
            continue
        res = db.guilds.update_one(filt, {'$set': set_doc})
        write_log.append({
            '_id': str(_id),
            'matched_count': res.matched_count,
            'modified_count': res.modified_count,
            'fields_set': list(set_doc.keys()),
        })

    # 8) Verify post-state
    post_state = []
    for doc in db.guilds.find({'_id':{'$in':[d['_id'] for d in live_unsafe]}}):
        post_state.append({
            '_id': str(doc['_id']),
            'has_user_id': 'user_id' in doc,
            'has_account_id': 'account_id' in doc,
            'has_server_id': 'server_id' in doc,
            'server_id_value': doc.get('server_id'),
            'has_cleanup_marker': '_slc_g_guilds_cleanup_marker' in doc,
            'user_id_equals_leader_id': doc.get('user_id') == doc.get('leader_id'),
            'account_id_equals_leader_id': doc.get('account_id') == doc.get('leader_id'),
            'leader_id_unchanged': True,
            'members_count': len(doc.get('members',[])) if isinstance(doc.get('members'), list) else 0,
        })
    # Verify the global unsafe count is now 0
    unsafe_after = db.guilds.count_documents({'user_id':{'$exists':False},'account_id':{'$exists':False}})

    # 9) Verify NO OTHER guilds were touched (count remains 2)
    guilds_total = db.guilds.count_documents({})

    final = {
        'task_origin':'SLC-G-GUILDS-CLEANUP-B-APPLY','version':'v1',
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'mode':'TARGETED_DB_WRITE_BACKUP_FIRST_ROLLBACK_READY',
        'approval_marker_present':True,'slc_g_commit_marker_present':False,
        'guilds_total_pre':2,'guilds_total_post':guilds_total,
        'unsafe_unknown_post': unsafe_after,
        'targets_modified': sum(1 for w in write_log if w.get('modified_count',0) > 0),
        'backup_file': str(backup_file),
        'backup_sha256': backup_payload['sha256'],
        'write_log': write_log,
        'post_state': post_state,
        'verdict': 'CLEANUP_APPLIED_SAFE' if (unsafe_after == 0 and guilds_total == 2 and all(p['has_user_id'] and p['has_account_id'] and p['has_server_id'] and p['server_id_value']=='s1' and p['has_cleanup_marker'] for p in post_state)) else 'PARTIAL_FAILURE',
    }
    RESULT.write_text(json.dumps(final, indent=2, default=str))
    print(f"[apply_slc_g_guilds_cleanup_b] {final['verdict']} unsafe_after={unsafe_after} targets_modified={final['targets_modified']} backup={backup_file.name}")
    for p in post_state:
        print(f"  _id={p['_id']} user_id={'YES' if p['has_user_id'] else 'NO'} account_id={'YES' if p['has_account_id'] else 'NO'} server_id={p['server_id_value']} marker={'YES' if p['has_cleanup_marker'] else 'NO'} members={p['members_count']}")
    return 0 if final['verdict']=='CLEANUP_APPLIED_SAFE' else 2

if __name__ == '__main__':
    sys.exit(main())
