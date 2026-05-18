#!/usr/bin/env python3
"""Validator for Stage4 signoff package V5 (V20).

Must ensure final_user approval is false and stage4_apply_allowed=false.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

PACK = Path('/app/data/design/affinity/af2n_stage4_signoff_package_v5.json')
REQUIRED_OWNERS = ['product_v5','engineering_v5','qa_v5','economy_balance_v5','rollback_owner_v5','security_abuse_v5','support_ops_v5']


def main():
    failures=[]
    def rec(n,c):
        print(f'  [{"OK" if c else "X"}] {n}')
        if not c: failures.append(n)
    print('='*70); print('AF2-N-STAGE4-SIGNOFF-PACKAGE V5 — Validator'); print('='*70)
    if not PACK.exists(): rec('package_present', False); print('Overall: FAIL'); return 1
    d = json.loads(PACK.read_text())
    rec('package_id', d.get('package_id') == 'af2n_stage4_signoff_package_v5')
    rec('design_only_true', d.get('design_only') is True)
    rec('runtime_attached_false', d.get('runtime_attached') is False)
    rec('stage4_apply_allowed_false', d.get('stage4_apply_allowed') is False)
    rec('final_user_approval_false', d.get('final_user_stage4_apply_approval') is False)
    rec('broad_rollout_off', d.get('broad_rollout_authorized') is False)
    rec('public_spend_off', d.get('public_spend_ui') is False)
    rec('battle_wiring_off', d.get('battle_wiring') is False)
    so = d.get('signoffs', {})
    for owner in REQUIRED_OWNERS:
        rec(f'signoff_present:{owner}', owner in so)
        if owner in so:
            rec(f'signoff_blockers_listed:{owner}', isinstance(so[owner].get('blockers'), list))
            rec(f'signoff_evidence_listed:{owner}', isinstance(so[owner].get('evidence_refs'), list) and len(so[owner]['evidence_refs']) >= 1)
            # status NOT GRANTED at this stage — must be PENDING / not PASSED
            rec(f'signoff_status_not_PASSED:{owner}', so[owner].get('status') != 'PASSED')
    fu = so.get('final_user_apply_approval_v5', {})
    rec('final_user_signoff_present', bool(fu))
    rec('final_user_status_NOT_GRANTED', fu.get('status') == 'NOT_GRANTED')
    rec('required_for_apply_listed', len(d.get('required_for_apply', [])) >= 6)
    summ = d.get('global_status_summary', {})
    rec('operator_signoffs_passed_zero', summ.get('operator_signoffs_passed_count') == 0)
    rec('operator_signoffs_total_7', summ.get('operator_signoffs_total') == 7)
    rec('global_apply_disallowed', summ.get('stage4_apply_allowed') is False)
    rec('explicit_status_apply_denied', 'APPLY_DENIED' in d.get('explicit_status',''))
    rec('safety_invariants_listed', len(d.get('safety_invariants', [])) >= 4)
    print('-'*70); print('Overall:', 'PASS' if not failures else 'FAIL')
    return 0 if not failures else 1

if __name__ == '__main__':
    sys.exit(main())
