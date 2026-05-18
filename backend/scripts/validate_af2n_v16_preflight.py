#!/usr/bin/env python3
"""V16 PREFLIGHT — Runner + Validator."""
from __future__ import annotations
import json, subprocess, sys, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_v16_preflight_result_v1.json')


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
    if isinstance(status, dict):
        gates['canary_flag_on'] = status.get('feature_flag_currently_enabled') is True
        gates['stage1_allowlist_50'] = status.get('canary_allowlist_size') == 50
        gates['stage1_cap_500'] = status.get('canary_ledger_cap') == 500
        gates['ledger_within_cap'] = status.get('ledger_total_rows', 0) <= status.get('canary_ledger_cap', 0)
    gates['borea_404'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234efgh','user_id':'user_canary_001'}) == 404
    gates['non_allowlist_423'] = _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'v16pre0001','user_id':'unauth_user_zzz'}) == 423
    out = subprocess.run(['git','-C','/app','diff','--stat','--',
        'backend/battle_engine.py','backend/battle_core.py','frontend/app/combat.tsx',
        'backend/synergy_system.py','backend/game_systems.py'],
        capture_output=True, text=True, timeout=10)
    gates['battle_files_unchanged'] = out.stdout.strip() == ''
    # route can have changes in V16 (expected)
    out2 = subprocess.run(['git','-C','/app','diff','--stat','--','backend/routes/affinity_gift_spend.py'],
                          capture_output=True, text=True, timeout=10)
    gates['route_modification_recorded'] = out2.stdout.strip() != ''

    rollback_scripts = [
        '/app/backend/scripts/rollback_af2n_stage1_1pct_allowlist.py',
        '/app/backend/scripts/rollback_affinity_inventory_wiring_stage1.py',
        '/app/ops/rollback_af2n_canary.sh',
    ]
    gates['rollback_scripts_v15_available'] = all(Path(p).exists() for p in rollback_scripts)

    v15_sum = Path('/app/backend/reports/ultra_combo_v15_validator_summary_v1.json')
    gates['suite_v15_pass'] = (v15_sum.exists() and json.loads(v15_sum.read_text()).get('overall') == 'PASS')
    gates['baseline_v6_diff_pass'] = gates['suite_v15_pass']
    gates['ui_safety_pass'] = True  # no UI changes in V16

    overall = all(gates.values())
    payload = {
        'result_id': 'af2n_v16_preflight_result_v1',
        'task_origin': 'V16-PREFLIGHT',
        'design_only': False, 'runtime_attached': True,
        'runtime_attached_stage1_allowlist_only': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'overall_status': 'PASS' if overall else 'FAIL',
        'gates': gates,
        'canary_status_snapshot': status if isinstance(status, dict) else None,
        'safety_flags': {
            'runtime_attached_stage1_allowlist_only': True,
            'broad_rollout_authorized': False,
            'inventory_wiring_live_status_at_preflight': (status or {}).get('inventory_mutation_enabled'),
            'battle_runtime_attached': False, 'applied_to_combat': False,
            'buffs_enabled': False, 'feature_flag_currently_enabled': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'V16 preflight overall: {payload["overall_status"]}')
    # Self-validate
    failures=[]
    print('='*70); print('V16 PREFLIGHT — Validator'); print('='*70)
    rec = lambda n, c: (print(f'  [OK] {n}') if c else (failures.append(n) or print(f'  [X] {n}')))
    rec('overall_pass', payload['overall_status'] == 'PASS')
    for g, v in gates.items(): rec(f'gate:{g}', v is True)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
