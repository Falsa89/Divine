#!/usr/bin/env python3
"""PROJECT_U Track G validator — dev-live readiness gate for Project V."""
import json, sys
from pathlib import Path

M = Path('/app/data/design/project_management/project_u_second_slice_dev_live_readiness_gate_v1.json')
REQUIRED_PROD_SIGS = {'PROD_ROLLOUT_USER_APPROVAL', 'PROD_ROLLOUT_QA_APPROVAL', 'PROD_ROLLOUT_OPS_APPROVAL', 'PROD_ROLLOUT_ROLLBACK_OWNER_APPROVAL', 'PROD_ROLLOUT_BALANCE_APPROVAL', 'STATUS_RUNTIME_SECOND_SLICE_PROD_OK'}


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_G_SECOND_SLICE_DEV_LIVE_READINESS_GATE_READY': fail('verdict mismatch')
    if 'PROJECT_V_STATUS_SECOND_SLICE_DEV_LIVE_ROLLOUT_PACK' not in str(m.get('next_pack', '')): fail('next_pack must be PROJECT_V_..._DEV_LIVE_ROLLOUT_PACK')
    g = m.get('gate_status') or {}
    for k in ('canary_flag_on_smoke_green', 'canary_light_load_green', 'no_leak_green', 'rollback_green', 'suite_green'):
        if g.get(k) is not True: fail(f'gate_status.{k} must be True')
    if m.get('dev_live_rollout_in_pack_u') is not False: fail('dev_live_rollout_in_pack_u must be False')
    if m.get('prod_explicitly_excluded') is not True: fail('prod_explicitly_excluded must be True')
    declared = set(m.get('required_signatures_at_prod_w') or [])
    missing = REQUIRED_PROD_SIGS - declared
    if missing: fail(f'required_signatures_at_prod_w missing: {sorted(missing)}')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print('[PASS] PROJECT_U Track G dev-live readiness gate READY — 5 gates green, Project V identified, 6 prod sigs declared')
    sys.exit(0)


if __name__ == '__main__': main()
