#!/usr/bin/env python3
"""V14 PREFLIGHT — validator.

Reads /app/data/design/affinity/af2n_v14_preflight_result_v1.json (produced by
the apply script) and asserts every gate required to authorize Stage1 apply.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_v14_preflight_result_v1.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'af2n_v14_preflight_result_v1', '')
rec('task', r.get('task_origin') == 'V14-PREFLIGHT', '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')

gates = r.get('gates') or {}
for gate_name in [
    'api_heroes_count_100', 'api_heroes_no_borea',
    'canary_status_200', 'canary_flag_on', 'canary_ledger_within_cap',
    'canary_only_writes', 'gift_spend_borea_404', 'gift_spend_non_allowlist_423',
    'no_5xx_observed', 'battle_files_unchanged',
    'stage1_plan_present', 'monitoring_window_pass',
    'all_5_operator_signoffs_true', 'final_user_runtime_approval_present',
    'inventory_mutation_count_zero', 'affinity_points_mutation_count_zero',
    'buffs_count_zero', 'battle_wiring_count_zero', 'borea_hero_count_zero',
    'rollback_script_ready', 'suite_post_af2n_pass',
]:
    rec(f'gate:{gate_name}', gates.get(gate_name) is True, f'got={gates.get(gate_name)}')

rec('overall_pass', r.get('overall_status') == 'PASS', '')
rec('stage1_apply_authorized', r.get('stage1_apply_authorized') is True, '')
rec('explicit_user_stage1_approval', r.get('explicit_user_stage1_approval') is True, '')
rec('do_not_apply_today_false', r.get('do_not_apply_today') is False, '')

sf = r.get('safety_flags') or {}
rec('sf_broad_off', sf.get('broad_rollout_authorized') is False, '')
rec('sf_inventory_off', sf.get('inventory_mutation_enabled') is False, '')
rec('sf_battle_off', sf.get('battle_runtime_attached') is False, '')
rec('sf_combat_off', sf.get('applied_to_combat') is False, '')

print('='*70); print('V14 PREFLIGHT — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
