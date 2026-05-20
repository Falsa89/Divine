#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/affinity_inventory_delta_consistency_v27_report.json')
def main():
    if not P.exists(): print('FAIL: missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: verdict'); return 2
    if d.get('negative_inventory_count', 1) != 0: print('FAIL: negative_inventory'); return 2
    if d.get('borea_in_ledger_count', 1) != 0: print('FAIL: borea_in_ledger'); return 2
    if d.get('non_allowlist_success_count', 1) != 0: print('FAIL: unauthorized_success'); return 2
    if d.get('production_db_touched') is True: print('FAIL: db_touched'); return 2
    print('PASS: AF2-N-V27-INVENTORY-DELTA-AUDIT'); return 0
if __name__ == '__main__': sys.exit(main())
