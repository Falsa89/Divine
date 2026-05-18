#!/usr/bin/env python3
"""V21 — DB backup drill REAL (non-destructive).

For each critical collection: count documents, dump to JSON file, compute
sha256 checksum, write manifest. Restore is DRY-RUN only (re-read + verify).

No DELETE, no DROP, no UPDATE.
"""
from __future__ import annotations
import hashlib, json, os, sys
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient
from bson import json_util

COLLECTIONS = ['gift_transaction_ledger', 'user_gift_inventory', 'user_affinity_state']
BACKUP_ROOT = Path('/app/backups/af2n_stage4')
OUT = Path('/app/data/design/affinity/af2n_stage4_db_backup_drill_result_v1.json')
NOW = datetime.now(timezone.utc)
STAMP = NOW.strftime('%Y%m%dT%H%M%SZ')


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    backup_dir = BACKUP_ROOT / f'backup_{STAMP}'
    backup_dir.mkdir(parents=True, exist_ok=False)

    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'divine_waifus')
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    db = client[db_name]

    manifest = {
        'manifest_id': 'af2n_stage4_db_backup_drill_v1',
        'task_origin': 'V21-AF2N-DB-BACKUP-DRILL-REAL',
        'design_only': False,
        'destructive': False,
        'restore_executed': False,
        'restore_dry_run_only': True,
        'started_at_utc': NOW.isoformat().replace('+00:00', 'Z'),
        'backup_dir': str(backup_dir),
        'collections': {},
    }
    all_ok = True
    for name in COLLECTIONS:
        try:
            coll = db[name]
            n = coll.count_documents({})
            dump_path = backup_dir / f'{name}.json'
            with dump_path.open('w') as f:
                f.write('[')
                first = True
                for doc in coll.find({}):
                    if not first:
                        f.write(',\n')
                    else:
                        first = False
                    f.write(json_util.dumps(doc))
                f.write(']')
            checksum = _sha256(dump_path)
            size = dump_path.stat().st_size
            # restore DRY-RUN: re-read and count docs in file
            with dump_path.open('r') as f:
                read_docs = json_util.loads(f.read())
            read_count = len(read_docs) if isinstance(read_docs, list) else -1
            manifest['collections'][name] = {
                'live_count': n,
                'dump_file': str(dump_path),
                'dump_size_bytes': size,
                'sha256': checksum,
                'dry_run_read_count': read_count,
                'counts_match_live': (read_count == n),
            }
            if read_count != n:
                all_ok = False
        except Exception as e:
            manifest['collections'][name] = {'error': str(e)}
            all_ok = False

    manifest['finished_at_utc'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    manifest['all_collections_ok'] = all_ok
    manifest['overall_status'] = 'PASS' if all_ok else 'FAIL'
    manifest['restore_plan'] = {
        'order': [
            '1. Stop backend (supervisorctl stop backend)',
            '2. For each collection: db.<name>.drop()',
            '3. mongoimport --uri ... --collection <name> --file <dump>.json',
            '4. Verify counts match manifest live_count',
            '5. Restart backend (supervisorctl restart backend)',
            '6. Run V21 preflight to confirm canary status'
        ],
        'rollback_owner_ref': 'rollback_owner_v5'
    }
    manifest['safety_invariants'] = [
        'no destructive restore',
        'no delete / drop / update on live db',
        'backup files immutable (no rewrite)',
        'never modifies battle_engine.py / combat.tsx'
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, indent=2))
    print(f'V21-DB-BACKUP-DRILL {manifest["overall_status"]} -> {OUT}')
    return 0 if all_ok else 2


if __name__ == '__main__':
    sys.exit(main())
