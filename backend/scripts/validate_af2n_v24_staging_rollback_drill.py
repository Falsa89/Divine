#!/usr/bin/env python3
"""V24 — Validate staging rollback drill."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_v24_staging_rollback_drill_result_v1.json')


def main():
    if not R.exists(): print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    if d.get('non_destructive') is not True: print('FAIL: destructive'); return 2
    if d.get('production_state_modified') is not False: print('FAIL: production_modified'); return 2
    if d.get('overall_status') != 'PASS':
        for f in d.get('fails', []): print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-V24-STAGING-ROLLBACK-DRILL'); return 0


if __name__ == '__main__':
    sys.exit(main())
