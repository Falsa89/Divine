#!/usr/bin/env python3
"""PROJECT_N Track F — rollback / kill-switch for the canary flag flip.

This script removes the line `STATUS_RUNTIME_BUFF_SLICE_ENABLED=true` from
`/app/backend/.env` (if present) and restarts the backend supervisor.
In dry-run mode (default) it only inspects the file and reports what it
would do, without modifying anything.

PRECONDITION: `/app/backend/.env.project_n_pre_flip.bak` must exist (backup).

Usage:
    python3 rollback_project_n_status_first_slice_canary_flag.py            # inspect
    python3 rollback_project_n_status_first_slice_canary_flag.py --apply    # restore + restart
"""
import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

ENV_FILE = Path('/app/backend/.env')
BACKUP = Path('/app/backend/.env.project_n_pre_flip.bak')
FLAG_LINE = 'STATUS_RUNTIME_BUFF_SLICE_ENABLED='


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='Actually remove flag and restart backend')
    args = ap.parse_args(argv)

    print(f'[ROLLBACK PROJECT_N] target: {ENV_FILE}')
    if not ENV_FILE.exists():
        print('[ABORT] backend/.env missing')
        return 2
    content = ENV_FILE.read_text(encoding='utf-8')
    has_flag = FLAG_LINE in content
    print(f'[INFO] flag line present: {has_flag}')
    print(f'[INFO] current md5: {_md5(ENV_FILE)}')
    if BACKUP.exists():
        print(f'[INFO] backup md5:  {_md5(BACKUP)}')
    else:
        print('[WARN] backup file missing; manual rollback only')

    if not has_flag:
        print('[INFO] flag already absent — nothing to do')
        return 0
    if not args.apply:
        print('[DRY-RUN] would restore .env from backup and restart backend (pass --apply to execute)')
        return 0

    if not BACKUP.exists():
        print('[ABORT] cannot --apply without backup')
        return 3
    shutil.copy2(BACKUP, ENV_FILE)
    print('[OK] .env restored from backup')
    print(f'[INFO] post-restore md5: {_md5(ENV_FILE)}')
    # Restart backend to load env.
    proc = subprocess.run(['sudo', 'supervisorctl', 'restart', 'backend'], capture_output=True, text=True, timeout=30)
    print(f'[INFO] supervisor restart rc={proc.returncode}')
    print(proc.stdout.strip())
    if proc.stderr.strip():
        print(proc.stderr.strip())
    return 0


if __name__ == '__main__':
    sys.exit(main())
