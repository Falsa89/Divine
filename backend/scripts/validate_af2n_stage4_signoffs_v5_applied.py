#!/usr/bin/env python3
"""V21 — Validate Stage4 signoffs V5 applied file."""
from __future__ import annotations
import json, sys
from pathlib import Path

PKG = Path('/app/data/design/affinity/af2n_stage4_signoff_package_v5_applied.json')
REQUIRED_OPS = ['product_v5', 'engineering_v5', 'qa_v5', 'economy_balance_v5',
                'rollback_owner_v5', 'security_abuse_v5', 'support_ops_v5']


def main():
    if not PKG.exists():
        print(f'FAIL: missing {PKG}')
        return 2
    d = json.loads(PKG.read_text())
    fails = []
    if d.get('package_id') != 'af2n_stage4_signoff_package_v5_applied':
        fails.append('package_id_mismatch')
    sg = d.get('signoffs', {})
    for op in REQUIRED_OPS:
        s = sg.get(op, {})
        if s.get('status') != 'PASSED':
            fails.append(f'op_not_passed:{op}')
        if not s.get('approver_signature'):
            fails.append(f'op_no_signature:{op}')
        if not s.get('date_utc'):
            fails.append(f'op_no_date:{op}')
    fu = sg.get('final_user_apply_approval_v5', {})
    if fu.get('status') != 'PASSED':
        fails.append('final_user_not_passed')
    if d.get('stage4_apply_allowed') is not True:
        fails.append('apply_not_allowed')
    if d.get('final_user_stage4_apply_approval') is not True:
        fails.append('final_user_flag_false')
    summ = d.get('global_status_summary', {})
    if summ.get('operator_signoffs_passed_count') != 7:
        fails.append('op_passed_count_not_7')
    # safety invariants must still be false
    if d.get('broad_rollout_authorized') is not False:
        fails.append('broad_rollout_true')
    if d.get('public_spend_ui') is not False:
        fails.append('public_spend_ui_true')
    if d.get('battle_wiring') is not False:
        fails.append('battle_wiring_true')
    if fails:
        for f in fails:
            print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-STAGE4-SIGNOFFS-V5-APPLIED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
