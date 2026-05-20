#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v7.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('broad_rollout_authorized') is not False: print('FAIL: broad'); return 2
    if d.get('public_spend_ui_authorized') is not False: print('FAIL: public_ui'); return 2
    if d.get('summary_by_severity', {}).get('P0', {}).get('open', 1) != 0: print('FAIL: p0'); return 2
    print('PASS: AF2-N-V28-BLOCKER-MATRIX-V7'); return 0
if __name__ == '__main__': sys.exit(main())
