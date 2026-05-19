#!/usr/bin/env python3
"""V23 — Validate Broad-Rollout Blocker Matrix V2."""
from __future__ import annotations
import json, sys
from pathlib import Path

M = Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v2.json')
REQ_IDS = [f'BR-{i:03d}' for i in range(1, 13)]


def main():
    if not M.exists(): print(f'FAIL: missing {M}'); return 2
    d = json.loads(M.read_text())
    fails = []
    if d.get('broad_rollout_authorized') is not False: fails.append('broad_rollout_true')
    if d.get('go_no_go_global') != 'NO_GO': fails.append('global_not_no_go')
    if d.get('supersedes') != 'af2n_broad_rollout_blocker_matrix_v1': fails.append('not_supersede_v1')
    blockers = d.get('blockers', [])
    if len(blockers) != 12: fails.append(f'wrong_blocker_count:{len(blockers)}')
    seen = {b.get('blocker_id') for b in blockers}
    missing = set(REQ_IDS) - seen
    if missing: fails.append(f'missing_ids:{sorted(missing)}')
    br001 = next((b for b in blockers if b.get('blocker_id')=='BR-001'), None)
    if not br001 or br001.get('current_status') != 'CONDITIONAL_GO':
        fails.append('BR-001_not_conditional_go')
    for b in blockers:
        for k in ('blocker_id','area','severity','current_status','required_before_broad_rollout','owner','go_no_go'):
            if k not in b:
                fails.append(f'blocker_missing:{b.get("blocker_id","?")}:{k}'); break
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-V23-BROAD-ROLLOUT-BLOCKER-MATRIX-V2'); return 0


if __name__ == '__main__':
    sys.exit(main())
