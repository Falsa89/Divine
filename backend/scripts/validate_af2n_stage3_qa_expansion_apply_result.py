#!/usr/bin/env python3
"""Validator for af2n_stage3_qa_expansion_apply_result_v1.json.
Accepts APPLIED_PASS or READY_NOT_APPLIED with a valid reason.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

RESULT = Path('/app/data/design/affinity/af2n_stage3_qa_expansion_apply_result_v1.json')
VALID = {'APPLIED_PASS', 'READY_NOT_APPLIED'}


def main():
    failures = []
    def rec(n, c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('AF2-N-STAGE3-APPLY-RESULT — Validator'); print('='*70)
    if not RESULT.exists():
        rec('result_present', False); print('Overall: FAIL'); return 1
    d = json.loads(RESULT.read_text())
    status = d.get('overall_status')
    rec('status_known', status in VALID)
    rec('plan_ref', d.get('plan_ref') == 'af2n_stage3_qa_expansion_plan_v1')
    rec('broad_rollout_off', d.get('broad_rollout_authorized') is False)
    rec('public_spend_off', d.get('public_spend_ui') is False)
    sf = d.get('safety_flags', {})
    rec('sf_broad_off', sf.get('broad_rollout_authorized') is False)
    rec('sf_buffs_off', sf.get('buffs_enabled') is False)
    rec('sf_battle_off', sf.get('battle_runtime_attached') is False)
    rec('sf_combat_off', sf.get('applied_to_combat') is False)
    rec('sf_borea_hidden', sf.get('hidden_aliases_blocked') == ['borea','greek_borea','primordial_gaia'])
    rec('user_count_le_200', d.get('stage3_user_count_target', 0) <= 200)
    rec('total_target_le_500', d.get('stage3_total_allowlist_target', 0) <= 500)
    rec('cap_target_le_5000', d.get('stage3_ledger_cap_target', 0) <= 5000)
    if status == 'APPLIED_PASS':
        rec('applied_true', d.get('applied') is True)
        rec('seed_complete', (d.get('seed_inserts',0) + d.get('seed_skips',0)) == 100)
        rec('smoke_ok', d.get('smoke_status_ok') is True)
        sm = d.get('smoke_canary_status', {}) or {}
        rec('smoke_allowlist_le_500', sm.get('canary_allowlist_size', 999) <= 500)
        rec('smoke_cap_le_5000', sm.get('canary_ledger_cap', 999999) <= 5000)
        rec('smoke_battle_off', sm.get('battle_runtime_attached') is False)
        rec('smoke_buffs_off', sm.get('buffs_enabled') is False)
        rec('smoke_combat_off', sm.get('applied_to_combat') is False)
    elif status == 'READY_NOT_APPLIED':
        rec('ready_not_applied_has_reason', bool(d.get('ready_not_applied_reason')))
        rec('not_applied_no_apply_state', d.get('applied') is not True)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
