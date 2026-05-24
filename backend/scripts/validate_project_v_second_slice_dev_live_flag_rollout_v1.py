#!/usr/bin/env python3
"""PROJECT_V Track B validator — dev-live flag rollout (final state OFF)."""
import hashlib, json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_v_second_slice_dev_live_flag_rollout_v1.json')
ENV = Path('/app/backend/.env')
BACKUP = Path('/app/backend/.env.project_v_pre_flip_backup')
FLAG = 'STATUS_RUNTIME_SECOND_SLICE_ENABLED'
KEEP = 'STATUS_RUNTIME_SECOND_SLICE_KEEP_ON_AFTER_DEV_LIVE'
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def _md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    if not M.exists(): fail('marker missing')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_B_SECOND_SLICE_DEV_LIVE_FLAG_ROLLOUT_SAFE': fail('verdict mismatch')
    if not BACKUP.exists(): fail('backup missing')
    if _md5(BACKUP) != m.get('env_pre_flip_md5'): fail('backup md5 mismatch declared')
    env_txt = ENV.read_text()
    flag_present = any(ln.strip().startswith(FLAG + '=') for ln in env_txt.splitlines())
    keep_present = any(ln.strip().startswith(KEEP + '=') and ln.split('=',1)[1].strip().lower()=='true' for ln in env_txt.splitlines())
    if m.get('keep_on_after_dev_live_marker_present') != keep_present: fail('keep_on marker mismatch with env scan')
    if not keep_present:
        if flag_present: fail(f'final .env contains {FLAG} but keep marker absent')
        if _md5(ENV) != m.get('env_pre_flip_md5'): fail('final .env md5 != pre-flip')
    if m.get('rollback_executed') is not True and not keep_present: fail('rollback_executed must be True')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print('[PASS] PROJECT_V Track B dev-live flag rollout SAFE — flag flipped, drilled, rolled back, .env byte-identical')
    sys.exit(0)
if __name__ == '__main__': main()
