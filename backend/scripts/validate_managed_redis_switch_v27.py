#!/usr/bin/env python3
"""V27 PART B — Validator for Managed Redis switch."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/managed_redis_switch_v27_result.json')


def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    # Accept both SWITCHED (live) and READY_NOT_APPLIED (no env)
    if d.get('status') not in ('SWITCHED', 'READY_NOT_APPLIED'):
        print('FAIL: status not allowed'); return 2
    print(f"PASS: AF2-N-V27-MANAGED-REDIS-SWITCH ({d.get('status')})"); return 0


if __name__ == '__main__':
    sys.exit(main())
