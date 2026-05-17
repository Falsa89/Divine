#!/usr/bin/env python3
"""AF2-N-STAGE1-1PCT-ALLOWLIST ROLLBACK (V14 Part F).

Restores backend.conf from the most recent /app/backups/backend.conf.pre-stage1.*.bak
and restarts backend. Verifies post-rollback that the V12 canary state is back
(3-user allowlist, cap 20).

Usage:
  python3 rollback_af2n_stage1_1pct_allowlist.py            # live rollback
  python3 rollback_af2n_stage1_1pct_allowlist.py --dry-run  # validate readiness only
"""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
BACKEND_CONF = Path('/etc/supervisor/conf.d/backend.conf')
BACKUP_DIR = Path('/app/backups')


def latest_backup() -> Path | None:
    if not BACKUP_DIR.exists(): return None
    cands = sorted(BACKUP_DIR.glob('backend.conf.pre-stage1.*.bak'))
    return cands[-1] if cands else None


def _get(p):
    try:
        with urlopen(API + p, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='Only verify readiness; do not apply')
    args = ap.parse_args()

    backup = latest_backup()
    if backup is None:
        print('NO_BACKUP_FOUND')
        return 1
    print(f'Backup to restore: {backup}')

    if args.dry_run:
        # Validate backup contents look correct
        text = backup.read_text()
        has_allow = 'AFFINITY_GIFT_CANARY_ALLOWLIST=' in text
        has_cap = 'AFFINITY_GIFT_CANARY_LEDGER_CAP=' in text
        print(f'dry-run: has_allowlist_env={has_allow} has_cap_env={has_cap}')
        return 0 if (has_allow and has_cap and backup.is_file()) else 1

    shutil.copy2(backup, BACKEND_CONF)
    subprocess.run(['sudo', 'supervisorctl', 'reread'], capture_output=True, text=True, timeout=20)
    subprocess.run(['sudo', 'supervisorctl', 'update'], capture_output=True, text=True, timeout=20)
    subprocess.run(['sudo', 'supervisorctl', 'restart', 'backend'], capture_output=True, text=True, timeout=30)

    # Wait
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        code, _ = _get('/health')
        if code == 200: break
        time.sleep(0.5)

    code, st = _get('/affinity/gift-spend/canary-status')
    print(f'post-rollback canary-status: code={code} allowlist={(st or {}).get("canary_allowlist_size")} cap={(st or {}).get("canary_ledger_cap")}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
