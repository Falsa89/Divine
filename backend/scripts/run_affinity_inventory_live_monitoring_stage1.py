#!/usr/bin/env python3
"""AF2-N-INVENTORY-LIVE-MONITORING (Stage1 only) — V15.

If activation_state == 'ACTIVATED' (not today), runs controlled spends and
verifies inventory/affinity deltas. Today (V15) the activation is
READY_NOT_ACTIVATED — so this script runs a SAFE-BLOCK monitoring report:
  - confirms the dedicated flag is OFF
  - confirms ledger has 0 inventory_mutated / affinity_points_mutated rows
  - confirms the route still returns inventory_mutation_enabled=False in canary-status
  - confirms Borea, non-allowlist behaviors unchanged
Produces result with overall_status='PASS_SAFE_BLOCK'.
"""
from __future__ import annotations
import json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
APPLY_RESULT = Path('/app/data/design/affinity/affinity_inventory_wiring_stage1_apply_result_v1.json')
OUT = Path('/app/data/design/affinity/affinity_inventory_live_monitoring_stage1_result_v1.json')
FLAG_NAME = 'AFFINITY_GIFT_INVENTORY_WRITES_ENABLED'
FLAG_ON = 'true_explicit_affinity_inventory_on'


def _get(p):
    try:
        with urlopen(API + p, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None


def _post(p, b):
    payload = json.dumps(b).encode(); headers = {'Content-Type': 'application/json'}
    req = Request(API + p, data=payload, method='POST', headers=headers)
    try:
        with urlopen(req, timeout=6) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1


def main():
    if not APPLY_RESULT.exists():
        print('APPLY_RESULT_MISSING'); return 1
    apply_r = json.loads(APPLY_RESULT.read_text())
    state = apply_r.get('activation_state')
    flag_on = os.environ.get(FLAG_NAME) == FLAG_ON

    triggers = []
    code, status = _get('/affinity/gift-spend/canary-status')
    canary_inv_off = code == 200 and isinstance(status, dict) and status.get('inventory_mutation_enabled') is False
    canary_pts_off = code == 200 and isinstance(status, dict) and status.get('affinity_points_mutation_enabled') is False
    canary_buffs_off = code == 200 and isinstance(status, dict) and status.get('buffs_enabled') is False
    canary_battle_off = code == 200 and isinstance(status, dict) and status.get('battle_runtime_attached') is False

    code_h, heroes = _get('/heroes')
    heroes_ok = isinstance(heroes, list) and len(heroes) == 100
    borea_ok = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234efgh','user_id':'user_canary_001'}) == 404
    nonal_ok = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'v15invmon1','user_id':'unauth_user_xxx'}) == 423

    db_inv = db_pts = db_buf = db_btl = -1
    try:
        from pymongo import MongoClient
        coll = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']['gift_transaction_ledger']
        db_inv = coll.count_documents({'inventory_mutated': True})
        db_pts = coll.count_documents({'affinity_points_mutated': True})
        db_buf = coll.count_documents({'buffs_activated': True})
        db_btl = coll.count_documents({'battle_wiring_attached': True})
    except Exception as e:
        triggers.append(('mongo_unreachable', repr(e)))

    if state == 'READY_NOT_ACTIVATED':
        # SAFE-BLOCK path expected today
        if flag_on: triggers.append(('flag_on_but_state_blocked', f'{FLAG_NAME} set unexpectedly'))
        if not canary_inv_off: triggers.append(('canary_inv_not_off', ''))
        if not canary_pts_off: triggers.append(('canary_pts_not_off', ''))
        if not canary_buffs_off: triggers.append(('canary_buffs_not_off', ''))
        if not canary_battle_off: triggers.append(('canary_battle_not_off', ''))
        if not heroes_ok: triggers.append(('heroes_not_100', ''))
        if not borea_ok: triggers.append(('borea_not_404', ''))
        if not nonal_ok: triggers.append(('non_allowlist_not_423', ''))
        if isinstance(db_inv, int) and db_inv > 0: triggers.append(('inventory_mutation_rows', f'count={db_inv}'))
        if isinstance(db_pts, int) and db_pts > 0: triggers.append(('affinity_points_rows', f'count={db_pts}'))
        if isinstance(db_buf, int) and db_buf > 0: triggers.append(('buffs_rows', f'count={db_buf}'))
        if isinstance(db_btl, int) and db_btl > 0: triggers.append(('battle_rows', f'count={db_btl}'))
        overall = 'PASS_SAFE_BLOCK' if not triggers else 'FAIL'
    elif state == 'ACTIVATED':
        # Future path (V15 does NOT take this). When implemented, this should
        # do a controlled 1-3 spend probe against a seeded Stage1 QA user with
        # known inventory and assert exact deltas. Today, emit FAIL because we
        # never expected ACTIVATED for V15.
        triggers.append(('unexpected_activated_state_in_v15', ''))
        overall = 'FAIL'
    else:
        triggers.append(('unknown_activation_state', f'state={state}'))
        overall = 'FAIL'

    payload = {
        'result_id': 'affinity_inventory_live_monitoring_stage1_result_v1',
        'task_origin': 'AF2-N-INVENTORY-LIVE-MONITORING (Stage1 only)',
        'design_only': False, 'runtime_attached': True,
        'runtime_attached_stage1_allowlist_only': True,
        'db_write': False,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'inventory_activation_state': state,
        'flag_currently_set': flag_on,
        'observed': {
            'canary_inventory_mutation_enabled': (status or {}).get('inventory_mutation_enabled') if isinstance(status, dict) else None,
            'canary_affinity_points_mutation_enabled': (status or {}).get('affinity_points_mutation_enabled') if isinstance(status, dict) else None,
            'canary_buffs_enabled': (status or {}).get('buffs_enabled') if isinstance(status, dict) else None,
            'canary_battle_runtime_attached': (status or {}).get('battle_runtime_attached') if isinstance(status, dict) else None,
            'heroes_count_100': heroes_ok,
            'borea_404': borea_ok,
            'non_allowlist_423': nonal_ok,
            'ledger_inventory_mutated_rows': db_inv,
            'ledger_affinity_points_mutated_rows': db_pts,
            'ledger_buffs_activated_rows': db_buf,
            'ledger_battle_wiring_rows': db_btl,
        },
        'triggers_fired': [{'trigger': t, 'detail': d} for t, d in triggers],
        'triggers_total': len(triggers),
        'overall_status': overall,
        'safety_flags': {
            'runtime_attached_stage1_allowlist_only': True,
            'broad_rollout_authorized': False,
            'inventory_wiring_live': False,
            'inventory_mutation_enabled': False,
            'affinity_points_mutation_enabled': False,
            'buffs_enabled': False,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
            'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Inventory live monitoring: state={state}, overall={overall}, triggers={len(triggers)}')
    return 0 if overall in ('PASS_SAFE_BLOCK','PASS_ACTIVATED') else 1

if __name__ == '__main__':
    sys.exit(main())
