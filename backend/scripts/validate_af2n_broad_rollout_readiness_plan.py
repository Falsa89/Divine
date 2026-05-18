#!/usr/bin/env python3
"""Validator for broad-rollout readiness PLAN (NEVER applied automatically)."""
from __future__ import annotations
import json, sys
from pathlib import Path

PLAN = Path('/app/data/design/affinity/af2n_broad_rollout_readiness_plan_v1.json')


def main():
    failures=[]
    def rec(n,c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('AF2-N-BROAD-ROLLOUT-READINESS-PLAN V19 — Validator'); print('='*70)
    if not PLAN.exists():
        rec('plan_present', False); print('Overall: FAIL'); return 1
    d = json.loads(PLAN.read_text())
    rec('plan_id', d.get('plan_id') == 'af2n_broad_rollout_readiness_plan_v1')
    rec('design_only_true', d.get('design_only') is True)
    rec('runtime_attached_false', d.get('runtime_attached') is False)
    rec('applied_false', d.get('applied') is False)
    rec('broad_rollout_authorized_false', d.get('broad_rollout_authorized') is False)
    rec('public_spend_disabled_false', d.get('public_spend_enabled') is False)
    rec('battle_wiring_false', d.get('battle_wiring') is False)
    rec('explicit_status_ready_not_applied', d.get('explicit_status') == 'READY_NOT_APPLIED_DESIGN_ONLY')
    rec('gates_listed_min_10', len(d.get('required_gates_before_any_authorization', [])) >= 10)
    rec('staged_rollout_present', isinstance(d.get('staged_rollout_plan'), list) and len(d['staged_rollout_plan']) >= 3)
    rec('rollback_thresholds_present', isinstance(d.get('rollback_thresholds'), dict) and len(d['rollback_thresholds']) >= 4)
    rec('safety_invariants_listed', len(d.get('safety_invariants', [])) >= 5)
    rec('support_plan_present', isinstance(d.get('support_plan'), dict))
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
