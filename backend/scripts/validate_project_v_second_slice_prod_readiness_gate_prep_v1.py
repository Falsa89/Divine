#!/usr/bin/env python3
"""PROJECT_V Track G validator — prod readiness gate prep for Project W."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/project_management/project_v_second_slice_prod_readiness_gate_prep_v1.json')
REQ = {'PROD_ROLLOUT_USER_APPROVAL','PROD_ROLLOUT_QA_APPROVAL','PROD_ROLLOUT_OPS_APPROVAL','PROD_ROLLOUT_ROLLBACK_OWNER_APPROVAL','PROD_ROLLOUT_BALANCE_APPROVAL','STATUS_RUNTIME_SECOND_SLICE_PROD_OK'}
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    if not M.exists(): fail('marker missing')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_G_SECOND_SLICE_PROD_READINESS_GATE_PREP_READY': fail('verdict mismatch')
    if 'PROJECT_W_STATUS_SECOND_SLICE_PROD_ROLLOUT_PACK' not in str(m.get('next_pack', '')): fail('next_pack must be PROJECT_W_...')
    if m.get('prod_rollout_in_pack_v') is not False: fail('prod_rollout_in_pack_v must be False')
    if m.get('prod_explicitly_excluded') is not True: fail('prod_explicitly_excluded must be True')
    g = m.get('gate_status') or {}
    for k in ('canary_smoke_green', 'canary_load_green', 'dev_live_behavior_regression_green', 'dev_live_extended_load_green', 'no_leak_green', 'rollback_green', 'suite_green'):
        if g.get(k) is not True: fail(f'gate_status.{k} must be True')
    declared = set(m.get('required_signatures_at_pack_w') or [])
    if REQ - declared: fail(f'missing prod signatures: {sorted(REQ - declared)}')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print('[PASS] PROJECT_V Track G prod readiness gate prep READY — 7 gates green, Project W identified, 6 prod sigs declared')
    sys.exit(0)
if __name__ == '__main__': main()
