#!/usr/bin/env python3
"""V21 — ROLLBACK Stage4 Internal Beta.

Restores supervisor.conf from V21 pre-stage4 backup, removes stage4 seed docs
(metadata.seed_task == 'V21_STAGE4'), restarts backend.

DOES NOT touch battle files. DOES NOT drop databases. DOES NOT remove user data
belonging to non-stage4 users.
"""
from __future__ import annotations
import json, os, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient

SUPERVISOR_CONF = Path('/etc/supervisor/conf.d/backend.conf')
BACKUP_DIR = Path('/app/backups/af2n_stage4')
OUT = Path('/app/data/design/affinity/af2n_stage4_internal_beta_rollback_result_v1.json')
NOW = datetime.now(timezone.utc)


def main():
    dry_run = os.environ.get('STAGE4_ROLLBACK_DRY_RUN', '') != 'false'
    # find latest pre-stage4 backup
    backups = sorted(BACKUP_DIR.glob('backend.conf.v21_pre_stage4_apply_*.bak'))
    if not backups:
        msg = 'no V21 pre-stage4 backup found'
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps({
            'overall_status': 'FAIL', 'reason': msg, 'dry_run': dry_run,
            'finished_at_utc': NOW.isoformat().replace('+00:00', 'Z')
        }, indent=2))
        print(f'STAGE4-ROLLBACK FAIL: {msg}')
        return 2
    latest = backups[-1]
    actions = {'dry_run': dry_run, 'backup_used': str(latest), 'steps': []}
    if not dry_run:
        SUPERVISOR_CONF.write_text(latest.read_text())
        actions['steps'].append('supervisor_conf_restored')
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'divine_waifus')
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        # remove stage4 seed docs only (V21_STAGE4 marker)
        rd = db['user_gift_inventory'].delete_many({'metadata.seed_task': 'V21_STAGE4'})
        actions['stage4_seed_docs_deleted'] = rd.deleted_count
        actions['steps'].append('stage4_seed_docs_removed')
        subprocess.run(['sudo', 'supervisorctl', 'update'], capture_output=True, text=True, timeout=30)
        r = subprocess.run(['sudo', 'supervisorctl', 'restart', 'backend'], capture_output=True, text=True, timeout=30)
        actions['supervisor_restart_stdout_tail'] = (r.stdout or '')[-200:]
        actions['steps'].append('backend_restarted')
        import time; time.sleep(4)
        from urllib.request import urlopen
        try:
            with urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=6) as rr:
                actions['post_rollback_canary_status'] = json.loads(rr.read().decode())
        except Exception as e:
            actions['post_rollback_canary_status'] = {'error': str(e)}
    else:
        actions['steps'] = ['DRY_RUN_only: would_restore_conf', 'DRY_RUN_only: would_delete_stage4_seed_docs', 'DRY_RUN_only: would_restart_backend']
    actions['overall_status'] = 'PASS'
    actions['finished_at_utc'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(actions, indent=2, default=str))
    print(f'STAGE4-ROLLBACK {"DRY-RUN" if dry_run else "APPLIED"} {actions["overall_status"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
