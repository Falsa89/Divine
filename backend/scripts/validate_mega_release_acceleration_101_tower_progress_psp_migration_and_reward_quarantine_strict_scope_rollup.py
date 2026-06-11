#!/usr/bin/env python3
"""Pack 101 ROLLUP: tutti i validators Pack 101 in sequenza."""
import os, sys, subprocess
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS=[
    'validate_v110_pack_101_tower_server_scope_sot.py',
    'validate_v110_pack_101_tower_legacy_path_audit.py',
    'validate_v110_pack_101_tower_psp_progress_schema_loader.py',
    'validate_v110_pack_101_tower_backfill_preflight.py',
    'validate_v110_pack_101_tower_status_strict_endpoint.py',
    'validate_v110_pack_101_tower_battle_progress_strict_preview.py',
    'validate_v110_pack_101_tower_reward_quarantine.py',
    'validate_v110_pack_101_frontend_tower_consumer_guard.py',
    'validate_v110_pack_101_story_daily_tower_cross_validator.py',
    'validate_v110_pack_101_runtime_smoke_e2e.py',
    'validate_v110_pack_101_static_tower_anti_leak_guard.py',
    'validate_v110_pack_101_data_invariants.py',
    'validate_v110_pack_101_cleanup_rollback.py',
    'validate_v110_pack_101_live_readiness_update.py',
    'validate_v110_pack_101_gate_invariant_preservation.py',
]
failed=[]
for s in SCRIPTS:
    rc=subprocess.run(['python3', os.path.join(R,'backend/scripts',s)], capture_output=True, text=True)
    if rc.returncode != 0:
        failed.append((s, rc.stdout, rc.stderr))
        print(f'[FAIL] {s} rc={rc.returncode}\n  STDOUT: {rc.stdout[:200]}\n  STDERR: {rc.stderr[:300]}')
    else:
        print(f'[PASS] {s}')
if failed:
    print(f'[v110 MEGA_RELEASE_ACCELERATION_101_ROLLUP] BLOCKED failed={[f[0] for f in failed]}')
    sys.exit(2)
print('[v110 MEGA_RELEASE_ACCELERATION_101_TOWER_PROGRESS_PSP_MIGRATION_AND_REWARD_QUARANTINE_STRICT_SCOPE_ROLLUP] OK all_15_validators_passed tower_strict_server_scoped reward_quarantined S1_S2_isolated no_users_mutation no_legacy_write pack_91_100_preserved')
print('PUBLIC_SYNC_TAG_v110_TOWER_PROGRESS_PSP_MIGRATION_AND_REWARD_QUARANTINE_STRICT_SCOPE')
