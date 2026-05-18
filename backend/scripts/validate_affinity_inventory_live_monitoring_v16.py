#!/usr/bin/env python3
"""V16 INVENTORY LIVE MONITORING — Validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/affinity_inventory_live_monitoring_v16_result.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'affinity_inventory_live_monitoring_v16_result', '')
rec('task', r.get('task_origin') == 'AF2-N-INVENTORY-LIVE-MONITORING-V16', '')
rec('stage1_only', r.get('runtime_attached_stage1_allowlist_only') is True, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('overall_pass', r.get('overall_status') == 'PASS_ACTIVATED', f"got={r.get('overall_status')}")
rec('triggers_zero', r.get('triggers_total', 99) == 0, f"triggers={r.get('triggers_fired')}")
rec('state_activated', r.get('inventory_activation_state') == 'ACTIVATED', '')

rep = r.get('replay_idempotency') or {}
rec('replay_200', rep.get('replay_code') == 200, '')
rec('replay_idempotent', rep.get('replay_result') == 'idempotent_replay', '')
rec('replay_inv_unchanged', rep.get('inventory_unchanged') is True, '')
rec('replay_aff_unchanged', rep.get('affinity_unchanged') is True, '')

bb = r.get('borea_block') or {}
rec('borea_404', bb.get('code') == 404, '')
rec('borea_rows_unchanged_zero', bb.get('pre_borea_rows') == 0 and bb.get('post_borea_rows') == 0, '')

nb = r.get('non_allowlist_block') or {}
rec('non_allowlist_423', nb.get('code') == 423, '')

ib = r.get('insufficient_block') or {}
rec('insufficient_412', ib.get('code') == 412, '')
rec('insufficient_inv_unchanged', ib.get('inv_unchanged') is True, '')

obs = r.get('observed') or {}
rec('inv_mut_rows_min_3', obs.get('ledger_inventory_mutated_rows', 0) >= 3, '')
rec('aff_mut_rows_min_3', obs.get('ledger_affinity_points_mutated_rows', 0) >= 3, '')
rec('inv_aff_mut_same_count', obs.get('ledger_inventory_mutated_rows') == obs.get('ledger_affinity_points_mutated_rows'), '')
rec('buffs_zero', obs.get('ledger_buffs_activated_rows') == 0, '')
rec('battle_zero', obs.get('ledger_battle_wiring_rows') == 0, '')
rec('no_negative_inventory', obs.get('ledger_negative_inventory_count') == 0, '')

sf = r.get('safety_flags') or {}
for k in ('inventory_wiring_live','inventory_mutation_enabled','affinity_points_mutation_enabled','feature_flag_currently_enabled'):
    rec(f'sf_{k}_true', sf.get(k) is True, '')
for k in ('broad_rollout_authorized','buffs_enabled','battle_runtime_attached','applied_to_combat'):
    rec(f'sf_{k}_false', sf.get(k) is False, '')
rec('sf_stage1_only', sf.get('runtime_attached_stage1_allowlist_only') is True, '')

print('='*70); print('V16 INVENTORY LIVE MONITORING — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
