#!/usr/bin/env python3
"""SAFETY-ROLLUP-I — Validator for rollup v9 (post Stage1 apply)."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v9.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('rollup_present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('report_id') == 'collection_affinity_runtime_activation_readiness_rollup_v9', '')
rec('task', r.get('task_origin') == 'SAFETY-ROLLUP-I', '')
rec('supersedes_v8', r.get('supersedes') == 'collection_affinity_runtime_activation_readiness_rollup_v8', '')
rec('design_only_false', r.get('design_only') is False, '')
rec('runtime_stage1_only', r.get('runtime_attached_stage1_allowlist_only') is True, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')

for k in ('product_signoff','engineering_signoff','qa_signoff','economy_balance_signoff','rollback_owner_signoff'):
    rec(f'{k}_true', r.get(k) is True, '')
rec('all_5_signoffs_true', r.get('all_5_operator_signoffs_true') is True, '')
rec('final_user_approval_present', r.get('final_user_runtime_approval_present') is True, '')

rec('af2n_executed', r.get('AF2N_executed') is True, '')
rec('af2n_canary_pass', r.get('AF2N_canary_status') == 'PASS', '')
rec('af2n_stage1_applied_pass', r.get('AF2N_stage1_status') == 'APPLIED_PASS', '')
rec('broad_rollout_off', r.get('AF2N_broad_rollout_authorized') is False, '')
rec('monitoring_pass', r.get('AF2N_monitoring_window_status') == 'PASS', '')
rec('stage1_monitoring_pass', r.get('AF2N_stage1_monitoring_window_status') == 'PASS', '')
rec('inventory_shadow_ready', r.get('AF2N_inventory_wiring_state') == 'SHADOW_ADAPTER_READY_NOT_WIRED', '')
rec('k6_prep3_pass', r.get('k6_live_prep3_status') == 'PASS', '')
rec('stage1_rollback_ready', r.get('stage1_rollback_readiness_status') == 'PASS', '')
rec('decision_stage1_only', r.get('go_no_go_decision') == 'STAGE1_ONLY_NO_BROAD_ROLLOUT', '')
rec('state_stage1_active', r.get('overall_runtime_activation_state') == 'stage1_allowlist_active_no_broad_rollout', '')
rec('feature_flag_on', r.get('feature_flag_currently_enabled') is True, '')
rec('allowlist_50', r.get('stage1_allowlist_size') == 50, f'got={r.get("stage1_allowlist_size")}')
rec('cap_500', r.get('stage1_ledger_cap') == 500, f'got={r.get("stage1_ledger_cap")}')
rec('ledger_within_cap', r.get('ledger_row_count_within_cap') is True, '')
rec('rollback_executed_false', r.get('rollback_executed') is False, '')

subs = r.get('subsystems') or {}
for key, expected in [
    ('axis_layer', 'GO'), ('ops_layer', 'GO'), ('idempotency_contract', 'LIVE_VERIFIED'),
    ('operator_signoff_v4', 'ALL_TRUE'), ('final_user_approval', 'PRESENT'),
    ('af2n_canary', 'SUCCEEDED'), ('af2n_monitoring_window', 'PASS'),
    ('af2n_stage1_apply', 'APPLIED_PASS'),
    ('af2n_stage1_monitoring', 'PASS'),
    ('af2n_inventory_wiring_shadow', 'PASS_SHADOW_READY_NOT_WIRED'),
    ('af2n_stage1_rollback', 'READY'),
    ('battle_runtime', 'NO_GO'),
    ('borea_layer', 'GO'),
    ('k6_live_prep3', 'PASS'),
]:
    rec(f'sub_{key}', (subs.get(key) or {}).get('status') == expected,
        f"got={(subs.get(key) or {}).get('status')}")

trig = r.get('abort_triggers_status') or []
rec('triggers_min_8', len(trig) >= 8, '')
rec('no_trigger_fired', all(t.get('triggered') is False for t in trig), '')

st = r.get('runtime_status_at_completion') or {}
rec('rs_heroes_100', st.get('api_heroes_count') == 100, '')
rec('rs_borea_invisible', st.get('borea_visible_in_heroes') is False, '')
rec('rs_spend_default_423', st.get('gift_spend_default_status') == 423, '')
rec('rs_spend_borea_404', st.get('gift_spend_borea_status') == 404, '')
rec('rs_spend_canary_200', st.get('gift_spend_canary_status') == 200, '')
rec('rs_spend_stage1_200', st.get('gift_spend_stage1_user_status') == 200, '')
rec('rs_no_inventory_mut', st.get('ledger_inventory_mutation_count') == 0, '')
rec('rs_no_points_mut', st.get('ledger_affinity_points_mutation_count') == 0, '')
rec('rs_no_buffs', st.get('ledger_buffs_activation_count') == 0, '')
rec('rs_no_battle', st.get('ledger_battle_wiring_count') == 0, '')
rec('rs_no_borea_hero', st.get('ledger_borea_hero_count') == 0, '')

sf = r.get('safety_flags') or {}
rec('sf_stage1_only', sf.get('runtime_attached_stage1_allowlist_only') is True, '')
rec('sf_broad_off', sf.get('broad_rollout_authorized') is False, '')
rec('sf_stage1_applied', sf.get('stage1_applied') is True, '')
rec('sf_inventory_live_off', sf.get('inventory_wiring_live') is False, '')
rec('sf_inventory_mut_off', sf.get('inventory_mutation_enabled') is False, '')
rec('sf_battle_off', sf.get('battle_runtime_attached') is False, '')
rec('sf_combat_off', sf.get('applied_to_combat') is False, '')
rec('sf_supervisor_ready_not_applied', sf.get('supervisor_wiring_state') == 'READY_NOT_APPLIED', '')

print('='*70); print('SAFETY-ROLLUP-I — Validator (rollup v9)'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
