#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_v28_preflight_result_v1.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    c = d.get('checks', {})
    if c.get('canary_ledger_cap') != 25000: print('FAIL: cap'); return 2
    if c.get('canary_allowlist_size') != 700: print('FAIL: allowlist_pre'); return 2
    if c.get('borea_leak_in_list'): print('FAIL: borea_leak'); return 2
    if not c.get('gift_spend_borea_404'): print('FAIL: borea_404'); return 2
    if c.get('battle_runtime_attached') is not False: print('FAIL: battle'); return 2
    if not all((c.get('guardrail_diffs_clean') or {}).values()): print('FAIL: guardrails'); return 2
    if not c.get('db_collections_healthy'): print('FAIL: db'); return 2
    print('PASS: AF2-N-V28-PREFLIGHT'); return 0
if __name__ == '__main__': sys.exit(main())
