#!/usr/bin/env python3
"""V27 PART D — Rollback cap S1."""
import shutil, subprocess, sys, time, urllib.request, json
from pathlib import Path

BACKEND_CONF = Path('/etc/supervisor/conf.d/backend.conf')
BACKUP_DIR = Path('/app/backend/backups/v27_cap_s1')


def main():
    backups = sorted(BACKUP_DIR.glob('backend.conf.*.bak'), key=lambda p: p.stat().st_mtime, reverse=True)
    if not backups: print('NO_BACKUP'); return 1
    shutil.copy2(backups[0], BACKEND_CONF)
    subprocess.run(['supervisorctl', 'reread'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'update'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'restart', 'backend'], capture_output=True, text=True, timeout=20)
    time.sleep(4)
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=5) as r:
            cs = json.loads(r.read().decode())
        print(f"ROLLED_BACK; canary_ledger_cap={cs.get('canary_ledger_cap')}")
    except Exception as e:
        print(f'rollback done; canary unreachable: {e}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
