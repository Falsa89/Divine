#!/usr/bin/env python3
"""Validator for af2n_stage2_5_10pct_apply_result_v1.json.

Accepts BOTH outcomes:
  - APPLIED_PASS: all gates passed AND apply succeeded with safe smoke.
  - READY_NOT_APPLIED: with a valid reason (gates failed or dry-run).

Fails only if:
  - Result missing
  - Result claims APPLIED_PASS but invariants violated
  - Status is unknown/other
"""
from __future__ import annotations
import json, sys
from pathlib import Path

RESULT = Path('/app/data/design/affinity/af2n_stage2_5_10pct_apply_result_v1.json')

VALID_STATUSES = {'APPLIED_PASS', 'READY_NOT_APPLIED'}


def main():
    failures = []
    def rec(n, c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('AF2-N-STAGE2-APPLY-RESULT — Validator'); print('='*70)
    if not RESULT.exists():
        rec('result_present', False); print('Overall: FAIL'); return 1
    data = json.loads(RESULT.read_text())
    status = data.get('overall_status')
    rec('status_known', status in VALID_STATUSES)
    rec('plan_ref', data.get('plan_ref') == 'af2n_stage2_5_10pct_plan_v1')
    rec('broad_rollout_off', data.get('broad_rollout_authorized') is False)
    sf = data.get('safety_flags', {})
    rec('sf_broad_rollout_off', sf.get('broad_rollout_authorized') is False)
    rec('sf_buffs_off', sf.get('buffs_enabled') is False)
    rec('sf_battle_off', sf.get('battle_runtime_attached') is False)
    rec('sf_combat_off', sf.get('applied_to_combat') is False)
    rec('sf_borea_hidden', sf.get('hidden_aliases_blocked') == ['borea','greek_borea','primordial_gaia'])
    rec('stage2_user_count_le_50', data.get('stage2_user_count_target', 0) <= 50)
    rec('stage2_total_target_le_200', data.get('stage2_total_allowlist_target', 0) <= 200)
    rec('stage2_cap_le_1000', data.get('stage2_ledger_cap_target', 0) <= 1000)
    if status == 'APPLIED_PASS':
        rec('applied_true', data.get('applied') is True)
        rec('seed_complete', (data.get('seed_inserts',0) + data.get('seed_skips',0)) == 50)
        rec('smoke_status_ok', data.get('smoke_status_ok') is True)
        sm = data.get('smoke_canary_status', {}) or {}
        rec('smoke_allowlist_size_le_200', sm.get('canary_allowlist_size', 999) <= 200)
        rec('smoke_ledger_cap_le_1000', sm.get('canary_ledger_cap', 99999) <= 1000)
        rec('smoke_battle_off', sm.get('battle_runtime_attached') is False)
        rec('smoke_buffs_off', sm.get('buffs_enabled') is False)
        rec('smoke_combat_off', sm.get('applied_to_combat') is False)
    elif status == 'READY_NOT_APPLIED':
        rec('ready_not_applied_has_reason', bool(data.get('ready_not_applied_reason')))
        rec('not_applied_means_no_smoke_state_change', data.get('applied') is not True)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
