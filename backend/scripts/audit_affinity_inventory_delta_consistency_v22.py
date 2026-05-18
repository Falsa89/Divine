#!/usr/bin/env python3
"""V22 — Inventory/Affinity Delta Consistency Audit.

Read-only DB audit. No mutations.
"""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient

OUT = Path('/app/data/design/affinity/affinity_inventory_delta_consistency_v22_report.json')
NOW = datetime.now(timezone.utc)


def main():
    db = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']
    coll = db['gift_transaction_ledger']
    ugi = db['user_gift_inventory']
    uas = db['user_affinity_state']

    fails = []
    checks = {}

    # 1. no negative inventory
    checks['negative_inventory_count'] = ugi.count_documents({'quantity': {'$lt': 0}})
    if checks['negative_inventory_count'] > 0: fails.append('negative_inventory')

    # 2. no Borea in ledger / inventory / state
    checks['borea_in_ledger'] = coll.count_documents({'hero_id': {'$in':['borea','greek_borea','primordial_gaia']}})
    checks['borea_in_affinity_state'] = uas.count_documents({'hero_id': {'$in':['borea','greek_borea','primordial_gaia']}})
    if checks['borea_in_ledger'] > 0: fails.append('borea_in_ledger')
    if checks['borea_in_affinity_state'] > 0: fails.append('borea_in_affinity_state')

    # 3. transaction_id uniqueness
    dup_tx = list(coll.aggregate([
        {'$group': {'_id': '$tx_id', 'cnt': {'$sum': 1}}},
        {'$match': {'cnt': {'$gt': 1}, '_id': {'$ne': None}}}, {'$limit': 5},
    ]))
    checks['duplicate_tx_ids'] = len(dup_tx)
    if dup_tx: fails.append('duplicate_tx_ids')

    # 4. idempotency uniqueness per (user_id, idempotency_key)
    dup_idem = list(coll.aggregate([
        {'$group': {'_id': {'user_id':'$user_id','key':'$idempotency_key'}, 'cnt':{'$sum':1}}},
        {'$match': {'cnt': {'$gt': 1}}}, {'$limit': 5},
    ]))
    checks['duplicate_idempotency_groups'] = len(dup_idem)
    if dup_idem: fails.append('duplicate_idempotency')

    # 5. per-user sum of inventory-mutating ledger qty == sum of affinity_points awarded
    #    Sample per user_id (limit 30 stage4_qa_*).
    per_user = list(coll.aggregate([
        {'$match': {'inventory_mutated': True, 'user_id': {'$regex': '^stage[34]_qa_'}}},
        {'$group': {
            '_id': {'user_id':'$user_id','hero_id':'$hero_id'},
            'qty_mut': {'$sum': '$quantity'},
        }},
        {'$limit': 60},
    ]))
    per_user_check = []
    delta_mismatch = 0
    for r in per_user:
        uid = r['_id']['user_id']; hid = r['_id']['hero_id']
        qty_mut = r['qty_mut']
        st = uas.find_one({'user_id':uid,'hero_id':hid}) or {}
        aff = st.get('affinity_points', 0)
        total_gifts = st.get('total_gifts_given', 0)
        ok = (qty_mut == aff) and (qty_mut == total_gifts)
        per_user_check.append({'user_id':uid,'hero_id':hid,'qty_mut':qty_mut,'affinity_points':aff,'total_gifts_given':total_gifts,'ok':ok})
        if not ok: delta_mismatch += 1
    checks['delta_mismatch_users'] = delta_mismatch
    checks['delta_audit_sample_size'] = len(per_user_check)
    if delta_mismatch > 0: fails.append('inv_aff_delta_mismatch')

    # 6. canary markers consistent (every applied_inventory_live row has canary=True and not borea)
    weird = coll.count_documents({
        'status': 'applied_inventory_live',
        '$or': [{'canary': {'$ne': True}}, {'hero_id': {'$in':['borea','greek_borea','primordial_gaia']}}]
    })
    checks['inconsistent_canary_markers'] = weird
    if weird > 0: fails.append('inconsistent_canary_markers')

    # 7. no non-allowlist successful spend (proxy: every ledger row's user_id matches stage1/2/3/4_qa_* or canary)
    bad_uids = list(coll.aggregate([
        {'$match': {'status': {'$in': ['applied_canary','applied_inventory_live']},
                     'user_id': {'$not': {'$regex': '^(stage[1-4]_qa_|user_canary_)'}}}},
        {'$limit': 5},
    ]))
    checks['non_allowlist_success_count'] = len(bad_uids)
    if bad_uids: fails.append('non_allowlist_success')

    # 8. no orphan Stage4 seed records pointing to non-existent users (informational; we can't fully check)
    orphan_inv = ugi.count_documents({'metadata.seed_task': 'V21_STAGE4'})
    checks['stage4_seed_inv_rows'] = orphan_inv

    # 9. all idempotent replays produced same tx_id (one ledger row per (user_id,key))
    grouped = list(coll.aggregate([
        {'$group': {'_id': {'u':'$user_id','k':'$idempotency_key'}, 'tx_ids': {'$addToSet':'$tx_id'}, 'cnt':{'$sum':1}}},
        {'$match': {'cnt': {'$gt': 0}, '$expr': {'$gt': [{'$size':'$tx_ids'}, 1]}}},
        {'$limit': 5},
    ]))
    checks['idempotency_distinct_tx_ids'] = len(grouped)
    if grouped: fails.append('idempotency_distinct_tx_ids')

    overall = (len(fails) == 0)
    out_doc = {
        'report_id': 'affinity_inventory_delta_consistency_v22_report',
        'task_origin': 'V22-AF2N-DELTA-AUDIT',
        'generated_at_utc': NOW.isoformat().replace('+00:00','Z'),
        'checks': checks,
        'per_user_check_sample': per_user_check[:20],
        'fails': fails,
        'overall_status': 'PASS' if overall else 'FAIL',
        'safety_invariants': [
            'read-only audit', 'no DB mutation', 'never exposes Borea data',
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out_doc, indent=2, default=str))
    print(f'V22-DELTA-AUDIT {out_doc["overall_status"]} fails={fails}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
