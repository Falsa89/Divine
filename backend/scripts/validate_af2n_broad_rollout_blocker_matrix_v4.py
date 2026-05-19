#!/usr/bin/env python3
"""V25 PART G — Validator for Blocker Matrix V4."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v4.json')


def main():
    if not P.exists(): print('FAIL: matrix_missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: matrix_verdict'); return 2
    if d.get('broad_rollout_authorized') is not False: print('FAIL: broad_rollout_must_be_false'); return 2
    if d.get('public_spend_ui_authorized') is not False: print('FAIL: public_spend_ui_must_be_false'); return 2
    if not d.get('p0_all_closed'): print('FAIL: p0_not_all_closed'); return 2
    ids = {b['id'] for b in d.get('matrix', [])}
    required = {'BLK-A-01','BLK-A-02','BLK-A-03','BLK-B-01','BLK-B-03','BLK-D-01','BLK-D-02','BLK-E-01'}
    missing = required - ids
    if missing: print('FAIL: missing_ids', sorted(missing)); return 2
    print('PASS: AF2-N-V25-BROAD-ROLLOUT-BLOCKER-MATRIX-V4'); return 0


if __name__ == '__main__':
    sys.exit(main())
