#!/usr/bin/env python3
"""V27 PART B — Rollback Managed Redis switch.

Restores backend.conf from the latest V27 backup and restarts backend.
"""
import json, shutil, subprocess, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

BACKEND_CONF = Path('/etc/supervisor/conf.d/backend.conf')
BACKUP_DIR = Path('/app/backend/backups/v27_switch')


def main():
    backups = sorted(BACKUP_DIR.glob('backend.conf.*.bak'), key=lambda p: p.stat().st_mtime, reverse=True)
    if not backups:
        print('NO_BACKUP_FOUND — cannot rollback')
        return 1
    latest = backups[0]
    shutil.copy2(latest, BACKEND_CONF)
    subprocess.run(['supervisorctl', 'reread'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'update'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'restart', 'backend'], capture_output=True, text=True, timeout=20)
    time.sleep(4)
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=5) as r:
            cs = json.loads(r.read().decode())
    except Exception as e:
        cs = {'error': str(e)[:200]}
    print(f"ROLLED_BACK from {latest.name}; rate_limit_backend={cs.get('rate_limit_backend')}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
