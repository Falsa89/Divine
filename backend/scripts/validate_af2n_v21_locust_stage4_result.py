#!/usr/bin/env python3
"""V21 — Validate Locust Stage4 low-impact result."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_v21_locust_stage4_result_v1.json')


def main():
    if not R.exists():
        print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    if d.get('overall_status') != 'PASS':
        print('FAIL: overall_not_pass')
        return 2
    if d.get('cap_exceeded') is True:
        print('FAIL: cap_exceeded'); return 2
    if not d.get('safe_ledger_growth'):
        print('FAIL: unsafe_ledger_growth'); return 2
    print('PASS: AF2-L-LOCUST-STAGE4-V21')
    return 0


if __name__ == '__main__':
    sys.exit(main())
