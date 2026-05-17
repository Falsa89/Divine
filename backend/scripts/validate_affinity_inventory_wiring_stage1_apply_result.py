#!/usr/bin/env python3
"""AF2-N-INVENTORY-WIRING ACTIVATE — Apply result validator.

Accepts BOTH outcomes:
  - activation_state == 'READY_NOT_ACTIVATED'  (safe block path)
  - activation_state == 'WOULD_ACTIVATE_NEXT_TASK' (gates pass but not flipped)
  - activation_state == 'ACTIVATED'              (future)
In all cases the result must declare inventory_wiring_live=False today (V15)
and the safety flags must hold.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/affinity_inventory_wiring_stage1_apply_result_v1.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'affinity_inventory_wiring_stage1_apply_result_v1', '')
rec('task', r.get('task_origin') == 'AF2-N-INVENTORY-WIRING ACTIVATE (Stage1 only)', '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('stage1_only', r.get('runtime_attached_stage1_allowlist_only') is True, '')
rec('inventory_live_false', r.get('inventory_wiring_live') is False, '')
rec('activation_applied_false_today', r.get('activation_applied') is False, '')
rec('activation_state_valid',
    r.get('activation_state') in {'READY_NOT_ACTIVATED','WOULD_ACTIVATE_NEXT_TASK','ACTIVATED'}, '')

if r.get('activation_state') == 'READY_NOT_ACTIVATED':
    rec('blocked_by_present', isinstance(r.get('blocked_by'), list) and len(r['blocked_by']) > 0, '')
    rec('remediation_steps_min_3', len(r.get('remediation_steps') or []) >= 3, '')
    rec('flag_currently_off', r.get('flag_currently_set') is False, '')
    rec('preconditions_recorded', isinstance(r.get('preconditions_evaluated'), dict)
        and len(r['preconditions_evaluated']) >= 5, '')

sf = r.get('safety_flags') or {}
for k in ('broad_rollout_authorized','inventory_wiring_live','inventory_mutation_enabled',
          'affinity_points_mutation_enabled','buffs_enabled','battle_runtime_attached','applied_to_combat'):
    rec(f'sf_{k}_false', sf.get(k) is False, '')
rec('sf_stage1_only', sf.get('runtime_attached_stage1_allowlist_only') is True, '')
rec('sf_flag_on', sf.get('feature_flag_currently_enabled') is True, '')

print('='*70); print('AF2-N-INVENTORY-WIRING ACTIVATE — Apply Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
