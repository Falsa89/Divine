#!/usr/bin/env python3
"""PROJECT_S Track G validator — implementation RC gate for future Project T.

Verifica che il gate descriva:
- pacco futuro PROJECT_T_..._SINGLE_POINT_WIRING_CANARY_PACK
- flag proposto STATUS_RUNTIME_SECOND_SLICE_ENABLED OFF default
- golden tests pass, no runtime import, no DoT/CC/Borea, rollback ready
- 6 firme prod required at future Project W
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/project_management/project_s_second_slice_implementation_rc_gate_v1.json')
REQUIRED_PROD_SIGS = {'PROD_ROLLOUT_USER_APPROVAL', 'PROD_ROLLOUT_QA_APPROVAL', 'PROD_ROLLOUT_OPS_APPROVAL', 'PROD_ROLLOUT_ROLLBACK_OWNER_APPROVAL', 'PROD_ROLLOUT_BALANCE_APPROVAL', 'STATUS_RUNTIME_SECOND_SLICE_PROD_OK'}


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_G_SECOND_SLICE_IMPLEMENTATION_RC_GATE_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    if 'PROJECT_T_STATUS_SECOND_SLICE_SINGLE_POINT_WIRING_CANARY_PACK' not in str(m.get('future_pack_id', '')):
        fail(f'future_pack_id must be PROJECT_T_..._SINGLE_POINT_WIRING_CANARY_PACK')
    gr = m.get('gate_requirements') or {}
    for k in ('resolver_golden_tests_pass', 'no_runtime_import_until_project_t', 'flag_off_byte_identical_guard', 'no_dot_or_hard_cc_logic', 'no_borea_marchio_logic', 'rollback_ready'):
        if gr.get(k) is not True:
            fail(f'gate_requirements.{k} must be True')
    if gr.get('proposed_flag') != 'STATUS_RUNTIME_SECOND_SLICE_ENABLED':
        fail('proposed_flag must be STATUS_RUNTIME_SECOND_SLICE_ENABLED')
    if str(gr.get('flag_default', '')).lower() not in ('false', '0', 'off'):
        fail('flag_default must be false')
    declared_sigs = set(m.get('prod_rollout_signatures_required_at_future_w') or [])
    missing = REQUIRED_PROD_SIGS - declared_sigs
    if missing:
        fail(f'prod_rollout_signatures_required_at_future_w missing: {sorted(missing)}')
    if m.get('project_t_implementation_in_this_pack') is not False:
        fail('project_t_implementation_in_this_pack must be False')
    if m.get('db_writes') is not False:
        fail('db_writes must be False')
    print('[PASS] PROJECT_S Track G RC gate READY — Project T pack identified, flag OFF default, 6 prod sigs declared')
    sys.exit(0)


if __name__ == '__main__': main()
