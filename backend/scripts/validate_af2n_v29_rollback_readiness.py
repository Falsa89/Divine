#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_v29_rollback_readiness_result_v1.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('production_db_touched') is True: print('FAIL: db_touched'); return 2
    print('PASS: AF2-N-V29-ROLLBACK-READINESS'); return 0
if __name__ == '__main__': sys.exit(main())
