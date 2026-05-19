#!/usr/bin/env python3
"""V23 — Delta audit (refreshed sample after Redis switch)."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient

OUT = Path('/app/data/design/affinity/affinity_inventory_delta_consistency_v23_report.json')


def main():
    NOW = datetime.now(timezone.utc)
    db = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']
    coll = db['gift_transaction_ledger']
    ugi = db['user_gift_inventory']
    uas = db['user_affinity_state']
    fails = []; checks = {}
    checks['negative_inventory_count'] = ugi.count_documents({'quantity': {'$lt': 0}})
    if checks['negative_inventory_count'] > 0: fails.append('neg_inv')
    checks['borea_in_ledger'] = coll.count_documents({'hero_id': {'$in':['borea','greek_borea','primordial_gaia']}})
    checks['borea_in_affinity_state'] = uas.count_documents({'hero_id': {'$in':['borea','greek_borea','primordial_gaia']}})
    if checks['borea_in_ledger'] or checks['borea_in_affinity_state']: fails.append('borea_in_db')
    dup_tx = list(coll.aggregate([
        {'$group': {'_id':'$tx_id','c':{'$sum':1}}},
        {'$match':{'c':{'$gt':1},'_id':{'$ne':None}}},{'$limit':5}]))
    checks['duplicate_tx_ids'] = len(dup_tx)
    if dup_tx: fails.append('dup_tx')
    dup_idem = list(coll.aggregate([
        {'$group':{'_id':{'u':'$user_id','k':'$idempotency_key'},'c':{'$sum':1}}},
        {'$match':{'c':{'$gt':1}}},{'$limit':5}]))
    checks['duplicate_idempotency_groups'] = len(dup_idem)
    if dup_idem: fails.append('dup_idem')
    per_user = list(coll.aggregate([
        {'$match':{'inventory_mutated':True,'user_id':{'$regex':'^stage[34]_qa_'}}},
        {'$group':{'_id':{'u':'$user_id','h':'$hero_id'},'qty':{'$sum':'$quantity'}}},
        {'$limit':80}]))
    delta_mismatch = 0; per_user_check = []
    for r in per_user:
        uid = r['_id']['u']; hid = r['_id']['h']; qty = r['qty']
        st = uas.find_one({'user_id':uid,'hero_id':hid}) or {}
        aff = st.get('affinity_points',0); tot = st.get('total_gifts_given',0)
        ok = (qty == aff) and (qty == tot)
        per_user_check.append({'user_id':uid,'hero_id':hid,'qty_mut':qty,'aff':aff,'total':tot,'ok':ok})
        if not ok: delta_mismatch += 1
    checks['delta_mismatch_users'] = delta_mismatch
    checks['delta_audit_sample_size'] = len(per_user_check)
    if delta_mismatch: fails.append('inv_aff_delta_mismatch')
    bad_uids = list(coll.aggregate([
        {'$match':{'status':{'$in':['applied_canary','applied_inventory_live']},
                    'user_id':{'$not':{'$regex':'^(stage[1-4]_qa_|user_canary_)'}}}},
        {'$limit':5}]))
    checks['non_allowlist_success_count'] = len(bad_uids)
    if bad_uids: fails.append('non_allowlist_success')
    overall = (len(fails) == 0)
    out_doc = {
        'report_id':'affinity_inventory_delta_consistency_v23_report',
        'task_origin':'V23-AF2N-DELTA-AUDIT-POST-REDIS-SWITCH',
        'generated_at_utc': NOW.isoformat().replace('+00:00','Z'),
        'checks': checks,
        'per_user_check_sample': per_user_check[:20],
        'fails': fails,
        'overall_status': 'PASS' if overall else 'FAIL',
        'safety_invariants': ['read-only audit','no DB mutation','no Borea data leak'],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out_doc, indent=2, default=str))
    print(f'V23-DELTA-AUDIT {out_doc["overall_status"]} fails={fails}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
