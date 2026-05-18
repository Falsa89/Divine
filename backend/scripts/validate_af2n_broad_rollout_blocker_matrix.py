#!/usr/bin/env python3
"""V22 — Validate Broad-Rollout Blocker Matrix."""
from __future__ import annotations
import json, sys
from pathlib import Path

M = Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v1.json')
REQ_AREAS = {
    'rate_limit','observation_window','public_spend_ui','borea_safety',
    'rollback_drills','abuse_monitoring','support_ops_runbook',
    'economy_caps_simulation','locust_extended','db_backup_restore_rehearsal',
    'stack_g_battle_wiring','final_user_signoff_v6',
}


def main():
    if not M.exists(): print(f'FAIL: missing {M}'); return 2
    d = json.loads(M.read_text())
    fails = []
    if d.get('broad_rollout_authorized') is not False: fails.append('broad_rollout_true')
    if d.get('go_no_go_global') != 'NO_GO': fails.append('global_not_no_go')
    blockers = d.get('blockers', [])
    if len(blockers) < 12: fails.append(f'too_few_blockers:{len(blockers)}')
    seen_areas = {b.get('area') for b in blockers}
    missing = REQ_AREAS - seen_areas
    if missing: fails.append(f'missing_areas:{missing}')
    for b in blockers:
        for k in ('blocker_id','area','current_status','severity','required_before_broad_rollout','owner','evidence_needed','current_evidence','next_task','go_no_go'):
            if k not in b:
                fails.append(f'blocker_missing_field:{b.get("blocker_id","?")}:{k}'); break
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-V22-BROAD-ROLLOUT-BLOCKER-MATRIX')
    return 0


if __name__ == '__main__':
    sys.exit(main())
