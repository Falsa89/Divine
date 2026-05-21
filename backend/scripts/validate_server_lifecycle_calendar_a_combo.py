#!/usr/bin/env python3
"""SLC-A: Combo validator (runs the 4 sub-validators)."""
import subprocess, sys
from pathlib import Path
ROOT = Path('/app/backend/scripts')
SUBS = [
    ('SLC-A-SHARD-ISOLATION-AUDIT',  'audit_server_shard_isolation_v1.py'),
    ('SLC-A-POLICIES',               'validate_server_lifecycle_policies_v1.py'),
    ('SLC-A-CALENDAR-SCHEMA',        'validate_server_age_calendar_schema_v1.py'),
    ('SLC-A-MERGE-RECOVERY',         'validate_server_merge_recovery_policy_v1.py'),
    ('SLC-A-SHARD-ISOLATION-SAFETY', 'audit_server_shard_isolation_safety_v1.py'),
]


def main():
    passes=[]; fails=[]
    for label, script in SUBS:
        p=ROOT/script
        if not p.exists(): fails.append(f'missing:{label}'); continue
        r = subprocess.run(['python3', str(p)], capture_output=True, text=True, timeout=60)
        if r.returncode == 0: passes.append(label)
        else:
            tail = ((r.stdout or '')+(r.stderr or '')).strip().splitlines()
            fails.append(f'fail:{label}:{tail[-1] if tail else ""}')
    print(f"SERVER-LIFECYCLE-CALENDAR-A {'PASS' if not fails else 'FAIL'} passes={len(passes)} fails={len(fails)}")
    for x in passes: print(f'  ✓ {x}')
    for x in fails: print(f'  ✗ {x}')
    return 0 if not fails else 2


if __name__ == '__main__': sys.exit(main())
