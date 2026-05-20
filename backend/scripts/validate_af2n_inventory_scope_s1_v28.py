#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_inventory_scope_s1_v28_result.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('status') not in ('APPLIED', 'READY_NOT_APPLIED'):
        print('FAIL: status'); return 2
    if d.get('status') == 'APPLIED':
        if d.get('allowlist_post_observed') != d.get('allowlist_target'): print('FAIL: count'); return 2
        if d.get('borea_in_seeded_aff', 1) != 0: print('FAIL: borea_in_seeded'); return 2
        s = d.get('safety', {})
        if not s.get('cap_unchanged_25000'): print('FAIL: cap_changed'); return 2
        if s.get('broad_rollout_authorized') is True: print('FAIL: broad'); return 2
        if s.get('battle_engine_modified') is True: print('FAIL: battle'); return 2
    print(f"PASS: AF2-N-V28-INVENTORY-SCOPE-S1 ({d.get('status')})"); return 0
if __name__ == '__main__': sys.exit(main())
