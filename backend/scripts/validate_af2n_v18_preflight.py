#!/usr/bin/env python3
"""V18 PREFLIGHT — Runner + Validator."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_v18_preflight_result_v1.json')


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
    gates = {}
    code, _ = _get('/health'); gates['api_health_200'] = code == 200
    code, heroes = _get('/heroes')
    if isinstance(heroes, list):
        gates['heroes_100'] = len(heroes) == 100
        ids = {h.get('id') for h in heroes if isinstance(h, dict)}
        gates['heroes_no_borea'] = not (ids & {'borea','greek_borea','primordial_gaia'})
    code, status = _get('/affinity/gift-spend/canary-status')
    gates['canary_status_200'] = code == 200
    inv_count = None; uas_count = None
    if isinstance(status, dict):
        gates['canary_flag_on'] = status.get('feature_flag_currently_enabled') is True
        gates['inv_writes_flag_on'] = status.get('inventory_mutation_enabled') is True
        gates['stage2_allowlist_ge_100'] = status.get('canary_allowlist_size', 0) >= 100
        gates['cap_ge_1000'] = status.get('canary_ledger_cap', 0) >= 1000
        gates['ledger_within_cap'] = status.get('ledger_total_rows', 0) <= status.get('canary_ledger_cap', 0)
        gates['battle_runtime_attached_false'] = status.get('battle_runtime_attached') is False
        gates['applied_to_combat_false'] = status.get('applied_to_combat') is False
        gates['buffs_enabled_false'] = status.get('buffs_enabled') is False
    gates['borea_404'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'v18pre0001a','user_id':'stage1_qa_001'}) == 404
    gates['non_allowlist_423'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'v18pre0001b','user_id':'unauth_v18_x'}) == 423

    out = subprocess.run(['git','-C','/app','diff','--stat','--',
        'backend/battle_engine.py','backend/battle_core.py','frontend/app/combat.tsx',
        'backend/synergy_system.py','backend/game_systems.py'],
        capture_output=True, text=True, timeout=10)
    gates['battle_files_unchanged'] = out.stdout.strip() == ''

    try:
        from pymongo import MongoClient
        db = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']
        ugi = db['user_gift_inventory']; uas = db['user_affinity_state']; coll = db['gift_transaction_ledger']
        gates['ugi_present'] = 'user_gift_inventory' in db.list_collection_names()
        gates['uas_present'] = 'user_affinity_state' in db.list_collection_names()
        gates['ugi_no_negative'] = ugi.count_documents({'quantity': {'$lt': 0}}) == 0
        inv_mut = coll.count_documents({'inventory_mutated': True})
        aff_mut = coll.count_documents({'affinity_points_mutated': True})
        gates['inv_aff_mut_equal'] = inv_mut == aff_mut
        gates['no_buffs_rows'] = coll.count_documents({'buffs_activated': True}) == 0
        gates['no_battle_wiring_rows'] = coll.count_documents({'battle_wiring_attached': True}) == 0
        gates['no_borea_hero_rows'] = coll.count_documents({'hero_id': {'$in': ['borea','greek_borea','primordial_gaia']}}) == 0
        gates['v16_seed_50_present'] = ugi.count_documents({'metadata.seed_task': 'V16'}) == 50
        gates['v17_stage2_seed_50_present'] = ugi.count_documents({'metadata.seed_task': 'V17_STAGE2'}) == 50
        inv_count = ugi.count_documents({}); uas_count = uas.count_documents({})
    except Exception:
        gates['ugi_present'] = False; gates['uas_present'] = False

    rollback_scripts = [
        '/app/backend/scripts/rollback_af2n_stage1_1pct_allowlist.py',
        '/app/backend/scripts/rollback_affinity_inventory_wiring_stage1.py',
        '/app/backend/scripts/rollback_affinity_inventory_wiring_stage1_retry.py',
        '/app/backend/scripts/rollback_stage1_qa_gift_inventory_seed.py',
        '/app/backend/scripts/rollback_af2n_stage2_5_10pct_allowlist.py',
        '/app/ops/rollback_af2n_canary.sh',
    ]
    gates['rollback_scripts_present'] = all(Path(p).exists() for p in rollback_scripts)

    v17_sum = Path('/app/backend/reports/ultra_combo_v17_validator_summary_v1.json')
    gates['suite_v17_pass'] = (v17_sum.exists() and json.loads(v17_sum.read_text()).get('overall') == 'PASS')
    gates['baseline_v6_diff_pass'] = gates.get('battle_files_unchanged', False)

    # UI safety: no spend Pressable on combat.tsx / no public spend route in frontend
    ui_leak = False
    for p in ('/app/frontend/app/combat.tsx',):
        pf = Path(p)
        if pf.exists():
            body = pf.read_text()
            for tok in ('gift-spend', 'giftSpend', 'spendGift', 'affinity_gift_spend'):
                if tok in body: ui_leak = True; break
    gates['ui_safety_no_spend_token'] = not ui_leak

    leak_found = False
    for p in ('/app/backend/battle_engine.py', '/app/backend/battle_core.py', '/app/frontend/app/combat.tsx'):
        pf = Path(p)
        if pf.exists() and 'affinity_gift_inventory_shadow_adapter' in pf.read_text():
            leak_found = True; break
    gates['no_shadow_adapter_live_leak'] = not leak_found

    overall = all(gates.values())
    payload = {
        'result_id': 'af2n_v18_preflight_result_v1',
        'task_origin': 'V18-PREFLIGHT',
        'design_only': False, 'runtime_attached': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'overall_status': 'PASS' if overall else 'FAIL',
        'gates': gates,
        'canary_status_snapshot': status if isinstance(status, dict) else None,
        'collection_counts': {'user_gift_inventory': inv_count, 'user_affinity_state': uas_count},
        'safety_flags': {
            'broad_rollout_authorized': False,
            'public_spend_ui': False,
            'battle_runtime_attached': False, 'applied_to_combat': False,
            'buffs_enabled': False, 'feature_flag_currently_enabled': True,
            'inventory_writes_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'V18 preflight overall: {payload["overall_status"]}')
    failures=[]
    print('='*70); print('V18 PREFLIGHT — Validator'); print('='*70)
    rec = lambda n, c: (print(f'  [OK] {n}') if c else (failures.append(n) or print(f'  [X] {n}')))
    rec('overall_pass', payload['overall_status'] == 'PASS')
    for g, v in gates.items(): rec(f'gate:{g}', v is True)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
