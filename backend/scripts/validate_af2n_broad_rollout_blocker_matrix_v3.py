#!/usr/bin/env python3
"""V24 — Validate Blocker Matrix V3."""
from __future__ import annotations
import json, sys
from pathlib import Path

M = Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v3.json')
REQ_IDS = [f'BR-{i:03d}' for i in range(1, 13)]


def main():
    if not M.exists(): print(f'FAIL: missing {M}'); return 2
    d = json.loads(M.read_text())
    fails = []
    if d.get('broad_rollout_authorized') is not False: fails.append('broad_rollout_true')
    if d.get('go_no_go_global') != 'NO_GO': fails.append('global_not_no_go')
    if d.get('supersedes') != 'af2n_broad_rollout_blocker_matrix_v2': fails.append('not_supersede_v2')
    blockers = d.get('blockers', [])
    if len(blockers) != 12: fails.append(f'wrong_count:{len(blockers)}')
    seen = {b.get('blocker_id') for b in blockers}
    missing = set(REQ_IDS) - seen
    if missing: fails.append(f'missing_ids:{sorted(missing)}')
    br005 = next((b for b in blockers if b.get('blocker_id')=='BR-005'), None)
    if not br005 or br005.get('current_status') != 'STAGING_REHEARSAL_PASS': fails.append('BR-005_not_staging_pass')
    br006 = next((b for b in blockers if b.get('blocker_id')=='BR-006'), None)
    if not br006 or 'PARTIAL_INSTRUMENTATION' not in br006.get('current_status',''): fails.append('BR-006_not_partial')
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-V24-BLOCKER-MATRIX-V3'); return 0


if __name__ == '__main__':
    sys.exit(main())
