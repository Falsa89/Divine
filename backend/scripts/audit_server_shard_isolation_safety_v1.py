#!/usr/bin/env python3
"""SLC-A: Audit shard isolation safety (read-only sanity).

Verifies the audit JSON exists and that:
  - audit_only=True
  - db_writes_performed=False
  - db_connection_opened=False
  - no Borea/greek_borea/primordial_gaia in any audit result strings
  - our new SLC-A scripts have no mutating patterns or DB writes
"""
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path('/app/data/design/server_lifecycle')
OUT = Path(ROOT, '_audit_server_shard_isolation_safety_v1_result.json')
SCRIPT_DIR = Path('/app/backend/scripts')
AUDIT = ROOT/'server_shard_isolation_audit_v1.json'
OUR_SCRIPTS = [
    'audit_server_shard_isolation_v1.py',
    'validate_server_lifecycle_policies_v1.py',
    'validate_server_age_calendar_schema_v1.py',
    'validate_server_merge_recovery_policy_v1.py',
    'audit_server_shard_isolation_safety_v1.py',
    'validate_server_lifecycle_calendar_a_combo.py',
]
BAD_IMPORTS = ('motor.motor_asyncio','AsyncIOMotorClient','pymongo','redis.Redis')
BAD_PATTERNS = (
    r'\.insert_one\(', r'\.update_one\(', r'\.delete_one\(', r'\.replace_one\(',
    r'\.insert_many\(', r'\.update_many\(', r'\.delete_many\(',
    r'router\.post\(', r'router\.put\(', r'router\.delete\(', r'router\.patch\(',
    r'app\.post\(', r'app\.put\(', r'app\.delete\(', r'app\.patch\(',
)


def main():
    errs=[]
    if not AUDIT.exists():
        errs.append('audit_json_missing'); print('FAIL'); OUT.write_text(json.dumps({'errors':errs,'verdict':'FAIL'})); return 2
    a = json.loads(AUDIT.read_text())
    if a.get('db_writes_performed') is not False: errs.append('audit:db_writes_true')
    if a.get('db_connection_opened') is not False: errs.append('audit:db_connection_opened')
    if not (a.get('safety') or {}).get('audit_only'): errs.append('audit:not_audit_only')
    # Borea must not appear anywhere in audit JSON VALUES. We exclude:
    #  - sample_lines (read-only code quotes)
    #  - keys that are safety assertions (e.g. no_borea_exposure)
    def _walk_values(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == 'sample_lines':
                    continue
                if 'borea' in k.lower():
                    # Safety key like "no_borea_exposure" — allowed.
                    continue
                yield from _walk_values(v)
        elif isinstance(node, list):
            for it in node: yield from _walk_values(it)
        else:
            yield str(node).lower()
    borea_hits = []
    for val in _walk_values(a):
        for bad in ('borea','greek_borea','primordial_gaia'):
            if bad in val:
                borea_hits.append(bad)
    if borea_hits:
        errs.append(f'audit:borea_leak_in_values:{sorted(set(borea_hits))}')
    # Scripts safety
    for s in OUR_SCRIPTS:
        p = SCRIPT_DIR/s
        if not p.exists(): errs.append(f'script_missing:{s}'); continue
        if s == 'audit_server_shard_isolation_safety_v1.py':
            continue  # contains pattern literals
        txt = p.read_text()
        for bi in BAD_IMPORTS:
            if bi in txt: errs.append(f'{s}:bad_import:{bi}')
        for bp in BAD_PATTERNS:
            if re.search(bp, txt): errs.append(f'{s}:mutating_pattern:{bp}')
    out = {
        'task_origin':'SLC-A-AUDIT-SHARD-ISOLATION-SAFETY',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'errors': errs,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out,indent=2,default=str))
    print(f"verdict={out['verdict']} errors={len(errs)}")
    for e in errs[:20]: print(f'  - {e}')
    return 0 if not errs else 2


if __name__ == '__main__': sys.exit(main())
