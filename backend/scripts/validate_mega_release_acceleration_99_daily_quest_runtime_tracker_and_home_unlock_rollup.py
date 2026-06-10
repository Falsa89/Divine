#!/usr/bin/env python3
"""Pack 99 ROLLUP: aggrega tutti i validators del Pack 99 e li esegue in sequenza."""
import os, sys, subprocess
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS=[
    'validate_v110_pack_99_daily_quest_runtime_tracker_sot.py',
    'validate_v110_pack_99_daily_quest_tracker_endpoint.py',
    'validate_v110_pack_99_claim_tracker_enforcement.py',
    'validate_v110_pack_99_reward_payload_preservation.py',
    'validate_v110_pack_99_daily_home_controlled_unlock_static.py',
    'validate_v110_pack_99_frontend_daily_quest_tracker_guard.py',
    'validate_v110_pack_99_runtime_smoke_e2e.py',
    'validate_v110_pack_99_static_anti_leak_guard.py',
    'validate_v110_pack_99_legacy_claim_non_regression.py',
    'validate_v110_pack_99_data_invariants.py',
    'validate_v110_pack_99_cleanup_rollback.py',
    'validate_v110_pack_99_live_readiness_update.py',
    'validate_v110_pack_99_gate_invariant_preservation.py',
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
    print(f'[v110 MEGA_RELEASE_ACCELERATION_99_ROLLUP] BLOCKED failed={[f[0] for f in failed]}')
    sys.exit(2)
print('[v110 MEGA_RELEASE_ACCELERATION_99_DAILY_QUEST_RUNTIME_TRACKER_AND_HOME_UNLOCK_ROLLUP] OK all_13_validators_passed tracker_gated claim_enforced no_double_grant no_premium pack_91_98_preserved')
