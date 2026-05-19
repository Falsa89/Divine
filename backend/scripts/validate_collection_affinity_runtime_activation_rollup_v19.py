#!/usr/bin/env python3
"""V24 — Validate Safety Rollup S."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v19.json')


def main():
    if not R.exists(): print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    fails = []
    if d.get('rollup_id') != 'collection_affinity_runtime_activation_readiness_rollup_v19':
        fails.append('rollup_id_mismatch')
    for k in ('broad_rollout_authorized','public_spend_ui','battle_wiring_live'):
        if d.get(k) is not False: fails.append(f'inv:{k}')
    if d.get('borea_hidden') is not True: fails.append('borea_not_hidden')
    if d.get('rate_limit_active') is not True: fails.append('rate_limit_inactive')
    if d.get('rollback_ready') is not True: fails.append('rollback_not_ready')
    if d.get('blocker_matrix_v3_status') not in ('NO_GO','GO','CONDITIONAL_GO'):
        fails.append('bad_matrix_status')
    if d.get('redis_rate_limit_state') != 'redis_live_switch_applied_safely':
        fails.append('bad_redis_state')
    if d.get('redis_ha_state') != 'plan_documented_no_live_provision':
        fails.append('bad_ha_state')
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print('PASS: SAFETY-ROLLUP-S (v19)'); return 0


if __name__ == '__main__':
    sys.exit(main())
