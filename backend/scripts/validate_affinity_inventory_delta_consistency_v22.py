#!/usr/bin/env python3
"""V22 — Validate delta consistency audit."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/affinity_inventory_delta_consistency_v22_report.json')


def main():
    if not R.exists():
        print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    if d.get('overall_status') != 'PASS':
        for f in d.get('fails', []): print(f'FAIL: {f}')
        return 2
    c = d.get('checks', {})
    if c.get('negative_inventory_count', 0) > 0: print('FAIL: neg_inv'); return 2
    if c.get('borea_in_ledger', 0) > 0 or c.get('borea_in_affinity_state', 0) > 0: print('FAIL: borea'); return 2
    if c.get('duplicate_tx_ids', 0) > 0: print('FAIL: dup_tx'); return 2
    if c.get('duplicate_idempotency_groups', 0) > 0: print('FAIL: dup_idem'); return 2
    if c.get('inconsistent_canary_markers', 0) > 0: print('FAIL: inconsistent_canary'); return 2
    if c.get('non_allowlist_success_count', 0) > 0: print('FAIL: non_allowlist_success'); return 2
    if c.get('delta_mismatch_users', 0) > 0: print('FAIL: delta_mismatch'); return 2
    print('PASS: AF2-N-V22-DELTA-AUDIT')
    return 0


if __name__ == '__main__':
    sys.exit(main())
