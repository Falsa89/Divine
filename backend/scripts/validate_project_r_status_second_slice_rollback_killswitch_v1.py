#!/usr/bin/env python3
"""PROJECT_R Track F validator — rollback + kill-switch design.

Verifica che il flag futuro NON sia stato creato in .env live, che la strategia kill-switch
sia single-env-var-flip, che il path stadiato sia presente, che le firme prod siano richieste.
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/status_effects/project_r_status_second_slice_rollback_killswitch_v1.json')
ENV = Path('/app/backend/.env')
FLAG_NAME = 'STATUS_RUNTIME_SECOND_SLICE_ENABLED'


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_F_STATUS_SECOND_SLICE_ROLLBACK_AND_KILL_SWITCH_DESIGN_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    pf = m.get('proposed_future_flag') or {}
    if pf.get('name') != FLAG_NAME:
        fail(f'proposed_future_flag.name must be {FLAG_NAME}')
    if pf.get('default') is not False:
        fail('proposed_future_flag.default must be False')
    if pf.get('persisted_in_live_env_in_this_pack') is not False:
        fail('proposed_future_flag.persisted_in_live_env_in_this_pack must be False')
    # Independent scan: ensure flag is NOT in backend/.env
    if ENV.exists():
        env_txt = ENV.read_text()
        if any(ln.strip().startswith(FLAG_NAME + '=') for ln in env_txt.splitlines()):
            fail(f'forbidden: {FLAG_NAME} found in backend/.env (must NOT be persisted in design pack)')
    ks = m.get('kill_switch_strategy') or {}
    if ks.get('single_env_var_flip') is not True:
        fail('kill_switch_strategy.single_env_var_flip must be True')
    if int(ks.get('rollback_time_target_seconds', 9999)) > 60:
        fail('rollback_time_target_seconds must be <= 60')
    if ks.get('requires_db_revert') is not False or ks.get('requires_redeploy') is not False:
        fail('rollback must not require DB revert or redeploy')
    if len(m.get('staged_rollout_path') or []) < 6:
        fail('staged_rollout_path must have at least 6 stages')
    if len(m.get('no_persistent_enable_without_signatures') or []) < 5:
        fail('no_persistent_enable_without_signatures must list >= 5 required prod signatures')
    if m.get('env_flag_created_in_live_env') is not False or m.get('db_writes') is not False:
        fail('env_flag_created_in_live_env / db_writes must be False')
    print(f'[PASS] PROJECT_R Track F rollback + kill-switch READY — {FLAG_NAME} NOT in .env, single-env-var-flip, prod gated')
    sys.exit(0)


if __name__ == '__main__':
    main()
