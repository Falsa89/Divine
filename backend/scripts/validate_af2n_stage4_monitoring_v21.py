#!/usr/bin/env python3
"""V21 — Validate Stage4 monitoring V21 result."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_stage4_monitoring_v21_result.json')


def main():
    if not R.exists():
        print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    status = d.get('overall_status')
    if status == 'BLOCKED_NO_STAGE4':
        print('PASS: AF2-N-V21-STAGE4-MONITORING (BLOCKED-SAFE: Stage4 not applied)')
        return 0
    if status != 'PASS':
        for f in d.get('fails', []):
            print(f'FAIL: {f}')
        return 2
    counts = d.get('status_counts', {})
    for bad in ('500', '502', '503', '504'):
        if counts.get(bad, 0) > 0:
            print(f'FAIL: 5xx_observed:{bad}'); return 2
    print('PASS: AF2-N-V21-STAGE4-MONITORING')
    return 0


if __name__ == '__main__':
    sys.exit(main())
