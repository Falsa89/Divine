#!/usr/bin/env python3
"""PROJECT_O Track F — rollback / kill-switch for dev-live flag flip.

Mirror of PROJECT_N rollback, targeted at PROJECT_O backup file.
"""
import argparse, hashlib, shutil, subprocess, sys
from pathlib import Path
ENV = Path('/app/backend/.env')
BACKUP = Path('/app/backend/.env.project_o_pre_flip.bak')
FLAG_LINE = 'STATUS_RUNTIME_BUFF_SLICE_ENABLED='


def _md5(p): return hashlib.md5(p.read_bytes()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true')
    args = ap.parse_args(argv)
    print(f'[ROLLBACK PROJECT_O] target: {ENV}')
    if not ENV.exists(): print('[ABORT] .env missing'); return 2
    has_flag = FLAG_LINE in ENV.read_text(encoding='utf-8')
    print(f'[INFO] flag line present: {has_flag}')
    print(f'[INFO] current md5: {_md5(ENV)}')
    if BACKUP.exists(): print(f'[INFO] backup md5:  {_md5(BACKUP)}')
    else: print('[WARN] backup missing')
    if not has_flag: print('[INFO] flag already absent — nothing to do'); return 0
    if not args.apply: print('[DRY-RUN] would restore .env + restart backend'); return 0
    if not BACKUP.exists(): print('[ABORT] cannot --apply without backup'); return 3
    shutil.copy2(BACKUP, ENV)
    print('[OK] .env restored from backup')
    print(f'[INFO] post-restore md5: {_md5(ENV)}')
    proc = subprocess.run(['sudo', 'supervisorctl', 'restart', 'backend'], capture_output=True, text=True, timeout=30)
    print(f'[INFO] supervisor restart rc={proc.returncode}')
    return 0


if __name__ == '__main__': sys.exit(main())
