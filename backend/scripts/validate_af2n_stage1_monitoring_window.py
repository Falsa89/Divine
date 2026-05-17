#!/usr/bin/env python3
"""AF2-N-STAGE1-MONITORING-WINDOW — Validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_stage1_monitoring_window_result_v1.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'af2n_stage1_monitoring_window_result_v1', '')
rec('task', r.get('task_origin') == 'AF2-N-STAGE1-MONITORING-WINDOW', '')
rec('runtime_stage1_only', r.get('runtime_attached_stage1_allowlist_only') is True, '')
rec('db_write_false', r.get('db_write') is False, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('samples_min_30', r.get('samples', 0) >= 30, '')
rec('triggers_zero', r.get('triggers_total', 99) == 0, f"triggers={r.get('triggers_fired')}")
rec('overall_pass', r.get('overall_status') == 'PASS', '')
rec('5xx_zero', r.get('any_5xx_total', 99) == 0, '')
rec('allowlist_observed_50', r.get('observed_allowlist_size_must_be_50') is True, '')
rec('inventory_mut_zero', r.get('ledger_inventory_mutation_count') == 0, '')
rec('points_mut_zero', r.get('ledger_affinity_points_mutation_count') == 0, '')
rec('buffs_zero', r.get('ledger_buffs_activation_count') == 0, '')
rec('battle_wire_zero', r.get('ledger_battle_wiring_count') == 0, '')
rec('borea_hero_zero', r.get('ledger_borea_hero_count') == 0, '')
rec('only_canary_rows', r.get('ledger_total_rows') == r.get('ledger_canary_rows'), '')

cs = r.get('codes') or {}
for label, ok_codes in [('spend_empty',['423']),('spend_borea',['404']),('spend_nonal',['423']),('spend_replay',['200'])]:
    obs = cs.get(label) or {}
    rec(f'codes_{label}_clean', all(k in ok_codes for k in obs.keys()) and bool(obs), f'got {obs}')

sf = r.get('safety_flags') or {}
for k in ('broad_rollout_authorized','inventory_mutation_enabled','affinity_points_mutation_enabled',
          'buffs_enabled','battle_runtime_attached','applied_to_combat'):
    rec(f'sf_{k}_false', sf.get(k) is False, '')
rec('sf_canary_only', sf.get('runtime_attached_stage1_allowlist_only') is True, '')

print('='*70); print('AF2-N-STAGE1-MONITORING-WINDOW — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
