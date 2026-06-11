#!/usr/bin/env python3
"""Pack 100 ROLLUP: esegue tutti i validators del Pack 100 in sequenza."""
import os, sys, subprocess
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS=[
    'validate_v110_pack_100_server_scoped_progress_canon_sot.py',
    'validate_v110_pack_100_daily_quest_event_bus_static.py',
    'validate_v110_pack_100_daily_login_hook.py',
    'validate_v110_pack_100_first_daily_quest_event_mapping.py',
    'validate_v110_pack_100_story_tower_server_scope_audit.py',
    'validate_v110_pack_100_daily_quest_claim_real_player_status.py',
    'validate_v110_pack_100_frontend_daily_task_loop_ui_guard.py',
    'validate_v110_pack_100_runtime_smoke_e2e.py',
    'validate_v110_pack_100_static_server_scope_anti_leak_guard.py',
    'validate_v110_pack_100_legacy_claim_progress_non_regression.py',
    'validate_v110_pack_100_data_invariants.py',
    'validate_v110_pack_100_cleanup_rollback.py',
    'validate_v110_pack_100_live_readiness_update.py',
    'validate_v110_pack_100_gate_invariant_preservation.py',
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
    print(f'[v110 MEGA_RELEASE_ACCELERATION_100_ROLLUP] BLOCKED failed={[f[0] for f in failed]}')
    sys.exit(2)
print('[v110 MEGA_RELEASE_ACCELERATION_100_DAILY_QUEST_GAMEPLAY_COMPLETION_EVENTS_FIRST_REAL_TASK_LOOP_ROLLUP] OK all_14_validators_passed daily_task_loop_S1_real quest_1_real_event_ready quest_2_3_deferred S1_S2_isolated tower_deferred no_premium no_reward_live pack_91_99_preserved')
print('PUBLIC_SYNC_TAG_v110_DAILY_QUEST_GAMEPLAY_COMPLETION_EVENTS_FIRST_REAL_TASK_LOOP')
