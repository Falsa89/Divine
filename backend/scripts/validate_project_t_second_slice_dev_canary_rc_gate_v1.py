#!/usr/bin/env python3
"""PROJECT_T Track G validator — dev canary RC gate for Project U."""
import json, sys
from pathlib import Path

M = Path('/app/data/design/project_management/project_t_second_slice_dev_canary_rc_gate_v1.json')
ENV = Path('/app/backend/.env')


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_G_SECOND_SLICE_DEV_CANARY_RC_GATE_READY': fail('verdict mismatch')
    if 'PROJECT_U_STATUS_SECOND_SLICE_CANARY_ENV_FLAG_FLIP_PACK' not in str(m.get('next_pack', '')): fail('next_pack must be PROJECT_U_..._CANARY_ENV_FLAG_FLIP_PACK')
    if m.get('env_flag_required_at_next_pack') != 'STATUS_RUNTIME_SECOND_SLICE_ENABLED=true': fail('env_flag_required_at_next_pack mismatch')
    if m.get('prod_explicitly_excluded') is not True: fail('prod_explicitly_excluded must be True')
    if m.get('env_flag_flipped_in_pack_t') is not False: fail('env_flag_flipped_in_pack_t must be False')
    if ENV.exists():
        env_txt = ENV.read_text()
        if any(ln.strip().startswith('STATUS_RUNTIME_SECOND_SLICE_ENABLED=') for ln in env_txt.splitlines()):
            fail('STATUS_RUNTIME_SECOND_SLICE_ENABLED present in /app/backend/.env (Track G forbids env flip)')
    rb = m.get('rollback_target') or {}
    if int(rb.get('rollback_time_target_seconds', 9999)) > 60: fail('rollback_time_target_seconds must be <= 60')
    if 'rollback_method' not in rb or 'rollback_script' not in rb: fail('rollback_target missing method/script')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print('[PASS] PROJECT_T Track G dev canary RC gate READY — Project U identified, env flag NOT flipped, rollback target <= 60s')
    sys.exit(0)


if __name__ == '__main__': main()
