#!/usr/bin/env python3
"""Rollback Stage3 QA expansion.

Usage:
  python3 rollback_af2n_stage3_qa_expansion.py            # dry-run
  python3 rollback_af2n_stage3_qa_expansion.py --execute  # actually rollback
"""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

SUP_CONF = Path('/etc/supervisor/conf.d/backend.conf')
BACKUP_DIR = Path('/app/ops/backups')
API = 'http://127.0.0.1:8001/api'
OUT = Path('/app/data/design/affinity/af2n_stage3_qa_expansion_rollback_result_v1.json')


def _get(p):
    try:
        with urlopen(API + p, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--execute', action='store_true'); args = ap.parse_args()
    payload = {'result_id': 'af2n_stage3_qa_expansion_rollback_result_v1',
               'task_origin': 'AF2-N-STAGE3-ROLLBACK',
               'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
               'mode': 'execute' if args.execute else 'dry_run'}
    backups = sorted(BACKUP_DIR.glob('backend.conf.v18_pre_stage3.*.bak'))
    payload['backups_available'] = [b.name for b in backups]
    if not backups:
        payload['overall_status'] = 'NOT_APPLICABLE_NO_BACKUP_FOUND'
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
        print('No Stage3 backup found.'); return 0
    payload['selected_backup'] = backups[-1].name
    payload['dry_run_steps'] = [
        'restore_supervisor_conf_from_backup',
        'supervisorctl_update_and_restart_backend',
        'wait_api_health_200',
        'delete_user_gift_inventory_where_metadata_seed_task_eq_V18_STAGE3',
        'verify_canary_status_back_to_stage2',
    ]
    if not args.execute:
        payload['overall_status'] = 'DRY_RUN_OK'
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print('Stage3 rollback dry-run OK.'); return 0
    shutil.copy2(backups[-1], SUP_CONF)
    payload['supervisor_conf_restored'] = True
    subprocess.run(['supervisorctl','update'], capture_output=True, text=True, timeout=20)
    subprocess.run(['supervisorctl','restart','backend'], capture_output=True, text=True, timeout=30)
    ok = False
    for _ in range(20):
        time.sleep(1.5)
        c, _ = _get('/health')
        if c == 200: ok = True; break
    payload['backend_recovered'] = ok
    try:
        from pymongo import MongoClient
        db = MongoClient('mongodb://localhost:27017')['divine_waifus']
        res = db['user_gift_inventory'].delete_many({'metadata.seed_task': 'V18_STAGE3'})
        payload['stage3_seed_docs_deleted'] = res.deleted_count
    except Exception as e:
        payload['stage3_seed_docs_deleted'] = -1; payload['seed_delete_error'] = repr(e)
    _, st = _get('/affinity/gift-spend/canary-status')
    payload['post_rollback_canary_status'] = st
    payload['overall_status'] = 'EXECUTED_OK' if ok else 'EXECUTED_PARTIAL'
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'Stage3 rollback: {payload["overall_status"]}'); return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
