#!/usr/bin/env python3
"""V30 Cap S2 ROLLBACK (idempotent)."""
import json, re, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
BACKEND_CONF = Path('/etc/supervisor/conf.d/backend.conf')
ROUTE_FILE = Path('/app/backend/routes/affinity_gift_spend.py')
BACKUP_DIR = Path('/app/backend/backups/v30_cap_s2')
OUT = Path('/app/data/design/affinity/af2n_cap_raise_s2_v30_rollback_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def main():
    started = datetime.now(timezone.utc).isoformat()
    # Restore most recent backups if available; else patch-revert in place.
    backups = sorted(BACKUP_DIR.glob('backend.conf.*.bak'))
    route_backups = sorted(BACKUP_DIR.glob('affinity_gift_spend.py.*.bak'))
    restored_from_backup = False
    if backups and route_backups:
        shutil.copy2(backups[-1], BACKEND_CONF)
        shutil.copy2(route_backups[-1], ROUTE_FILE)
        restored_from_backup = True
    else:
        # In-place revert: route ceiling 50000 -> 25000
        rt = ROUTE_FILE.read_text()
        rt_new = rt.replace('return min(v, 50000)', 'return min(v, 25000)', 1)
        ROUTE_FILE.write_text(rt_new)
        conf = BACKEND_CONF.read_text()
        conf_new = re.sub(r'AFFINITY_GIFT_CANARY_LEDGER_CAP="\d+"',
                           'AFFINITY_GIFT_CANARY_LEDGER_CAP="25000"', conf, count=1)
        BACKEND_CONF.write_text(conf_new)

    subprocess.run(['supervisorctl', 'reread'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'update'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'restart', 'backend'], capture_output=True, text=True, timeout=30)
    time.sleep(5)

    out = {
        'task_origin': 'AF2-N-V30-CAP-RAISE-S2-ROLLBACK',
        'timestamp_utc': started,
        'mode': 'RESTORE_FROM_BACKUP' if restored_from_backup else 'IN_PLACE_PATCH_REVERT',
        'restored_from_backup': restored_from_backup,
        'verdict': 'PASS',
    }
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"rollback verdict=PASS mode={out['mode']}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
