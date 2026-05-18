#!/usr/bin/env python3
"""SAFETY-ROLLUP-K — Validator for rollup v11."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v11.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('rollup_present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('report_id') == 'collection_affinity_runtime_activation_readiness_rollup_v11', '')
rec('task', r.get('task_origin') == 'SAFETY-ROLLUP-K', '')
rec('supersedes_v10', r.get('supersedes') == 'collection_affinity_runtime_activation_readiness_rollup_v10', '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('stage1_only', r.get('runtime_attached_stage1_allowlist_only') is True, '')
for k in ('product_signoff','engineering_signoff','qa_signoff','economy_balance_signoff','rollback_owner_signoff'):
    rec(f'{k}_true', r.get(k) is True, '')
rec('all_5_signoffs_true', r.get('all_5_operator_signoffs_true') is True, '')
rec('final_user_approval', r.get('final_user_runtime_approval_present') is True, '')
rec('af2n_stage1_applied_pass', r.get('AF2N_stage1_status') == 'APPLIED_PASS', '')
rec('af2n_stage1_ext_mon_pass', r.get('AF2N_stage1_extended_monitoring_status') == 'PASS', '')
rec('inv_activated', r.get('AF2N_inventory_wiring_state') == 'ACTIVATED_STAGE1_ONLY', '')
rec('inv_schema_applied', r.get('AF2N_inventory_schema_migration_status') == 'APPLIED', '')
rec('inv_seed_50', r.get('AF2N_stage1_qa_seed_status') == 'APPLIED_50_USERS', '')
rec('inv_live_mon_pass', r.get('AF2N_inventory_live_monitoring_status') == 'PASS_ACTIVATED', '')
rec('broad_off', r.get('AF2N_broad_rollout_authorized') is False, '')
rec('battle_wiring_off', r.get('battle_wiring_live') is False, '')
rec('borea_hidden', r.get('Borea_hidden') is True, '')
rec('rollback_ready', r.get('rollback_ready') is True, '')
rec('decision_stage1_inv_live', r.get('go_no_go_decision') == 'STAGE1_INVENTORY_LIVE_NO_BROAD_ROLLOUT', '')
rec('state_stage1_inv_live', r.get('overall_runtime_activation_state') == 'stage1_inventory_live_active_no_broad_rollout', '')
rec('inv_flag_on', r.get('inventory_writes_flag_currently_enabled') is True, '')
rec('inv_flag_value', r.get('inventory_writes_flag_value') == 'true_explicit_affinity_inventory_on', '')
rec('inv_mut_count_min_3', r.get('inventory_mutation_count', 0) >= 3, '')
rec('aff_mut_count_min_3', r.get('affinity_state_mutation_count', 0) >= 3, '')
rec('ledger_within_cap', r.get('ledger_row_count_within_cap') is True, '')
rec('rollback_executed_false', r.get('rollback_executed') is False, '')

subs = r.get('subsystems') or {}
for key, expected in [
    ('axis_layer', 'GO'), ('ops_layer', 'GO'), ('idempotency_contract', 'LIVE_VERIFIED'),
    ('operator_signoff_v4', 'ALL_TRUE'), ('final_user_approval', 'PRESENT'),
    ('af2n_canary', 'SUCCEEDED'), ('af2n_stage1_apply', 'APPLIED_PASS'),
    ('af2n_stage1_extended_monitoring', 'PASS'),
    ('af2n_inventory_schema_migration', 'APPLIED'),
    ('af2n_stage1_qa_seed', 'APPLIED_50'),
    ('af2n_inventory_wiring_live', 'ACTIVATED_STAGE1_ONLY'),
    ('af2n_inventory_live_monitoring', 'PASS_ACTIVATED'),
    ('af2n_inventory_rollback', 'READY'),
    ('af2n_inventory_schema_rollback', 'READY'),
    ('af2n_inventory_seed_rollback', 'READY'),
    ('af2n_stage1_rollback', 'READY'),
    ('battle_runtime', 'NO_GO'), ('borea_layer', 'GO'),
    ('db_layer', 'STAGE1_INVENTORY_LIVE'),
]:
    rec(f'sub_{key}', (subs.get(key) or {}).get('status') == expected, f"got={(subs.get(key) or {}).get('status')}")

trig = r.get('abort_triggers_status') or []
rec('triggers_min_10', len(trig) >= 10, '')
rec('no_trigger_fired', all(t.get('triggered') is False for t in trig), '')

st = r.get('runtime_status_at_completion') or {}
rec('rs_heroes_100', st.get('api_heroes_count') == 100, '')
rec('rs_borea_invisible', st.get('borea_visible_in_heroes') is False, '')
rec('rs_spend_default_423', st.get('gift_spend_default_status') == 423, '')
rec('rs_spend_borea_404', st.get('gift_spend_borea_status') == 404, '')
rec('rs_spend_insufficient_412', st.get('gift_spend_insufficient_inventory_status') == 412, '')
rec('rs_spend_stage1_inv_live_200', st.get('gift_spend_stage1_user_inventory_live_status') == 200, '')
rec('rs_inv_mut_min_3', st.get('ledger_inventory_mutation_count', 0) >= 3, '')
rec('rs_aff_mut_min_3', st.get('ledger_affinity_points_mutation_count', 0) >= 3, '')
rec('rs_no_buffs', st.get('ledger_buffs_activation_count') == 0, '')
rec('rs_no_battle', st.get('ledger_battle_wiring_count') == 0, '')
rec('rs_no_borea_hero', st.get('ledger_borea_hero_count') == 0, '')
rec('rs_ugi_50', st.get('user_gift_inventory_rows') == 50, '')
rec('rs_uas_min_3', st.get('user_affinity_state_rows', 0) >= 3, '')
rec('rs_no_negative_inv', st.get('user_gift_inventory_negative_qty_count') == 0, '')

sf = r.get('safety_flags') or {}
for k in ('inventory_wiring_live','inventory_mutation_enabled','affinity_points_mutation_enabled','feature_flag_currently_enabled','inventory_writes_flag_currently_enabled'):
    rec(f'sf_{k}_true', sf.get(k) is True, '')
for k in ('broad_rollout_authorized','buffs_enabled','battle_runtime_attached','applied_to_combat'):
    rec(f'sf_{k}_false', sf.get(k) is False, '')
rec('sf_stage1_only', sf.get('runtime_attached_stage1_allowlist_only') is True, '')
rec('sf_supervisor_ready_not_applied', sf.get('supervisor_wiring_state') == 'READY_NOT_APPLIED', '')

print('='*70); print('SAFETY-ROLLUP-K — Validator (rollup v11)'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
