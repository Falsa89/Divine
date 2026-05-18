#!/usr/bin/env python3
"""V22 — Validate Safety Rollup Q (v17)."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v17.json')


def main():
    if not R.exists(): print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    fails = []
    if d.get('rollup_id') != 'collection_affinity_runtime_activation_readiness_rollup_v17':
        fails.append('rollup_id_mismatch')
    for k in ('broad_rollout_authorized','public_spend_ui','battle_wiring_live'):
        if d.get(k) is not False: fails.append(f'inv:{k}')
    if d.get('borea_hidden') is not True: fails.append('borea_not_hidden')
    if d.get('buffs_enabled') is True: fails.append('buffs_enabled_true')
    if d.get('rate_limit_active') is not True: fails.append('rate_limit_inactive')
    if d.get('rollback_ready') is not True: fails.append('rollback_not_ready')
    if d.get('redis_rate_limit_state') not in ('memory_current','redis_ready_not_applied','redis_ready_for_gated_switch','redis_active'):
        fails.append('bad_redis_state')
    if d.get('stage4_state') not in ('stage4_internal_beta_active_no_broad_rollout','stage4_ready_not_applied'):
        fails.append('bad_stage4_state')
    if d.get('blocker_matrix_status') not in ('NO_GO','GO','CONDITIONAL_GO'):
        fails.append('bad_blocker_matrix_status')
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print('PASS: SAFETY-ROLLUP-Q (v17)'); return 0


if __name__ == '__main__':
    sys.exit(main())
