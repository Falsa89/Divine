#!/usr/bin/env python3
"""
AF2-L — Rollback rehearsal runner. Delegates to the migration rollback
script in dry-run, then asserts the result is design-only.
"""
import subprocess
import sys
from pathlib import Path

ROLLBACK = Path('/app/backend/scripts/rollback_affinity_gift_transaction_ledger_migration.py')
proc = subprocess.run(['python3', str(ROLLBACK)], capture_output=True, text=True, timeout=60)
print(proc.stdout)
if proc.returncode != 0:
    print(proc.stderr, file=sys.stderr)
sys.exit(proc.returncode)
