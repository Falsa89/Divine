#!/usr/bin/env python3
"""V26 PART H — Validator for stress 2x V26."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_stress_2x_v26_result.json')


def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    s = d.get('safety', {})
    if not s.get('no_5xx'): print('FAIL: 5xx_present'); return 2
    if not s.get('borea_invariant_held'): print('FAIL: borea_invariant'); return 2
    if not s.get('no_unauthorized_spend'): print('FAIL: unauthorized'); return 2
    print('PASS: AF2-N-V26-STRESS-2X'); return 0


if __name__ == '__main__':
    sys.exit(main())
