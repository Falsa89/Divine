#!/usr/bin/env python3
"""COSMETIC-A: Combo validator (runs all 4 sub-validators)."""
import subprocess, sys
from pathlib import Path
ROOT = Path('/app/backend/scripts')
SUBS = [
    ('COSMETIC-A-POLICY',          'validate_cosmetic_system_policy_v1.py'),
    ('COSMETIC-A-SCHEMAS',         'validate_cosmetic_schemas_v1.py'),
    ('COSMETIC-A-EXAMPLES',        'validate_cosmetic_examples_v1.py'),
    ('COSMETIC-A-RUNTIME-SAFETY',  'audit_cosmetic_runtime_safety_v1.py'),
]


def main():
    passes=[]; fails=[]
    for label, script in SUBS:
        p = ROOT/script
        if not p.exists(): fails.append(f'missing:{label}'); continue
        r = subprocess.run(['python3', str(p)], capture_output=True, text=True, timeout=60)
        if r.returncode == 0: passes.append(label)
        else:
            tail = ((r.stdout or '')+(r.stderr or '')).strip().splitlines()
            fails.append(f'fail:{label}:{tail[-1] if tail else ""}')
    print(f"COSMETIC-SKIN-TITLE-SYSTEM-A {'PASS' if not fails else 'FAIL'} passes={len(passes)} fails={len(fails)}")
    for x in passes: print(f'  ✓ {x}')
    for x in fails: print(f'  ✗ {x}')
    return 0 if not fails else 2


if __name__ == '__main__': sys.exit(main())
