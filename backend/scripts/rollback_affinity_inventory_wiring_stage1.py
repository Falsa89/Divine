#!/usr/bin/env python3
"""AF2-N-INVENTORY-WIRING ROLLBACK (Stage1 only) — V15.

If the dedicated env flag AFFINITY_GIFT_INVENTORY_WRITES_ENABLED was set to
the explicit on value, this script will remove it from
/etc/supervisor/conf.d/backend.conf and restart the backend. Stage1 runtime
(canary allowlist + cap) is preserved.

Usage:
  python3 rollback_affinity_inventory_wiring_stage1.py             # live
  python3 rollback_affinity_inventory_wiring_stage1.py --dry-run    # check only
"""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
BACKEND_CONF = Path('/etc/supervisor/conf.d/backend.conf')
BACKUP_DIR = Path('/app/backups')
FLAG_NAME = 'AFFINITY_GIFT_INVENTORY_WRITES_ENABLED'


def _get(p):
    try:
        with urlopen(API + p, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    if not BACKEND_CONF.exists():
        print('BACKEND_CONF_MISSING'); return 1
    text = BACKEND_CONF.read_text()
    flag_present = re.search(rf'{FLAG_NAME}="[^"]*"', text) is not None

    if args.dry_run:
        # readiness check only
        # We do NOT require flag_present; rollback is a no-op if flag never set.
        print(f'dry-run: flag_present={flag_present}, conf_writable={BACKEND_CONF.is_file()}')
        return 0

    if not flag_present:
        print(f'NO_OP: {FLAG_NAME} not set in backend.conf')
        return 0

    # Backup
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = BACKUP_DIR / f'backend.conf.pre-inv-rollback.{ts}.bak'
    shutil.copy2(BACKEND_CONF, backup)
    # Strip flag
    new_text = re.sub(rf',?{FLAG_NAME}="[^"]*"', '', text)
    BACKEND_CONF.write_text(new_text)
    subprocess.run(['sudo','supervisorctl','reread'], capture_output=True, timeout=20)
    subprocess.run(['sudo','supervisorctl','update'], capture_output=True, timeout=20)
    try:
        subprocess.run(['sudo','supervisorctl','restart','backend'], capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        pass

    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        code, _ = _get('/health')
        if code == 200: break
        time.sleep(0.5)
    code, st = _get('/affinity/gift-spend/canary-status')
    print(f'post-rollback: code={code}, inventory_mutation_enabled={(st or {}).get("inventory_mutation_enabled")}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
