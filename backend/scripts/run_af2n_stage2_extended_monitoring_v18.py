#!/usr/bin/env python3
"""AF2-N-STAGE2-EXTENDED-MONITORING V18.

160 samples: mostly read/status/replay/non-allowlist/Borea-reject + max 8 fresh
Stage2 spends on dedicated users.
"""
from __future__ import annotations
import json, sys, uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_stage2_extended_monitoring_v18_result.json')
SAMPLES_TARGET = 160
MAX_FRESH_SPENDS = 8


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
    pre_neg_inv = ugi.count_documents({'quantity': {'$lt': 0}})
    pre_inv_mut = coll.count_documents({'inventory_mutated': True})
    pre_aff_mut = coll.count_documents({'affinity_points_mutated': True})
    pre_buffs = coll.count_documents({'buffs_activated': True})
    pre_battle = coll.count_documents({'battle_wiring_attached': True})

    triggers = []
    counters = {'samples_total':0,'health_ok':0,'heroes_100':0,'borea_404':0,'borea_bad':0,
                'non_allowlist_423':0,'non_allowlist_bad':0,'replay_ok':0,'replay_bad':0,
                'fresh_spend_ok':0,'fresh_spend_fail':0,'http_5xx':0,'canary_status_200':0}
    # 70 health
    for i in range(70):
        counters['samples_total'] += 1
        c, _ = _get('/health')
        if c == 200: counters['health_ok'] += 1
        elif 500 <= c < 600: counters['http_5xx'] += 1
    # 20 canary-status
    for i in range(20):
        counters['samples_total'] += 1
        c, _ = _get('/affinity/gift-spend/canary-status')
        if c == 200: counters['canary_status_200'] += 1
        elif 500 <= c < 600: counters['http_5xx'] += 1
    # 20 heroes count
    for i in range(20):
        counters['samples_total'] += 1
        c, data = _get('/heroes')
        if isinstance(data, list) and len(data) == 100: counters['heroes_100'] += 1
        if 500 <= c < 600: counters['http_5xx'] += 1
    # 15 Borea aliases
    for alias in (['borea','greek_borea','primordial_gaia']*5):
        counters['samples_total'] += 1
        c, _ = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':alias,'quantity':1,
             'idempotency_key':'v18stmonB'+uuid.uuid4().hex[:5],'user_id':'stage2_qa_001'})
        if c == 404: counters['borea_404'] += 1
        else: counters['borea_bad'] += 1; triggers.append(('borea_not_404', f'{alias} got={c}'))
        if 500 <= c < 600: counters['http_5xx'] += 1
    # 15 non-allow
    for i in range(15):
        counters['samples_total'] += 1
        c, _ = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':'greek_zeus','quantity':1,
             'idempotency_key':f'v18stmonNA{i:03d}','user_id':f'unauth_v18_{i}'})
        if c == 423: counters['non_allowlist_423'] += 1
        else: counters['non_allowlist_bad'] += 1; triggers.append(('non_allowlist_not_423', f'i={i} got={c}'))
        if 500 <= c < 600: counters['http_5xx'] += 1
    # 12 idempotent replays of historical fresh keys (v17 keys exist for stage2_qa_001..005)
    # Pick known idempotency keys via DB; we replay arbitrary recent ones.
    known = list(coll.find({'canary': True, 'inventory_mutated': True}).sort([('_id',-1)]).limit(12))
    for doc in known:
        counters['samples_total'] += 1
        u = doc.get('user_id'); h = doc.get('hero_id'); k = doc.get('idempotency_key'); q = doc.get('quantity')
        pre_iq = (ugi.find_one({'user_id':u,'gift_id':doc.get('gift_id','gift_test_001')}, {'_id':0,'quantity':1}) or {}).get('quantity')
        pre_ap = (uas.find_one({'user_id':u,'hero_id':h}, {'_id':0,'affinity_points':1}) or {}).get('affinity_points')
        c, body = _post('/affinity/gift-spend',
            {'gift_id':doc.get('gift_id','gift_test_001'),'hero_id':h,'quantity':q,
             'idempotency_key':k,'user_id':u})
        post_iq = (ugi.find_one({'user_id':u,'gift_id':doc.get('gift_id','gift_test_001')}, {'_id':0,'quantity':1}) or {}).get('quantity')
        post_ap = (uas.find_one({'user_id':u,'hero_id':h}, {'_id':0,'affinity_points':1}) or {}).get('affinity_points')
        if c == 200 and isinstance(body, dict) and body.get('result') == 'idempotent_replay' and pre_iq == post_iq and pre_ap == post_ap:
            counters['replay_ok'] += 1
        else:
            counters['replay_bad'] += 1
            triggers.append(('replay_failed', f'u={u} c={c} pre_iq={pre_iq} post_iq={post_iq}'))
        if 500 <= c < 600: counters['http_5xx'] += 1
    # 8 fresh Stage2 spends (different users to avoid colliding with V17 monitoring users)
    fresh = [(f'stage2_qa_{i:03d}','greek_hera',1) for i in (11,12,13,14,15,16,17,18)]
    for u, h, q in fresh:
        counters['samples_total'] += 1
        pre_iq = (ugi.find_one({'user_id':u,'gift_id':'gift_test_001'}, {'_id':0,'quantity':1}) or {}).get('quantity', 0)
        pre_ap = (uas.find_one({'user_id':u,'hero_id':h}, {'_id':0,'affinity_points':1}) or {}).get('affinity_points', 0)
        k = 'v18stmonF' + uuid.uuid4().hex[:10]
        c, body = _post('/affinity/gift-spend',
            {'gift_id':'gift_test_001','hero_id':h,'quantity':q,'idempotency_key':k,'user_id':u})
        post_iq = (ugi.find_one({'user_id':u,'gift_id':'gift_test_001'}, {'_id':0,'quantity':1}) or {}).get('quantity', 0)
        post_ap = (uas.find_one({'user_id':u,'hero_id':h}, {'_id':0,'affinity_points':1}) or {}).get('affinity_points', 0)
        if c == 200 and (post_iq == pre_iq - q) and (post_ap == pre_ap + q):
            counters['fresh_spend_ok'] += 1
        else:
            counters['fresh_spend_fail'] += 1
            triggers.append(('fresh_spend_inexact', f'u={u} c={c} pre_iq={pre_iq} post_iq={post_iq} pre_ap={pre_ap} post_ap={post_ap}'))
        if 500 <= c < 600: counters['http_5xx'] += 1

    post_neg_inv = ugi.count_documents({'quantity': {'$lt': 0}})
    post_inv_mut = coll.count_documents({'inventory_mutated': True})
    post_aff_mut = coll.count_documents({'affinity_points_mutated': True})
    post_buffs = coll.count_documents({'buffs_activated': True})
    post_battle = coll.count_documents({'battle_wiring_attached': True})
    inv_delta = post_inv_mut - pre_inv_mut
    aff_delta = post_aff_mut - pre_aff_mut

    if post_neg_inv > 0: triggers.append(('negative_inventory', f'count={post_neg_inv}'))
    if post_buffs > 0: triggers.append(('buffs_rows', f'count={post_buffs}'))
    if post_battle > 0: triggers.append(('battle_rows', f'count={post_battle}'))
    if inv_delta != aff_delta: triggers.append(('inv_aff_delta_mismatch', f'inv={inv_delta} aff={aff_delta}'))
    if inv_delta != counters['fresh_spend_ok']:
        triggers.append(('inv_delta_vs_fresh_ok', f'inv={inv_delta} fresh={counters["fresh_spend_ok"]}'))
    if counters['http_5xx'] > 0: triggers.append(('http_5xx', f'count={counters["http_5xx"]}'))

    overall_pass = (
        counters['samples_total'] >= SAMPLES_TARGET and
        counters['borea_bad'] == 0 and
        counters['non_allowlist_bad'] == 0 and
        counters['replay_bad'] == 0 and
        counters['fresh_spend_fail'] == 0 and
        counters['http_5xx'] == 0 and not triggers
    )
    payload = {
        'result_id': 'af2n_stage2_extended_monitoring_v18_result',
        'task_origin': 'AF2-N-STAGE2-EXTENDED-MONITORING-V18',
        'design_only': False, 'runtime_attached': True,
        'broad_rollout_authorized': False,
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'samples_target': SAMPLES_TARGET, 'max_fresh_spends': MAX_FRESH_SPENDS,
        'counters': counters,
        'pre': {'ledger': pre_ledger, 'negative_inventory': pre_neg_inv,
                'inv_mut': pre_inv_mut, 'aff_mut': pre_aff_mut,
                'buffs': pre_buffs, 'battle_wiring': pre_battle},
        'post': {'negative_inventory': post_neg_inv,
                 'inv_mut': post_inv_mut, 'aff_mut': post_aff_mut,
                 'inv_mut_delta': inv_delta, 'aff_mut_delta': aff_delta,
                 'buffs': post_buffs, 'battle_wiring': post_battle},
        'triggers_fired': [{'trigger':t,'detail':d} for t,d in triggers],
        'triggers_total': len(triggers),
        'overall_status': 'PASS' if overall_pass else 'FAIL',
        'safety_flags': {
            'broad_rollout_authorized': False, 'public_spend_ui': False,
            'battle_runtime_attached': False, 'applied_to_combat': False,
            'buffs_enabled': False, 'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'V18 Stage2 extended monitoring: {payload["overall_status"]}, samples={counters["samples_total"]}, triggers={len(triggers)}')
    return 0 if overall_pass else 1

if __name__ == '__main__':
    sys.exit(main())
