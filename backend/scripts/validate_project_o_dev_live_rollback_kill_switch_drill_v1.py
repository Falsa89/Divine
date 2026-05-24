#!/usr/bin/env python3
"""PROJECT_O Track F validator — dev-live rollback + kill-switch drill."""
import hashlib, json, subprocess, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_o_dev_live_rollback_kill_switch_drill_v1.json')
RBK = Path('/app/backend/scripts/rollback_project_o_status_first_slice_dev_live_flag.py')
ENV = Path('/app/backend/.env')
BKP = Path('/app/backend/.env.project_o_pre_flip.bak')


def _md5(p): return hashlib.md5(p.read_bytes()).hexdigest()


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_F_DEV_LIVE_ROLLBACK_AND_KILL_SWITCH_DRILL_READY': fail('verdict mismatch')
    if not RBK.exists(): fail('rollback script missing')
    if not BKP.exists(): fail('backup missing')
    if _md5(BKP) != m.get('backup_md5'): fail('backup md5 mismatch')
    txt = ENV.read_text()
    if any(ln.strip().startswith('STATUS_RUNTIME_BUFF_SLICE_ENABLED=') and ln.split('=', 1)[1].strip().lower() == 'true' for ln in txt.splitlines()):
        fail('flag still true in .env')
    proc = subprocess.run(['python3', str(RBK)], capture_output=True, text=True, timeout=30)
    if proc.returncode != 0: fail(f'dry-run rc={proc.returncode}: {proc.stderr or proc.stdout}')
    out = proc.stdout
    if 'nothing to do' not in out and 'DRY-RUN' not in out: fail(f'unexpected dry-run output')
    seq = m.get('drill_sequence') or []
    if len(seq) < 6: fail(f'drill_sequence must have >=6 steps')
    print('[PASS] PROJECT_O Track F rollback + kill-switch READY: 6-step drill recorded; current FLAG_OFF; dry-run rc=0')
    sys.exit(0)


if __name__ == '__main__': main()
