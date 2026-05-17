#!/usr/bin/env python3
"""V15 PREFLIGHT — validator.

Reads /app/data/design/affinity/af2n_v15_preflight_result_v1.json (produced
by the V15 apply driver or any preflight runner) and asserts every gate.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_v15_preflight_result_v1.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'af2n_v15_preflight_result_v1', '')
rec('task', r.get('task_origin') == 'V15-PREFLIGHT', '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')

gates = r.get('gates') or {}
for g in ['api_health_200','api_heroes_count_100','api_heroes_no_borea',
          'canary_status_200','canary_flag_on','stage1_allowlist_50','stage1_cap_500',
          'ledger_within_cap','canary_only_writes','gift_spend_borea_404',
          'gift_spend_non_allowlist_423','no_5xx_observed','battle_files_unchanged',
          'inventory_mutation_count_zero','affinity_points_mutation_count_zero',
          'buffs_count_zero','battle_wiring_count_zero','borea_hero_count_zero',
          'rollback_script_stage1_ready','rollback_script_canary_ready',
          'baseline_v6_diff_pass','suite_post_af2n_pass','ui_safety_pass',
          'user_gift_inventory_collection_present_or_safely_blocked']:
    rec(f'gate:{g}', gates.get(g) is True, f'got={gates.get(g)}')

rec('overall_pass', r.get('overall_status') == 'PASS', '')
sf = r.get('safety_flags') or {}
rec('sf_broad_off', sf.get('broad_rollout_authorized') is False, '')
rec('sf_inventory_live_off', sf.get('inventory_wiring_live') is False, '')
rec('sf_battle_off', sf.get('battle_runtime_attached') is False, '')
rec('sf_combat_off', sf.get('applied_to_combat') is False, '')
rec('sf_stage1_active', sf.get('stage1_applied') is True, '')

print('='*70); print('V15 PREFLIGHT — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
