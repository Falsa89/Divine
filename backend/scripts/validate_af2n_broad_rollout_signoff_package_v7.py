#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_broad_rollout_signoff_package_v7.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('broad_rollout_allowed') is not False: print('FAIL: broad'); return 2
    if d.get('public_spend_ui_allowed') is not False: print('FAIL: public_ui'); return 2
    if d.get('stack_g_allowed') is not False: print('FAIL: stack_g'); return 2
    if any((d.get('signoffs') or {}).values()): print('FAIL: signoffs_present'); return 2
    if not d.get('safety', {}).get('plan_only'): print('FAIL: not_plan_only'); return 2
    print('PASS: AF2-N-V29-BROAD-ROLLOUT-SIGNOFF-V7'); return 0
if __name__ == '__main__': sys.exit(main())
