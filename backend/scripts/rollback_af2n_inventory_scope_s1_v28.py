#!/usr/bin/env python3
"""V28 PART B — Rollback inventory scope S1.

Deletes ONLY seed documents with marker meta.v28_scope_s1=true. Restores
backend.conf from the latest V28 backup. Safe: production data without
the marker is NEVER touched.
"""
import asyncio, json, os, shutil, subprocess, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, '/app/backend')
BACKEND_CONF = Path('/etc/supervisor/conf.d/backend.conf')
BACKUP_DIR = Path('/app/backend/backups/v28_scope_s1')


async def _async_main():
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
    db = client[os.environ.get('DB_NAME') or 'divine_waifus']

    # 1) Delete marker docs
    inv_del = await db.user_gift_inventory.delete_many({'meta.v28_scope_s1': True})
    aff_del = await db.user_affinity_state.delete_many({'meta.v28_scope_s1': True})
    client.close()

    # 2) Restore backend.conf
    backups = sorted(BACKUP_DIR.glob('backend.conf.*.bak'),
                      key=lambda p: p.stat().st_mtime, reverse=True)
    if backups:
        shutil.copy2(backups[0], BACKEND_CONF)
        restored = str(backups[0])
    else:
        restored = None

    # 3) Restart backend
    subprocess.run(['supervisorctl', 'reread'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'update'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'restart', 'backend'], capture_output=True, text=True, timeout=30)
    time.sleep(5)
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=5) as r:
            cs = json.loads(r.read().decode())
    except Exception as e:
        cs = {'error': str(e)[:200]}

    print(json.dumps({
        'inv_docs_deleted': inv_del.deleted_count,
        'aff_docs_deleted': aff_del.deleted_count,
        'backend_conf_restored_from': restored,
        'post_canary_allowlist_size': cs.get('canary_allowlist_size'),
        'post_canary_cap': cs.get('canary_ledger_cap'),
    }, indent=2, default=str))
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(_async_main()))
