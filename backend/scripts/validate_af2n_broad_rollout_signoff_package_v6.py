#!/usr/bin/env python3
"""V26 PART E — Validator for broad-rollout signoff V6."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_broad_rollout_signoff_package_v6.json')


def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('status') != 'PLAN_ONLY': print('FAIL: must_be_plan_only'); return 2
    if d.get('broad_rollout_allowed') is True: print('FAIL: broad_must_false'); return 2
    if d.get('public_spend_ui_allowed') is True: print('FAIL: public_ui_must_false'); return 2
    if d.get('STACK_G_allowed') is True: print('FAIL: stackg_must_false'); return 2
    if d.get('final_user_approval_granted') is True: print('FAIL: user_approval_must_false'); return 2
    domains = d.get('domains', [])
    if len(domains) < 8: print('FAIL: insufficient_domains'); return 2
    if any(dom.get('gate_passed') for dom in domains): print('FAIL: no_gate_should_pass_yet'); return 2
    print(f'PASS: AF2-N-V26-BROAD-ROLLOUT-SIGNOFF-PACKAGE-V6 (domains={len(domains)} all blocked)'); return 0


if __name__ == '__main__':
    sys.exit(main())
