#!/usr/bin/env python3
"""PROJECT_N Track F validator — canary rollback + kill-switch drill."""
import hashlib, json, subprocess, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_n_canary_rollback_kill_switch_drill_v1.json')
RBK = Path('/app/backend/scripts/rollback_project_n_status_first_slice_canary_flag.py')
ENV = Path('/app/backend/.env')
BKP = Path('/app/backend/.env.project_n_pre_flip.bak')


def _md5(p): return hashlib.md5(p.read_bytes()).hexdigest()


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_F_CANARY_ROLLBACK_AND_KILL_SWITCH_DRILL_READY': fail('verdict mismatch')
    if not RBK.exists(): fail('rollback script missing')
    if not BKP.exists(): fail('pre-flip backup missing')
    if _md5(BKP) != m.get('backup_md5'): fail('backup md5 mismatch')
    # Current state must already be FLAG_OFF (drill executed at runtime).
    txt = ENV.read_text()
    if any(ln.strip().startswith('STATUS_RUNTIME_BUFF_SLICE_ENABLED=') and ln.split('=', 1)[1].strip().lower() == 'true' for ln in txt.splitlines()):
        fail('flag still true in .env')
    # Dry-run rollback must succeed.
    proc = subprocess.run(['python3', str(RBK)], capture_output=True, text=True, timeout=30)
    if proc.returncode != 0: fail(f'dry-run rc={proc.returncode}: {proc.stderr or proc.stdout}')
    out = proc.stdout
    # Acceptable outputs: 'nothing to do' (post-rollback) or 'DRY-RUN' marker.
    if 'nothing to do' not in out and 'DRY-RUN' not in out:
        fail(f'unexpected dry-run output: {out[:200]}')
    seq = m.get('drill_sequence') or []
    if len(seq) < 6: fail(f'drill_sequence must have >=6 steps, got {len(seq)}')
    print('[PASS] PROJECT_N Track F rollback + kill-switch drill READY: drill 6 steps recorded; current state FLAG_OFF; dry-run rc=0')
    sys.exit(0)


if __name__ == '__main__': main()
