#!/usr/bin/env python3
"""V21 — Validate DB backup drill result."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_stage4_db_backup_drill_result_v1.json')
REQUIRED = ['gift_transaction_ledger', 'user_gift_inventory', 'user_affinity_state']


def main():
    if not R.exists():
        print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    fails = []
    if d.get('destructive') is not False:
        fails.append('destructive_true')
    if d.get('restore_executed') is not False:
        fails.append('restore_executed')
    if d.get('overall_status') != 'PASS':
        fails.append('overall_not_pass')
    if not d.get('all_collections_ok'):
        fails.append('not_all_collections_ok')
    coll = d.get('collections', {})
    for c in REQUIRED:
        if c not in coll:
            fails.append(f'collection_missing:{c}')
            continue
        entry = coll[c]
        if 'error' in entry:
            fails.append(f'collection_error:{c}:{entry["error"]}')
            continue
        if not entry.get('counts_match_live'):
            fails.append(f'counts_mismatch:{c}')
        if not entry.get('sha256'):
            fails.append(f'no_checksum:{c}')
        if not Path(entry.get('dump_file', '')).exists():
            fails.append(f'dump_file_missing:{c}')
    if not isinstance(d.get('restore_plan', {}).get('order'), list):
        fails.append('no_restore_plan')
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-V21-DB-BACKUP-DRILL')
    return 0


if __name__ == '__main__':
    sys.exit(main())
