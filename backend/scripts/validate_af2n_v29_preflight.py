#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_v29_preflight_result_v1.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    print('PASS: AF2-N-V29-PREFLIGHT'); return 0
if __name__ == '__main__': sys.exit(main())
