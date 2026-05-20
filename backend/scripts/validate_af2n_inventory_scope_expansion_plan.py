#!/usr/bin/env python3
"""V26 PART D — Validator for inventory scope expansion plan."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_inventory_scope_expansion_plan_v1.json')


def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('status') != 'PLAN_ONLY': print('FAIL: must_be_plan_only'); return 2
    if d.get('live_expansion_in_v26') is True: print('FAIL: live_forbidden'); return 2
    if d.get('broad_rollout_authorized') is True: print('FAIL: broad_rollout_must_false'); return 2
    if len(d.get('stages', [])) < 4: print('FAIL: insufficient_stages'); return 2
    cn = d.get('constraints', {})
    if not cn.get('borea_hidden_invariant', {}).get('must_remain'): print('FAIL: borea_invariant'); return 2
    print('PASS: AF2-N-V26-INVENTORY-SCOPE-EXPANSION-PLAN'); return 0


if __name__ == '__main__':
    sys.exit(main())
