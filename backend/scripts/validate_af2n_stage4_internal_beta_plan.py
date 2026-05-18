#!/usr/bin/env python3
"""Validator for Stage4 internal beta PLAN-ONLY (V20)."""
from __future__ import annotations
import json, sys
from pathlib import Path

PLAN = Path('/app/data/design/affinity/af2n_stage4_internal_beta_plan_v1.json')


def main():
    failures=[]
    def rec(n,c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('AF2-N-STAGE4-INTERNAL-BETA-PLAN V20 — Validator'); print('='*70)
    if not PLAN.exists(): rec('plan_present', False); print('Overall: FAIL'); return 1
    d = json.loads(PLAN.read_text())
    rec('plan_id', d.get('plan_id') == 'af2n_stage4_internal_beta_plan_v1')
    rec('design_only_true', d.get('design_only') is True)
    rec('runtime_attached_false', d.get('runtime_attached') is False)
    rec('plan_only_true', d.get('plan_only') is True)
    rec('stage4_applied_false', d.get('stage4_applied') is False)
    rec('broad_rollout_off', d.get('broad_rollout_authorized') is False)
    rec('public_spend_off', d.get('public_spend_ui') is False)
    rec('battle_wiring_off', d.get('battle_wiring') is False)
    rec('target_user_class_internal_only', d.get('target_user_class') == 'internal_QA_engineering_economy_only')
    rec('recommended_users_500_le_1000', 500 <= d.get('recommended_new_users_count', 0) <= d.get('hard_cap_new_users_count', 0))
    rec('hard_cap_users_le_2000', d.get('hard_cap_new_users_count', 99999) <= 2000)
    rec('total_allowlist_hard_cap_le_5000', d.get('hard_cap_total_allowlist_size', 99999) <= 5000)
    rec('ledger_cap_hard_cap_le_50000', d.get('hard_cap_ledger_cap', 99999999) <= 50000)
    rec('seed_strategy_present', isinstance(d.get('seed_strategy'), dict))
    rec('rate_limit_plan_present', isinstance(d.get('rate_limit_plan'), dict))
    rec('abuse_monitoring_present', isinstance(d.get('abuse_monitoring_plan'), dict))
    rec('borea_safety_gates_present', len(d.get('borea_safety_gates', [])) >= 2)
    rec('economy_caps_present', isinstance(d.get('economy_caps_plan'), dict))
    rec('rollback_plan_present', isinstance(d.get('rollback_plan'), dict))
    rec('support_observability_checklist_present', len(d.get('support_observability_checklist', [])) >= 4)
    rec('required_signoffs_v5_listed', len(d.get('required_signoffs_v5', [])) >= 7)
    rec('required_gates_before_apply_listed', len(d.get('required_gates_before_apply', [])) >= 7)
    rec('explicit_status_plan_only', d.get('explicit_status', '').startswith('PLAN_ONLY'))
    rec('safety_invariants_listed', len(d.get('safety_invariants', [])) >= 5)
    rec('abort_triggers_listed', len(d.get('abort_triggers', [])) >= 8)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
