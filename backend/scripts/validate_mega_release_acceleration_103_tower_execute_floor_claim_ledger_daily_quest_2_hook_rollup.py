#!/usr/bin/env python3
"""Pack 103 ROLLUP."""
import os, sys, subprocess
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS=['validate_v110_pack_103_sot.py','validate_v110_pack_103_reward_source.py','validate_v110_pack_103_execute_endpoint.py','validate_v110_pack_103_daily_quest_2_hook.py','validate_v110_pack_103_static_anti_leak.py','validate_v110_pack_103_runtime_smoke_e2e.py','validate_v110_pack_103_data_invariants.py','validate_v110_pack_103_live_readiness_update.py','validate_v110_pack_103_gate_invariant_preservation.py','validate_v110_pack_103_cleanup_rollback.py']
failed=[]
for s in SCRIPTS:
    rc=subprocess.run(['python3', os.path.join(R,'backend/scripts',s)], capture_output=True, text=True)
    if rc.returncode != 0: failed.append((s, rc.stdout, rc.stderr)); print(f'[FAIL] {s}\n  {rc.stdout[:200]}\n  {rc.stderr[:300]}')
    else: print(f'[PASS] {s}')
if failed: print(f'[v110 MEGA_RELEASE_ACCELERATION_103_ROLLUP] BLOCKED failed={[f[0] for f in failed]}'); sys.exit(2)
print('[v110 MEGA_RELEASE_ACCELERATION_103_TOWER_EXECUTE_FLOOR_CLAIM_LEDGER_DAILY_QUEST_2_HOOK_ROLLUP] OK all_10_validators_passed')
print('PUBLIC_SYNC_TAG_v110_TOWER_EXECUTE_FLOOR_CLAIM_LEDGER_DAILY_QUEST_2_HOOK')
