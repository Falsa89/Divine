#!/usr/bin/env python3
"""SAFETY-ROLLUP-J — Validator for rollup v10."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v10.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('rollup_present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('report_id') == 'collection_affinity_runtime_activation_readiness_rollup_v10', '')
rec('task', r.get('task_origin') == 'SAFETY-ROLLUP-J', '')
rec('supersedes_v9', r.get('supersedes') == 'collection_affinity_runtime_activation_readiness_rollup_v9', '')
rec('design_only_false', r.get('design_only') is False, '')
rec('runtime_stage1_only', r.get('runtime_attached_stage1_allowlist_only') is True, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')

for k in ('product_signoff','engineering_signoff','qa_signoff','economy_balance_signoff','rollback_owner_signoff'):
    rec(f'{k}_true', r.get(k) is True, '')
rec('all_5_signoffs_true', r.get('all_5_operator_signoffs_true') is True, '')
rec('final_user_approval_present', r.get('final_user_runtime_approval_present') is True, '')

rec('af2n_executed', r.get('AF2N_executed') is True, '')
rec('af2n_stage1_applied_pass', r.get('AF2N_stage1_status') == 'APPLIED_PASS', '')
rec('af2n_stage1_extended_mon_pass', r.get('AF2N_stage1_extended_monitoring_status') == 'PASS', '')
rec('inventory_state_valid',
    r.get('inventory_wiring_state') in ('live_stage1_only','ready_not_activated','rolled_back'),
    f"got={r.get('inventory_wiring_state')}")
rec('battle_wiring_live_false', r.get('battle_wiring_live') is False, '')
rec('broad_rollout_off', r.get('broad_rollout_authorized') is False, '')
rec('borea_hidden', r.get('Borea_hidden') is True, '')
rec('rollback_ready', r.get('rollback_ready') is True, '')
rec('next_decision_valid',
    r.get('next_decision') in ('continue_monitoring','inventory_activate_retry','stage2_prep','rollback_required'),
    f"got={r.get('next_decision')}")
rec('decision_stage1_only', r.get('go_no_go_decision') == 'STAGE1_ONLY_NO_BROAD_ROLLOUT', '')
rec('feature_flag_on', r.get('feature_flag_currently_enabled') is True, '')
rec('ledger_within_cap', r.get('ledger_row_count_within_cap') is True, '')
rec('rollback_executed_false', r.get('rollback_executed') is False, '')
rec('inv_mutation_count_recorded', isinstance(r.get('inventory_mutation_count'), int), '')
rec('aff_state_mutation_count_recorded', isinstance(r.get('affinity_state_mutation_count'), int), '')
rec('buff_activation_false', r.get('buff_activation') is False, '')

subs = r.get('subsystems') or {}
for key, expected in [
    ('axis_layer', 'GO'), ('ops_layer', 'GO'),
    ('idempotency_contract', 'LIVE_VERIFIED'),
    ('operator_signoff_v4', 'ALL_TRUE'),
    ('final_user_approval', 'PRESENT'),
    ('af2n_canary', 'SUCCEEDED'),
    ('af2n_stage1_apply', 'APPLIED_PASS'),
    ('af2n_stage1_extended_monitoring', 'PASS'),
    ('af2n_inventory_wiring_live', 'READY_NOT_ACTIVATED'),
    ('af2n_inventory_live_monitoring', 'PASS_SAFE_BLOCK'),
    ('af2n_inventory_rollback', 'READY'),
    ('af2n_stage1_rollback', 'READY'),
    ('battle_runtime', 'NO_GO'),
    ('borea_layer', 'GO'),
    ('k6_live_install', 'READY_NOT_INSTALLED'),
    ('k6_fallback_probe', 'PASS'),
]:
    rec(f'sub_{key}', (subs.get(key) or {}).get('status') == expected,
        f"got={(subs.get(key) or {}).get('status')}")

trig = r.get('abort_triggers_status') or []
rec('triggers_min_10', len(trig) >= 10, '')
rec('no_trigger_fired', all(t.get('triggered') is False for t in trig), '')

st = r.get('runtime_status_at_completion') or {}
rec('rs_heroes_100', st.get('api_heroes_count') == 100, '')
rec('rs_borea_invisible', st.get('borea_visible_in_heroes') is False, '')
rec('rs_spend_default_423', st.get('gift_spend_default_status') == 423, '')
rec('rs_spend_borea_404', st.get('gift_spend_borea_status') == 404, '')
rec('rs_spend_canary_200', st.get('gift_spend_canary_status') == 200, '')
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

print('='*70); print('SAFETY-ROLLUP-J — Validator (rollup v10)'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
