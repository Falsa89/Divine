#!/usr/bin/env python3
"""V26 PART I — Validator for Blocker Matrix V5."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v5.json')


def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('broad_rollout_authorized') is not False: print('FAIL: broad_must_false'); return 2
    if d.get('public_spend_ui_authorized') is not False: print('FAIL: public_ui_must_false'); return 2
    ids = {b['id'] for b in d.get('matrix', [])}
    required = {'BLK-A-01', 'BLK-B-03', 'BLK-B-06', 'BLK-B-07', 'BLK-G-01', 'BLK-F-01'}
    missing = required - ids
    if missing: print('FAIL: missing_ids', sorted(missing)); return 2
    p0 = d.get('summary_by_severity', {}).get('P0', {})
    if p0.get('open', 1) != 0: print('FAIL: p0_not_closed'); return 2
    print('PASS: AF2-N-V26-BROAD-ROLLOUT-BLOCKER-MATRIX-V5'); return 0


if __name__ == '__main__':
    sys.exit(main())
