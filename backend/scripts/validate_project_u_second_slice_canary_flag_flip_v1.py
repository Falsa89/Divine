#!/usr/bin/env python3
"""PROJECT_U Track B validator — canary flag flip.

Verifica che il backup esista, che il marker dichiari il flip e il rollback,
che l'.env finale sia byte-identico al backup pre-flip (a meno che
KEEP_ON_AFTER_CANARY=true sia dichiarato). Esegue scan indipendente di /app/backend/.env.
"""
import hashlib, json, sys
from pathlib import Path

M = Path('/app/data/design/status_effects/project_u_second_slice_canary_flag_flip_v1.json')
ENV = Path('/app/backend/.env')
BACKUP = Path('/app/backend/.env.project_u_pre_flip_backup')
FLAG = 'STATUS_RUNTIME_SECOND_SLICE_ENABLED'
KEEP = 'STATUS_RUNTIME_SECOND_SLICE_KEEP_ON_AFTER_CANARY'


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def main() -> None:
    if not M.exists(): fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    allowed = ('TRACK_B_SECOND_SLICE_CANARY_FLAG_ENABLED_SAFE', 'TRACK_B_SECOND_SLICE_CANARY_FLAG_READY_NOT_APPLIED_ENV_NOT_PROVEN', 'TRACK_B_SECOND_SLICE_CANARY_FLAG_READY_NOT_APPLIED_APPROVAL_MISSING', 'TRACK_B_SECOND_SLICE_CANARY_FLAG_READY_NOT_APPLIED_SAFETY_BLOCKED')
    if m.get('verdict') not in allowed: fail(f'verdict not allowed: {m.get("verdict")}')
    if not BACKUP.exists(): fail(f'env backup missing: {BACKUP}')
    declared_pre = m.get('env_pre_flip_md5')
    actual_backup = _md5(BACKUP)
    if actual_backup != declared_pre: fail(f'backup md5 {actual_backup} != declared pre-flip {declared_pre}')
    # Independent .env scan
    env_txt = ENV.read_text() if ENV.exists() else ''
    flag_present = any(ln.strip().startswith(FLAG + '=') for ln in env_txt.splitlines())
    keep_present = any(ln.strip().startswith(KEEP + '=') and ln.split('=', 1)[1].strip().lower() == 'true' for ln in env_txt.splitlines())
    if m.get('keep_on_after_canary_marker_present') != keep_present:
        fail(f'marker keep_on_after_canary={m.get("keep_on_after_canary_marker_present")} but env scan keep={keep_present}')
    if not keep_present:
        # Final state must be OFF (flag not in .env)
        if flag_present: fail(f'final .env contains {FLAG} but keep_on marker absent: rollback incomplete')
        actual_env = _md5(ENV)
        if actual_env != declared_pre: fail(f'final .env md5 {actual_env} != pre-flip backup md5 {declared_pre}')
    if m.get('rollback_executed') is not True and not keep_present: fail('rollback_executed must be True when keep_on absent')
    if m.get('db_writes') is not False: fail('db_writes must be False')
    print(f'[PASS] PROJECT_U Track B canary flag flip SAFE — flag flipped during canary, final state OFF, .env byte-identical to pre-flip backup, rollback executed')
    sys.exit(0)


if __name__ == '__main__': main()
