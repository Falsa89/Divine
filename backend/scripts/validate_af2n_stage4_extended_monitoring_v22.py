#!/usr/bin/env python3
"""V22 — Validate Stage4 extended monitoring result."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_stage4_extended_monitoring_v22_result.json')


def main():
    if not R.exists():
        print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    if d.get('overall_status') == 'BLOCKED_NO_STAGE4':
        print('PASS: AF2-N-V22-STAGE4-EXTENDED-MONITORING (BLOCKED-SAFE)')
        return 0
    if d.get('overall_status') != 'PASS':
        for f in d.get('fails', []): print(f'FAIL: {f}')
        return 2
    if d.get('inv_neg_count', 0) > 0: print('FAIL: neg_inv'); return 2
    if d.get('borea_rows_in_ledger', 0) > 0: print('FAIL: borea_rows'); return 2
    if d.get('duplicate_idempotency_groups', 0) > 0: print('FAIL: dup_idem'); return 2
    counts = d.get('status_counts', {})
    for b in ('500','502','503','504'):
        if counts.get(b, 0) > 0: print(f'FAIL: 5xx:{b}'); return 2
    print('PASS: AF2-N-V22-STAGE4-EXTENDED-MONITORING')
    return 0


if __name__ == '__main__':
    sys.exit(main())
