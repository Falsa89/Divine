#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_cap_raise_s2_v30_result.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('status') not in ('APPLIED', 'READY_NOT_APPLIED', 'NO_OP_ALREADY_AT_50000'):
        print('FAIL: status'); return 2
    s = d.get('safety', {})
    if s and s.get('allowlist_unchanged_2500') is False: print('FAIL: allowlist'); return 2
    if s and s.get('no_borea_exposure') is False: print('FAIL: borea'); return 2
    if s and s.get('heroes_count_100') is False: print('FAIL: heroes'); return 2
    if s and s.get('broad_rollout_authorized') is True: print('FAIL: broad'); return 2
    print(f"PASS: AF2-N-V30-CAP-RAISE-S2 ({d.get('status')})"); return 0
if __name__ == '__main__': sys.exit(main())
