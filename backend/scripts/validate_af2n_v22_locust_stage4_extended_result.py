#!/usr/bin/env python3
"""V22 — Validate Locust extended result."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_v22_locust_stage4_extended_result_v1.json')


def main():
    if not R.exists(): print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    if d.get('overall_status') == 'BLOCKED_NO_STAGE4':
        print('PASS: AF2-L-LOCUST-STAGE4-V22 (BLOCKED-SAFE)'); return 0
    if d.get('overall_status') != 'PASS': print('FAIL: not_pass'); return 2
    if d.get('cap_exceeded'): print('FAIL: cap_exceeded'); return 2
    if not d.get('safe_ledger_growth'): print('FAIL: unsafe_growth'); return 2
    if d.get('negative_inventory_count', 0) > 0: print('FAIL: neg_inv'); return 2
    print('PASS: AF2-L-LOCUST-STAGE4-V22')
    return 0


if __name__ == '__main__':
    sys.exit(main())
