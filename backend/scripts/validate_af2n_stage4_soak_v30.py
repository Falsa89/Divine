#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_stage4_soak_v30_result.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    s = d.get('safety', {})
    if not s.get('no_5xx'): print('FAIL: 5xx'); return 2
    if not s.get('borea_invariant_held'): print('FAIL: borea'); return 2
    if not s.get('no_unauthorized_spend'): print('FAIL: unauth'); return 2
    if d.get('fresh_spend_count', 99) > 20: print('FAIL: fresh_cap'); return 2
    print('PASS: AF2-N-V30-STAGE4-SOAK'); return 0
if __name__ == '__main__': sys.exit(main())
