#!/usr/bin/env python3
# Pack 83 - Track G: future execute script skeleton / safety gates.
import os, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(R, 'backend/scripts/apply_v110_psp_user_id_normalization_gated.py')
assert os.path.exists(path)
src = open(path).read()
for must in ('AUTORIZZO_V110_PSP_USER_ID_PHYSICAL_NORMALIZATION_SU_DIVINE_WAIFUS', '--plan-only', '--execute', '--mapping-hash-pin', '--backup-manifest-hash-pin', '--rollback-plan-pin', '--commit-hash-pin', '--target-db', '--batch-id', 'REQUIRED_TARGET_DB = \'divine_waifus\'', 'REFUSED'):
    assert must in src, f'apply script missing token: {must}'
# Default --plan-only mode
rc = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=15)
assert rc.returncode == 0, f'apply script default mode must be plan-only OK; rc={rc.returncode} stderr={rc.stderr}'
assert 'plan_only' in rc.stdout or 'Plan-only' in rc.stdout, f'apply script default not plan-only: {rc.stdout}'
assert '"db_writes": 0' in rc.stdout or 'plan_only' in rc.stdout, 'apply script default must report 0 db writes / plan_only'
# Execute senza pins deve fallire
rc2 = subprocess.run([sys.executable, path, '--execute'], capture_output=True, text=True, timeout=15)
assert rc2.returncode != 0, 'apply --execute without approval must REFUSE'
assert 'REFUSED' in rc2.stdout
print('[v110 PACK_83_FUTURE_EXECUTE_SCRIPT_SAFETY] OK plan_only_default execute_refused_without_approval all_required_gates_present')
