#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/affinity_inventory_delta_consistency_v29_report.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('negative_inventory_count'): print('FAIL: neg'); return 2
    if d.get('borea_in_ledger_count'): print('FAIL: borea'); return 2
    if d.get('non_allowlist_success_count'): print('FAIL: unauth'); return 2
    if d.get('idempotency_dup_mutation_count'): print('FAIL: dup'); return 2
    if d.get('v28_scope_marker_nested_count'): print('FAIL: nested_v28'); return 2
    print('PASS: AF2-N-V29-INVENTORY-DELTA-AUDIT'); return 0
if __name__ == '__main__': sys.exit(main())
