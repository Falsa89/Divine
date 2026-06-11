#!/usr/bin/env python3
"""Pack 102 ROLLUP: tutti i validators Pack 102 in sequenza."""
import os, sys, subprocess
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS=[
    'validate_v110_pack_102_tower_floor_catalog_sot.py',
    'validate_v110_pack_102_hero_id_source_audit.py',
    'validate_v110_pack_102_100_floor_catalog_generation.py',
    'validate_v110_pack_102_catalog_loader_readonly_api.py',
    'validate_v110_pack_102_strict_preview_catalog_wiring.py',
    'validate_v110_pack_102_boss_team_rules_validator.py',
    'validate_v110_pack_102_frontend_catalog_preview_guard.py',
    'validate_v110_pack_102_expansion_policy.py',
    'validate_v110_pack_102_runtime_smoke_e2e.py',
    'validate_v110_pack_102_static_catalog_anti_leak_guard.py',
    'validate_v110_pack_102_data_invariants.py',
    'validate_v110_pack_102_cleanup_rollback.py',
    'validate_v110_pack_102_live_readiness_update.py',
    'validate_v110_pack_102_gate_invariant_preservation.py',
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
    print(f'[v110 MEGA_RELEASE_ACCELERATION_102_ROLLUP] BLOCKED failed={[f[0] for f in failed]}')
    sys.exit(2)
print('[v110 MEGA_RELEASE_ACCELERATION_102_TOWER_100_FLOOR_CATALOG_DETERMINISTIC_ENEMY_TEAMS_ROLLUP] OK all_14_validators_passed 100_floors_deterministic team_bosses_only S1_S2_isolated no_premium no_reward_live pack_91_101_preserved')
print('PUBLIC_SYNC_TAG_v110_TOWER_100_FLOOR_CATALOG_DETERMINISTIC_ENEMY_TEAMS')
