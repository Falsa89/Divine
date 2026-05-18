#!/usr/bin/env python3
"""AF2-N-INVENTORY-EXTENDED-MONITORING V17.

Extended observation window. Runs 120 deterministic samples primarily
read-only / replay / non-allowlist / borea reject. Includes a small set of
fresh controlled spends (max 5) using dedicated QA users.
"""
from __future__ import annotations
import json, sys, uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_inventory_extended_monitoring_v17_result.json')
SAMPLES_TOTAL = 120
MAX_FRESH_SPENDS = 5


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
    ugi = db['user_gift_inventory']; uas = db['user_affinity_state']; coll = db['gift_transaction_ledger']

    pre_ledger = coll.count_documents({})
    pre_inv_total = ugi.count_documents({})
    pre_neg_inv = ugi.count_documents({'quantity': {'$lt': 0}})
    pre_inv_mut = coll.count_documents({'inventory_mutated': True})
    pre_aff_mut = coll.count_documents({'affinity_points_mutated': True})
    pre_buffs = coll.count_documents({'buffs_activated': True})
    pre_battle = coll.count_documents({'battle_wiring_attached': True})

    triggers = []
    counters = {
        'samples_total': 0, 'health_ok': 0, 'heroes_count_100': 0,
        'borea_404': 0, 'borea_not_404': 0,
        'non_allowlist_423': 0, 'non_allowlist_other': 0,
        'idempotent_replay_ok': 0, 'idempotent_replay_bad': 0,
        'fresh_spend_ok': 0, 'fresh_spend_fail': 0,
        'http_5xx': 0,
    }

    # 50 health checks
    for i in range(50):
        counters['samples_total'] += 1
        c, _ = _get('/health')
        if c == 200: counters['health_ok'] += 1
        elif 500 <= c < 600: counters['http_5xx'] += 1

    # 20 heroes count
    for i in range(20):
        counters['samples_total'] += 1
        c, data = _get('/heroes')
        if isinstance(data, list) and len(data) == 100: counters['heroes_count_100'] += 1
        if 500 <= c < 600: counters['http_5xx'] += 1

    # 15 Borea aliases POST
    for alias in ['borea','greek_borea','primordial_gaia','borea','greek_borea']*3:
        counters['samples_total'] += 1
        c, _ = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':alias,'quantity':1,
             'idempotency_key':'v17monBorea'+uuid.uuid4().hex[:4],
             'user_id':'stage1_qa_001'})
        if c == 404: counters['borea_404'] += 1
        else: counters['borea_not_404'] += 1; triggers.append(('borea_not_404', f'alias={alias} got={c}'))
        if 500 <= c < 600: counters['http_5xx'] += 1

    # 15 non-allowlist 423
    for i in range(15):
        counters['samples_total'] += 1
        c, _ = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':'greek_zeus','quantity':1,
             'idempotency_key':f'v17monNON{i:03d}xx','user_id':f'unauth_v17_{i}'})
        if c == 423: counters['non_allowlist_423'] += 1
        else: counters['non_allowlist_other'] += 1; triggers.append(('non_allowlist_not_423', f'i={i} got={c}'))
        if 500 <= c < 600: counters['http_5xx'] += 1

    # 15 idempotent replays of existing V16 keys
    replay_keys = [('stage1_qa_001','v16live001ai',2,'greek_zeus')]*15
    for u, k, q, h in replay_keys:
        counters['samples_total'] += 1
        pre_iq = (ugi.find_one({'user_id':u,'gift_id':'gift_test_001'}, {'_id':0,'quantity':1}) or {}).get('quantity')
        pre_ap = (uas.find_one({'user_id':u,'hero_id':h}, {'_id':0,'affinity_points':1}) or {}).get('affinity_points')
        c, body = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':h,'quantity':q,'idempotency_key':k,'user_id':u})
        post_iq = (ugi.find_one({'user_id':u,'gift_id':'gift_test_001'}, {'_id':0,'quantity':1}) or {}).get('quantity')
        post_ap = (uas.find_one({'user_id':u,'hero_id':h}, {'_id':0,'affinity_points':1}) or {}).get('affinity_points')
        if c == 200 and isinstance(body, dict) and body.get('result') == 'idempotent_replay' and pre_iq == post_iq and pre_ap == post_ap:
            counters['idempotent_replay_ok'] += 1
        else:
            counters['idempotent_replay_bad'] += 1
            triggers.append(('replay_state_changed_or_not_idempotent', f'c={c} pre_iq={pre_iq} post_iq={post_iq} pre_ap={pre_ap} post_ap={post_ap}'))
        if 500 <= c < 600: counters['http_5xx'] += 1

    # 5 small controlled fresh spends on dedicated QA users
    fresh_users = [('stage1_qa_006','greek_zeus',1),
                   ('stage1_qa_007','greek_hera',1),
                   ('stage1_qa_008','greek_apollo',1),
                   ('stage1_qa_009','greek_athena',1),
                   ('stage1_qa_010','greek_ares',1)]
    fresh_keys = [f'v17ext{uuid.uuid4().hex[:10]}' for _ in fresh_users]
    for (u, h, q), k in zip(fresh_users, fresh_keys):
        counters['samples_total'] += 1
        pre_iq = (ugi.find_one({'user_id':u,'gift_id':'gift_test_001'}, {'_id':0,'quantity':1}) or {}).get('quantity', 0)
        pre_ap = (uas.find_one({'user_id':u,'hero_id':h}, {'_id':0,'affinity_points':1}) or {}).get('affinity_points', 0)
        c, body = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':h,'quantity':q,'idempotency_key':k,'user_id':u})
        post_iq = (ugi.find_one({'user_id':u,'gift_id':'gift_test_001'}, {'_id':0,'quantity':1}) or {}).get('quantity', 0)
        post_ap = (uas.find_one({'user_id':u,'hero_id':h}, {'_id':0,'affinity_points':1}) or {}).get('affinity_points', 0)
        if c == 200 and (post_iq == pre_iq - q) and (post_ap == pre_ap + q):
            counters['fresh_spend_ok'] += 1
        else:
            counters['fresh_spend_fail'] += 1
            triggers.append(('fresh_spend_inexact', f'user={u} c={c} pre_iq={pre_iq} post_iq={post_iq} pre_ap={pre_ap} post_ap={post_ap}'))
        if 500 <= c < 600: counters['http_5xx'] += 1

    post_ledger = coll.count_documents({})
    post_neg_inv = ugi.count_documents({'quantity': {'$lt': 0}})
    post_inv_mut = coll.count_documents({'inventory_mutated': True})
    post_aff_mut = coll.count_documents({'affinity_points_mutated': True})
    post_buffs = coll.count_documents({'buffs_activated': True})
    post_battle = coll.count_documents({'battle_wiring_attached': True})

    ledger_delta = post_ledger - pre_ledger
    inv_mut_delta = post_inv_mut - pre_inv_mut
    aff_mut_delta = post_aff_mut - pre_aff_mut

    if post_neg_inv > 0 or pre_neg_inv > 0:
        triggers.append(('negative_inventory_present', f'pre={pre_neg_inv} post={post_neg_inv}'))
    if post_buffs > 0: triggers.append(('buffs_rows', f'count={post_buffs}'))
    if post_battle > 0: triggers.append(('battle_rows', f'count={post_battle}'))
    if inv_mut_delta != aff_mut_delta:
        triggers.append(('inv_aff_delta_mismatch', f'inv_delta={inv_mut_delta} aff_delta={aff_mut_delta}'))
    if inv_mut_delta != counters['fresh_spend_ok']:
        triggers.append(('inv_mut_delta_vs_fresh_spend_ok', f'inv_delta={inv_mut_delta} fresh_ok={counters["fresh_spend_ok"]}'))
    if counters['http_5xx'] > 0:
        triggers.append(('http_5xx', f'count={counters["http_5xx"]}'))

    overall_pass = (
        counters['samples_total'] == SAMPLES_TOTAL and
        counters['health_ok'] >= 49 and
        counters['heroes_count_100'] >= 19 and
        counters['borea_404'] >= 14 and
        counters['borea_not_404'] == 0 and
        counters['non_allowlist_423'] >= 14 and
        counters['non_allowlist_other'] == 0 and
        counters['idempotent_replay_ok'] >= 14 and
        counters['idempotent_replay_bad'] == 0 and
        counters['fresh_spend_ok'] >= 4 and
        counters['http_5xx'] == 0 and
        not triggers
    )

    payload = {
        'result_id': 'af2n_inventory_extended_monitoring_v17_result',
        'task_origin': 'AF2-N-INVENTORY-EXTENDED-MONITORING-V17',
        'design_only': False, 'runtime_attached': True,
        'runtime_attached_stage1_allowlist_only': True,
        'db_write': True,
        'db_write_scope': 'gift_transaction_ledger + user_gift_inventory + user_affinity_state (Stage1 allowlist only, max 5 fresh spends)',
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'samples_total': counters['samples_total'],
        'samples_target': SAMPLES_TOTAL,
        'max_fresh_spends_allowed': MAX_FRESH_SPENDS,
        'counters': counters,
        'pre': {
            'ledger': pre_ledger, 'inv_collection': pre_inv_total, 'negative_inventory': pre_neg_inv,
            'inventory_mutated': pre_inv_mut, 'affinity_points_mutated': pre_aff_mut,
            'buffs': pre_buffs, 'battle_wiring': pre_battle,
        },
        'post': {
            'ledger': post_ledger, 'negative_inventory': post_neg_inv,
            'inventory_mutated': post_inv_mut, 'affinity_points_mutated': post_aff_mut,
            'buffs': post_buffs, 'battle_wiring': post_battle,
            'ledger_delta': ledger_delta,
            'inv_mut_delta': inv_mut_delta, 'aff_mut_delta': aff_mut_delta,
        },
        'triggers_fired': [{'trigger': t, 'detail': d} for t, d in triggers],
        'triggers_total': len(triggers),
        'overall_status': 'PASS' if overall_pass else 'FAIL',
        'safety_flags': {
            'runtime_attached_stage1_allowlist_only': True,
            'broad_rollout_authorized': False,
            'inventory_wiring_live': True,
            'buffs_enabled': False, 'battle_runtime_attached': False, 'applied_to_combat': False,
            'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'V17 extended monitoring: status={payload["overall_status"]}, samples={counters["samples_total"]}, triggers={len(triggers)}')
    return 0 if overall_pass else 1

if __name__ == '__main__':
    sys.exit(main())
