#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_v28_schema_fix_regression_v29_result.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if not d.get('idempotent_rerun_no_op', {}).get('no_op'): print('FAIL: rerun_not_noop'); return 2
    if d.get('pre', {}).get('nested') != 0: print('FAIL: nested_present'); return 2
    print('PASS: AF2-N-V29-V28-SCHEMA-FIX-REGRESSION'); return 0
if __name__ == '__main__': sys.exit(main())
