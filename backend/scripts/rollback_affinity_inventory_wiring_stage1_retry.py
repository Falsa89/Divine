#!/usr/bin/env python3
"""V16 inventory retry rollback — alias of V15 rollback (same script)."""
from __future__ import annotations
import sys, subprocess

if __name__ == '__main__':
    sys.exit(subprocess.call(['python3','/app/backend/scripts/rollback_affinity_inventory_wiring_stage1.py'] + sys.argv[1:]))
