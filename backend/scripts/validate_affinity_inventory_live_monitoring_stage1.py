#!/usr/bin/env python3
"""AF2-N-INVENTORY-LIVE-MONITORING — Validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/affinity_inventory_live_monitoring_stage1_result_v1.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'affinity_inventory_live_monitoring_stage1_result_v1', '')
rec('task', r.get('task_origin') == 'AF2-N-INVENTORY-LIVE-MONITORING (Stage1 only)', '')
rec('stage1_only', r.get('runtime_attached_stage1_allowlist_only') is True, '')
rec('db_write_false', r.get('db_write') is False, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('overall_pass', r.get('overall_status') in ('PASS_SAFE_BLOCK','PASS_ACTIVATED'), f"got={r.get('overall_status')}")
rec('triggers_zero', r.get('triggers_total', 99) == 0, f"triggers={r.get('triggers_fired')}")
rec('flag_off', r.get('flag_currently_set') is False, '')
rec('state_valid', r.get('inventory_activation_state') in ('READY_NOT_ACTIVATED','ACTIVATED','WOULD_ACTIVATE_NEXT_TASK'), '')

obs = r.get('observed') or {}
rec('obs_canary_inv_off', obs.get('canary_inventory_mutation_enabled') is False, '')
rec('obs_canary_pts_off', obs.get('canary_affinity_points_mutation_enabled') is False, '')
rec('obs_canary_buffs_off', obs.get('canary_buffs_enabled') is False, '')
rec('obs_canary_battle_off', obs.get('canary_battle_runtime_attached') is False, '')
rec('obs_heroes_100', obs.get('heroes_count_100') is True, '')
rec('obs_borea_404', obs.get('borea_404') is True, '')
rec('obs_non_allowlist_423', obs.get('non_allowlist_423') is True, '')
rec('ledger_inv_zero', obs.get('ledger_inventory_mutated_rows') == 0, '')
rec('ledger_pts_zero', obs.get('ledger_affinity_points_mutated_rows') == 0, '')
rec('ledger_buf_zero', obs.get('ledger_buffs_activated_rows') == 0, '')
rec('ledger_btl_zero', obs.get('ledger_battle_wiring_rows') == 0, '')

sf = r.get('safety_flags') or {}
for k in ('broad_rollout_authorized','inventory_wiring_live','inventory_mutation_enabled',
          'affinity_points_mutation_enabled','buffs_enabled','battle_runtime_attached','applied_to_combat'):
    rec(f'sf_{k}_false', sf.get(k) is False, '')
rec('sf_stage1_only', sf.get('runtime_attached_stage1_allowlist_only') is True, '')

print('='*70); print('AF2-N-INVENTORY-LIVE-MONITORING — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
