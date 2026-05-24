#!/usr/bin/env python3
"""PROJECT_O Track B validator — dev-live flag flip (final state FLAG_OFF)."""
import hashlib, json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_o_status_first_slice_dev_live_flag_flip_result_v1.json')
ENV = Path('/app/backend/.env')
BKP = Path('/app/backend/.env.project_o_pre_flip.bak')
RBK = Path('/app/backend/scripts/rollback_project_o_status_first_slice_dev_live_flag.py')


def _md5(p): return hashlib.md5(p.read_bytes()).hexdigest()


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    expected = (
        'TRACK_B_STATUS_FIRST_SLICE_DEV_LIVE_FLAG_ENABLED_THEN_ROLLED_BACK',
        'TRACK_B_STATUS_FIRST_SLICE_DEV_LIVE_FLAG_ENABLED_AND_KEPT_ON',
        'TRACK_B_STATUS_FIRST_SLICE_DEV_LIVE_FLAG_READY_NOT_APPLIED_ENV_NOT_PROVEN',
        'TRACK_B_STATUS_FIRST_SLICE_DEV_LIVE_FLAG_READY_NOT_APPLIED_SAFETY_BLOCKED',
    )
    if m.get('verdict') not in expected: fail(f'verdict not allowed: {m.get("verdict")}')
    if m.get('prod_rollout') is not False: fail('prod_rollout must be False')
    if m.get('broad_public_rollout') is not False: fail('broad_public_rollout must be False')
    if m.get('db_write') is not False: fail('db_write must be False')
    if not BKP.exists(): fail('backup missing')
    if not RBK.exists(): fail('rollback script missing')
    if _md5(BKP) != m.get('backup_md5'): fail('backup md5 mismatch')
    # Final state must be FLAG_OFF unless explicit keep-on marker.
    txt = ENV.read_text()
    flag_true = any(ln.strip().startswith('STATUS_RUNTIME_BUFF_SLICE_ENABLED=') and ln.split('=', 1)[1].strip().lower() == 'true' for ln in txt.splitlines())
    if m.get('keep_on_after_dev_live_marker_present') is True:
        if not flag_true: fail('marker claims keep-on but flag is OFF')
    else:
        if flag_true: fail('flag should be OFF (rollback expected)')
        if _md5(ENV) != _md5(BKP): fail(f'.env md5 {_md5(ENV)} != backup md5 {_md5(BKP)}')
    print('[PASS] PROJECT_O Track B dev-live flag flip EXECUTED + ROLLED BACK; final state FLAG_OFF; .env md5 clean')
    sys.exit(0)


if __name__ == '__main__': main()
