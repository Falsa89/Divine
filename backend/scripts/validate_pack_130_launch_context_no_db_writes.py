#!/usr/bin/env python3
"""Pack 130 — No DB writes nel route Pack 130 (STATIC)."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FILES = [REPO_ROOT / 'backend' / 'routes' / 'v130_lobby_launch_context.py',
         REPO_ROOT / 'backend' / 'helpers' / 'lobby_launch_context.py',
         REPO_ROOT / 'backend' / 'helpers' / 'real_player_snapshot.py']

FORBIDDEN = ['update_one(', 'update_many(', 'insert_one(', 'insert_many(',
             'delete_one(', 'delete_many(', 'replace_one(',
             'find_one_and_update(', 'find_one_and_delete(', 'find_one_and_replace(',
             'bulk_write(', 'create_index(']


def main() -> int:
    errors = []; notes = []
    for f in FILES:
        if not f.exists():
            errors.append(f'file missing: {f.relative_to(REPO_ROOT)}'); continue
        src = f.read_text(encoding='utf-8')
        for fp in FORBIDDEN:
            if fp in src:
                errors.append(f'{f.name} contains forbidden DB write op: `{fp}`')
    print(f'OK    {len(FILES)} Pack 130 files scanned, {len(FORBIDDEN)} forbidden write patterns checked')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_130_LAUNCH_CONTEXT_NO_DB_WRITES',
              'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'notes': notes,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_NO_DB_WRITE_OP_IN_PACK_130_ROUTE_OR_HELPERS'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_130_launch_context_no_db_writes_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  Pack 130 introduces NO DB write ops')
    return 0


if __name__ == '__main__': sys.exit(main())
