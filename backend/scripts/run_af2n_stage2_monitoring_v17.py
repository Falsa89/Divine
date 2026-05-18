#!/usr/bin/env python3
"""Stage2 monitoring V17 — runs only if Stage2 has been APPLIED.

If Stage2 result indicates READY_NOT_APPLIED, emits a 'NOT_APPLICABLE_READY_NOT_APPLIED'
result and exits 0 (this is the safe path).
If APPLIED, runs 80 samples mostly read-only + a few controlled Stage2 spends.
"""
from __future__ import annotations
import json, sys, uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
APPLY_RESULT = Path('/app/data/design/affinity/af2n_stage2_5_10pct_apply_result_v1.json')
OUT = Path('/app/data/design/affinity/af2n_stage2_monitoring_v17_result.json')
SAMPLES_TARGET = 80
MAX_STAGE2_FRESH_SPENDS = 5


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
    if not APPLY_RESULT.exists():
        payload = {'overall_status': 'NOT_APPLICABLE_NO_APPLY_RESULT'}
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
        print('Stage2 monitoring: NOT_APPLICABLE (no apply result file)'); return 0
    apply_data = json.loads(APPLY_RESULT.read_text())
    if apply_data.get('overall_status') != 'APPLIED_PASS':
        payload = {
            'result_id': 'af2n_stage2_monitoring_v17_result',
            'task_origin': 'AF2-N-STAGE2-MONITORING-V17',
            'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
            'overall_status': 'NOT_APPLICABLE_READY_NOT_APPLIED',
            'reason': apply_data.get('ready_not_applied_reason'),
            'apply_status_seen': apply_data.get('overall_status'),
            'safety_flags': {
                'runtime_attached_stage1_allowlist_only': True,
                'broad_rollout_authorized': False,
                'battle_runtime_attached': False, 'applied_to_combat': False,
                'buffs_enabled': False,
                'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
            },
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print('Stage2 monitoring: NOT_APPLICABLE_READY_NOT_APPLIED'); return 0

    # APPLIED path: small monitoring
    from pymongo import MongoClient
    db = MongoClient('mongodb://localhost:27017')['divine_waifus']
    ugi = db['user_gift_inventory']; uas = db['user_affinity_state']; coll = db['gift_transaction_ledger']

    pre_ledger = coll.count_documents({})
    pre_neg_inv = ugi.count_documents({'quantity': {'$lt': 0}})
    pre_inv_mut = coll.count_documents({'inventory_mutated': True})
    pre_aff_mut = coll.count_documents({'affinity_points_mutated': True})
    pre_buffs = coll.count_documents({'buffs_activated': True})
    pre_battle = coll.count_documents({'battle_wiring_attached': True})

    triggers = []; counters = {'samples_total':0,'health_ok':0,'heroes_100':0,'borea_404':0,'borea_bad':0,'non_allowlist_423':0,'non_allowlist_bad':0,'stage2_fresh_ok':0,'stage2_fresh_fail':0,'http_5xx':0}
    for i in range(30):
        counters['samples_total'] += 1
        c, _ = _get('/health');
        if c == 200: counters['health_ok'] += 1
        elif 500 <= c < 600: counters['http_5xx'] += 1
    for i in range(10):
        counters['samples_total'] += 1
        c, data = _get('/heroes')
        if isinstance(data, list) and len(data) == 100: counters['heroes_100'] += 1
        if 500 <= c < 600: counters['http_5xx'] += 1
    for alias in ['borea','greek_borea','primordial_gaia']*5:
        counters['samples_total'] += 1
        c, _ = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':alias,'quantity':1,
             'idempotency_key':'v17stmonB'+uuid.uuid4().hex[:5],
             'user_id':'stage2_qa_001'})
        if c == 404: counters['borea_404'] += 1
        else: counters['borea_bad'] += 1; triggers.append(('borea_not_404', f'{alias} got={c}'))
    for i in range(15):
        counters['samples_total'] += 1
        c, _ = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':'greek_zeus','quantity':1,
             'idempotency_key':f'v17stmonNA{i:03d}','user_id':f'unauth_st2_{i}'})
        if c == 423: counters['non_allowlist_423'] += 1
        else: counters['non_allowlist_bad'] += 1; triggers.append(('non_allowlist_not_423', f'i={i} got={c}'))

    stage2_users = [(f'stage2_qa_{i:03d}','greek_zeus',1) for i in (1,2,3,4,5)]
    for u, h, q in stage2_users:
        counters['samples_total'] += 1
        pre_iq = (ugi.find_one({'user_id':u,'gift_id':'gift_test_001'}, {'_id':0,'quantity':1}) or {}).get('quantity', 0)
        pre_ap = (uas.find_one({'user_id':u,'hero_id':h}, {'_id':0,'affinity_points':1}) or {}).get('affinity_points', 0)
        k = 'v17stmonS' + uuid.uuid4().hex[:10]
        c, body = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':h,'quantity':q,'idempotency_key':k,'user_id':u})
        post_iq = (ugi.find_one({'user_id':u,'gift_id':'gift_test_001'}, {'_id':0,'quantity':1}) or {}).get('quantity', 0)
        post_ap = (uas.find_one({'user_id':u,'hero_id':h}, {'_id':0,'affinity_points':1}) or {}).get('affinity_points', 0)
        if c == 200 and (post_iq == pre_iq - q) and (post_ap == pre_ap + q):
            counters['stage2_fresh_ok'] += 1
        else:
            counters['stage2_fresh_fail'] += 1
            triggers.append(('stage2_fresh_spend_inexact', f'user={u} c={c} pre_iq={pre_iq} post_iq={post_iq} pre_ap={pre_ap} post_ap={post_ap}'))

    # Idempotent replay on first Stage2 user
    if stage2_users:
        u, h, q = stage2_users[0]
        last_key = 'v17stmonRPxxxx'
        # Use a fresh key first, then replay it
        kfresh = 'v17stmonRP' + uuid.uuid4().hex[:6]
        pre_iq = (ugi.find_one({'user_id':u,'gift_id':'gift_test_001'}, {'_id':0,'quantity':1}) or {}).get('quantity', 0)
        pre_ap = (uas.find_one({'user_id':u,'hero_id':h}, {'_id':0,'affinity_points':1}) or {}).get('affinity_points', 0)
        counters['samples_total'] += 1
        c1, _ = _post('/affinity/gift-spend', {'gift_id':'gift_test_001','hero_id':h,'quantity':1,'idempotency_key':kfresh,'user_id':u})
        mid_iq = (ugi.find_one({'user_id':u,'gift_id':'gift_test_001'}, {'_id':0,'quantity':1}) or {}).get('quantity', 0)
        mid_ap = (uas.find_one({'user_id':u,'hero_id':h}, {'_id':0,'affinity_points':1}) or {}).get('affinity_points', 0)
        counters['samples_total'] += 1
        c2, body2 = _post('/affinity/gift-spend', {'gift_id':'gift_test_001','hero_id':h,'quantity':1,'idempotency_key':kfresh,'user_id':u})
        post_iq = (ugi.find_one({'user_id':u,'gift_id':'gift_test_001'}, {'_id':0,'quantity':1}) or {}).get('quantity', 0)
        post_ap = (uas.find_one({'user_id':u,'hero_id':h}, {'_id':0,'affinity_points':1}) or {}).get('affinity_points', 0)
        if c1 == 200 and c2 == 200 and isinstance(body2, dict) and body2.get('result') == 'idempotent_replay' and mid_iq == post_iq and mid_ap == post_ap:
            counters['stage2_fresh_ok'] += 1
        else:
            counters['stage2_fresh_fail'] += 1
            triggers.append(('stage2_replay_failed', f'c1={c1} c2={c2} mid_iq={mid_iq} post_iq={post_iq}'))

    post_neg_inv = ugi.count_documents({'quantity': {'$lt': 0}})
    post_inv_mut = coll.count_documents({'inventory_mutated': True})
    post_aff_mut = coll.count_documents({'affinity_points_mutated': True})
    post_buffs = coll.count_documents({'buffs_activated': True})
    post_battle = coll.count_documents({'battle_wiring_attached': True})
    inv_delta = post_inv_mut - pre_inv_mut; aff_delta = post_aff_mut - pre_aff_mut
    if post_neg_inv > 0: triggers.append(('negative_inventory', f'count={post_neg_inv}'))
    if post_buffs > 0: triggers.append(('buffs_rows', f'count={post_buffs}'))
    if post_battle > 0: triggers.append(('battle_rows', f'count={post_battle}'))
    if inv_delta != aff_delta: triggers.append(('inv_aff_delta_mismatch', f'inv={inv_delta} aff={aff_delta}'))
    if counters['http_5xx'] > 0: triggers.append(('http_5xx', f'count={counters["http_5xx"]}'))

    overall_pass = (
        counters['samples_total'] >= 70 and
        counters['borea_bad'] == 0 and
        counters['non_allowlist_bad'] == 0 and
        counters['stage2_fresh_fail'] == 0 and
        counters['http_5xx'] == 0 and
        not triggers
    )

    payload = {
        'result_id': 'af2n_stage2_monitoring_v17_result',
        'task_origin': 'AF2-N-STAGE2-MONITORING-V17',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'design_only': False, 'runtime_attached': True,
        'broad_rollout_authorized': False,
        'samples_target': SAMPLES_TARGET,
        'counters': counters,
        'pre': {'ledger': pre_ledger, 'negative_inventory': pre_neg_inv,
                'inv_mut': pre_inv_mut, 'aff_mut': pre_aff_mut,
                'buffs': pre_buffs, 'battle_wiring': pre_battle},
        'post': {'negative_inventory': post_neg_inv,
                 'inv_mut': post_inv_mut, 'aff_mut': post_aff_mut,
                 'inv_mut_delta': inv_delta, 'aff_mut_delta': aff_delta,
                 'buffs': post_buffs, 'battle_wiring': post_battle},
        'triggers_fired': [{'trigger':t,'detail':d} for t, d in triggers],
        'triggers_total': len(triggers),
        'overall_status': 'PASS' if overall_pass else 'FAIL',
        'safety_flags': {
            'runtime_attached_stage1_allowlist_only': True,
            'broad_rollout_authorized': False,
            'battle_runtime_attached': False, 'applied_to_combat': False,
            'buffs_enabled': False,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'Stage2 monitoring v17: status={payload["overall_status"]}, triggers={len(triggers)}')
    return 0 if overall_pass else 1

if __name__ == '__main__':
    sys.exit(main())
