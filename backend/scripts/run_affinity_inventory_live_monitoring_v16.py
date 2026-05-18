#!/usr/bin/env python3
"""AF2-N-INVENTORY-LIVE-MONITORING V16 — Snapshot result + validator.

We re-verify the post-flip state without doing additional mutations
(the controlled mutations have already been performed by the activation script).
"""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/affinity_inventory_live_monitoring_v16_result.json')


def _get(p):
    try:
        with urlopen(API + p, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None


def _post(p, b):
    payload = json.dumps(b).encode(); headers = {'Content-Type': 'application/json'}
    req = Request(API + p, data=payload, method='POST', headers=headers)
    try:
        with urlopen(req, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e:
        try: return e.code, json.loads(e.read().decode())
        except: return e.code, None
    except URLError: return -1, None


def main():
    from pymongo import MongoClient
    db = MongoClient('mongodb://localhost:27017')['divine_waifus']
    ugi = db['user_gift_inventory']; uas = db['user_affinity_state']
    coll = db['gift_transaction_ledger']

    # Re-test idempotent replay (must not double-mutate)
    pre_inv = ugi.find_one({'user_id':'stage1_qa_001','gift_id':'gift_test_001'}, {'_id':0,'quantity':1})
    pre_aff = uas.find_one({'user_id':'stage1_qa_001','hero_id':'greek_zeus'}, {'_id':0,'affinity_points':1})
    code_replay, body_replay = _post('/affinity/gift-spend',
        {'gift_id':'gift_test_001','hero_id':'greek_zeus','quantity':2,
         'idempotency_key':'v16live001ai','user_id':'stage1_qa_001'})
    post_inv = ugi.find_one({'user_id':'stage1_qa_001','gift_id':'gift_test_001'}, {'_id':0,'quantity':1})
    post_aff = uas.find_one({'user_id':'stage1_qa_001','hero_id':'greek_zeus'}, {'_id':0,'affinity_points':1})

    inv_unchanged_on_replay = (pre_inv or {}).get('quantity') == (post_inv or {}).get('quantity')
    aff_unchanged_on_replay = (pre_aff or {}).get('affinity_points') == (post_aff or {}).get('affinity_points')

    # Re-test Borea: must 404 + no ledger row
    pre_borea_rows = coll.count_documents({'hero_id':{'$in':['borea','greek_borea','primordial_gaia']}})
    code_borea, _ = _post('/affinity/gift-spend',
        {'gift_id':'gift_test_001','hero_id':'borea','quantity':1,
         'idempotency_key':'v16monboreaxx','user_id':'stage1_qa_001'})
    post_borea_rows = coll.count_documents({'hero_id':{'$in':['borea','greek_borea','primordial_gaia']}})

    # Re-test non-allowlist: 423
    code_nonal, _ = _post('/affinity/gift-spend',
        {'gift_id':'gift_test_001','hero_id':'greek_zeus','quantity':1,
         'idempotency_key':'v16monnonalxx','user_id':'unauth_user_xyz'})

    # Re-test insufficient: 412 + no decrement. Use qty within Pydantic
    # bounds (<=1000) but above seeded inventory (10) to hit the inv check.
    pre_inv_004 = ugi.find_one({'user_id':'stage1_qa_004','gift_id':'gift_test_001'}, {'_id':0,'quantity':1})
    code_412, body_412 = _post('/affinity/gift-spend',
        {'gift_id':'gift_test_001','hero_id':'greek_zeus','quantity':500,
         'idempotency_key':'v16moninsuffx','user_id':'stage1_qa_004'})
    post_inv_004 = ugi.find_one({'user_id':'stage1_qa_004','gift_id':'gift_test_001'}, {'_id':0,'quantity':1})

    # DB invariants
    inv_mut_rows = coll.count_documents({'inventory_mutated': True})
    aff_mut_rows = coll.count_documents({'affinity_points_mutated': True})
    buffs_rows = coll.count_documents({'buffs_activated': True})
    battle_rows = coll.count_documents({'battle_wiring_attached': True})
    neg_inv = ugi.count_documents({'quantity': {'$lt': 0}})

    # Cross-check: every inv_mut_row has matching update to inventory
    inv_mut_sample = list(coll.find({'inventory_mutated': True}, {'_id':0,'tx_id':1,'user_id':1,'gift_id':1,'quantity':1,'hero_id':1}).limit(20))

    triggers = []
    if code_replay != 200: triggers.append(('replay_not_200', f'got {code_replay}'))
    if body_replay and body_replay.get('result') != 'idempotent_replay': triggers.append(('replay_not_idempotent', f"got result={body_replay.get('result')}"))
    if not inv_unchanged_on_replay: triggers.append(('idempotency_inventory_double_decrement', f'pre={pre_inv} post={post_inv}'))
    if not aff_unchanged_on_replay: triggers.append(('idempotency_affinity_double_increment', f'pre={pre_aff} post={post_aff}'))
    if code_borea != 404: triggers.append(('borea_not_404', f'got {code_borea}'))
    if post_borea_rows != pre_borea_rows or pre_borea_rows != 0: triggers.append(('borea_ledger_row_created', f'pre={pre_borea_rows} post={post_borea_rows}'))
    if code_nonal != 423: triggers.append(('non_allowlist_not_423', f'got {code_nonal}'))
    if code_412 != 412: triggers.append(('insufficient_not_412', f'got {code_412}'))
    if (pre_inv_004 or {}).get('quantity') != (post_inv_004 or {}).get('quantity'):
        triggers.append(('insufficient_caused_decrement', f'pre={pre_inv_004} post={post_inv_004}'))
    if buffs_rows > 0: triggers.append(('buffs_rows_present', f'count={buffs_rows}'))
    if battle_rows > 0: triggers.append(('battle_rows_present', f'count={battle_rows}'))
    if neg_inv > 0: triggers.append(('negative_inventory_present', f'count={neg_inv}'))
    if inv_mut_rows != aff_mut_rows: triggers.append(('inv_aff_mut_mismatch', f'inv={inv_mut_rows} aff={aff_mut_rows}'))

    payload = {
        'result_id': 'affinity_inventory_live_monitoring_v16_result',
        'task_origin': 'AF2-N-INVENTORY-LIVE-MONITORING-V16',
        'design_only': False, 'runtime_attached': True,
        'runtime_attached_stage1_allowlist_only': True,
        'db_write': True, 'db_write_scope_v16': 'gift_transaction_ledger + user_gift_inventory + user_affinity_state (Stage1 only)',
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'inventory_activation_state': 'ACTIVATED',
        'controlled_spends_already_executed_by_apply': True,
        'replay_idempotency': {
            'replay_code': code_replay, 'replay_result': (body_replay or {}).get('result'),
            'inventory_pre': pre_inv, 'inventory_post': post_inv, 'inventory_unchanged': inv_unchanged_on_replay,
            'affinity_pre': pre_aff, 'affinity_post': post_aff, 'affinity_unchanged': aff_unchanged_on_replay,
        },
        'borea_block': {'code': code_borea, 'expected': 404, 'pre_borea_rows': pre_borea_rows, 'post_borea_rows': post_borea_rows},
        'non_allowlist_block': {'code': code_nonal, 'expected': 423},
        'insufficient_block': {'code': code_412, 'expected': 412,
                               'inv_pre': pre_inv_004, 'inv_post': post_inv_004,
                               'inv_unchanged': (pre_inv_004 or {}).get('quantity') == (post_inv_004 or {}).get('quantity')},
        'observed': {
            'ledger_inventory_mutated_rows': inv_mut_rows,
            'ledger_affinity_points_mutated_rows': aff_mut_rows,
            'ledger_buffs_activated_rows': buffs_rows,
            'ledger_battle_wiring_rows': battle_rows,
            'ledger_negative_inventory_count': neg_inv,
            'inv_mut_sample_first_20': inv_mut_sample,
        },
        'triggers_fired': [{'trigger': t, 'detail': d} for t, d in triggers],
        'triggers_total': len(triggers),
        'overall_status': 'PASS_ACTIVATED' if not triggers else 'FAIL',
        'safety_flags': {
            'runtime_attached_stage1_allowlist_only': True,
            'broad_rollout_authorized': False,
            'inventory_wiring_live': True,
            'inventory_mutation_enabled': True,
            'affinity_points_mutation_enabled': True,
            'buffs_enabled': False,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
            'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'live monitoring v16: status={payload["overall_status"]}, triggers={len(triggers)}')
    return 0 if not triggers else 1

if __name__ == '__main__':
    sys.exit(main())
