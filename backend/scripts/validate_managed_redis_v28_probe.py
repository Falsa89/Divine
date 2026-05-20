#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/managed_redis_v28_probe_result.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('status') not in ('READY_NOT_APPLIED', 'CONNECTED'): print('FAIL: status'); return 2
    print(f"PASS: AF2-N-V28-MANAGED-REDIS-PROBE ({d.get('status')})"); return 0
if __name__ == '__main__': sys.exit(main())
