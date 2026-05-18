#!/usr/bin/env python3
"""V21 — Validate Safety Rollup P (v16)."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v16.json')


def main():
    if not R.exists():
        print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    fails = []
    if d.get('rollup_id') != 'collection_affinity_runtime_activation_readiness_rollup_v16':
        fails.append('rollup_id_mismatch')
    for k in ('broad_rollout_authorized', 'public_spend_ui', 'battle_wiring_live'):
        if d.get(k) is not False:
            fails.append(f'invariant_violated:{k}')
    if d.get('borea_hidden') is not True:
        fails.append('borea_not_hidden')
    if d.get('buffs_enabled') is True:
        fails.append('buffs_enabled_true')
    if d.get('stage4_state') not in ('stage4_internal_beta_active_no_broad_rollout', 'stage4_ready_not_applied'):
        fails.append('bad_state')
    if d.get('rollback_ready') is not True:
        fails.append('rollback_not_ready')
    if d.get('rate_limit_active') is not True:
        fails.append('rate_limit_inactive')
    if d.get('db_backup_drill_pass') is not True:
        fails.append('db_backup_drill_not_pass')
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print('PASS: SAFETY-ROLLUP-P (v16)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
