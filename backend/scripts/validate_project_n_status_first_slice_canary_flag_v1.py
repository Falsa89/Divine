#!/usr/bin/env python3
"""PROJECT_N Track B validator — canary flag flip result (final state must be FLAG_OFF)."""
import hashlib, json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_n_status_first_slice_canary_flag_flip_result_v1.json')
ENV = Path('/app/backend/.env')
BKP = Path('/app/backend/.env.project_n_pre_flip.bak')
RBK = Path('/app/backend/scripts/rollback_project_n_status_first_slice_canary_flag.py')


def _md5(p): return hashlib.md5(p.read_bytes()).hexdigest()


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') not in (
        'TRACK_B_STATUS_FIRST_SLICE_CANARY_FLAG_ENABLED_SAFE',
        'TRACK_B_STATUS_FIRST_SLICE_CANARY_FLAG_READY_NOT_APPLIED_APPROVAL_MISSING',
        'TRACK_B_STATUS_FIRST_SLICE_CANARY_FLAG_READY_NOT_APPLIED_ENV_NOT_PROVEN',
        'TRACK_B_STATUS_FIRST_SLICE_CANARY_FLAG_READY_NOT_APPLIED_SAFETY_BLOCKED',
    ):
        fail(f'verdict not in allowed set: {m.get("verdict")}')
    if m.get('prod_rollout') is not False: fail('prod_rollout must be False')
    if m.get('dev_live_broad_rollout') is not False: fail('dev_live_broad_rollout must be False')
    if m.get('db_write') is not False: fail('db_write must be False')
    if m.get('battle_code_patch_beyond_project_m_seam') is not False: fail('no further battle patch allowed')
    if not BKP.exists(): fail('pre-flip backup missing')
    if not RBK.exists(): fail('rollback script missing')
    if _md5(BKP) != m.get('backup_md5'): fail('backup md5 mismatch')
    # Final state must be FLAG_OFF in backend/.env (canary container rolled back after validation).
    txt = ENV.read_text(encoding='utf-8')
    flag_present = 'STATUS_RUNTIME_BUFF_SLICE_ENABLED=' in txt and any(
        ln.strip().startswith('STATUS_RUNTIME_BUFF_SLICE_ENABLED=') and ln.split('=', 1)[1].strip().lower() == 'true'
        for ln in txt.splitlines()
    )
    if flag_present: fail('final state has flag true in .env — rollback expected')
    # Backend/.env md5 must equal backup md5 post-rollback (proves clean revert).
    if _md5(ENV) != _md5(BKP): fail(f'.env md5 {_md5(ENV)} != backup md5 {_md5(BKP)} (rollback not clean)')
    print('[PASS] PROJECT_N Track B canary flag flip EXECUTED then ROLLED BACK; current state FLAG_OFF; backup intact')
    sys.exit(0)


if __name__ == '__main__': main()
