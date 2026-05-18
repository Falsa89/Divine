#!/usr/bin/env python3
"""AF2-N-INVENTORY-WIRING-STAGE1-RETRY APPLY — Validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/affinity_inventory_wiring_stage1_retry_apply_result_v1.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'affinity_inventory_wiring_stage1_retry_apply_result_v1', '')
rec('task', r.get('task_origin') == 'AF2-N-INVENTORY-WIRING-STAGE1-RETRY APPLY', '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('stage1_only', r.get('runtime_attached_stage1_allowlist_only') is True, '')
rec('activated', r.get('activation_state') == 'ACTIVATED', f"state={r.get('activation_state')}")
rec('flag_on', r.get('flag_currently_on') is True, '')
rec('flag_value', r.get('flag_value') == 'true_explicit_affinity_inventory_on', f"got={r.get('flag_value')}")
rec('schema_ready', r.get('schema_ready') is True, '')
rec('seed_count_50', r.get('seed_count_stage1_v16') == 50, f"got={r.get('seed_count_stage1_v16')}")
rec('backup_present', isinstance(r.get('backup_path_pre_flag'), str)
    and r.get('backup_path_pre_flag','').startswith('/app/backups/'), '')

cs = r.get('canary_status_post_activation') or {}
rec('cs_inv_enabled', cs.get('inventory_mutation_enabled') is True, '')
rec('cs_pts_enabled', cs.get('affinity_points_mutation_enabled') is True, '')
rec('cs_buffs_off', cs.get('buffs_enabled') is False, '')
rec('cs_battle_off', cs.get('battle_runtime_attached') is False, '')
rec('cs_combat_off', cs.get('applied_to_combat') is False, '')
rec('cs_allowlist_50', cs.get('canary_allowlist_size') == 50, '')

rec('ledger_inv_mut_rows_min_3', r.get('observed_ledger_inventory_mut_rows', 0) >= 3, '')
rec('ledger_aff_mut_rows_min_3', r.get('observed_ledger_affinity_mut_rows', 0) >= 3, '')

sf = r.get('safety_flags') or {}
for k in ('inventory_wiring_live','inventory_mutation_enabled','affinity_points_mutation_enabled'):
    rec(f'sf_{k}_true', sf.get(k) is True, '')
for k in ('broad_rollout_authorized','buffs_enabled','battle_runtime_attached','applied_to_combat'):
    rec(f'sf_{k}_false', sf.get(k) is False, '')
rec('sf_stage1_only', sf.get('runtime_attached_stage1_allowlist_only') is True, '')

print('='*70); print('V16 INVENTORY RETRY APPLY — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
