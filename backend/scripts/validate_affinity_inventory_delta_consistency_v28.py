#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/affinity_inventory_delta_consistency_v28_report.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('negative_inventory_count', 1) != 0: print('FAIL: neg_inv'); return 2
    if d.get('borea_in_ledger_count', 1) != 0: print('FAIL: borea'); return 2
    if d.get('borea_in_marker_aff_count', 1) != 0: print('FAIL: borea_marker'); return 2
    if d.get('non_allowlist_success_count', 1) != 0: print('FAIL: unauth'); return 2
    if d.get('idempotency_dup_mutation_count', 1) != 0: print('FAIL: dup'); return 2
    print('PASS: AF2-N-V28-INVENTORY-DELTA-AUDIT'); return 0
if __name__ == '__main__': sys.exit(main())
