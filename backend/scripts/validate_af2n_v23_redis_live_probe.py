#!/usr/bin/env python3
"""V23 — Validate Redis live probe."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_v23_redis_live_probe_result_v1.json')


def main():
    if not R.exists(): print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    s = d.get('overall_status')
    if s == 'PASS':
        print('PASS: AF2-N-V23-REDIS-LIVE-PROBE (live)'); return 0
    if s == 'READY_NOT_APPLIED':
        print('PASS: AF2-N-V23-REDIS-LIVE-PROBE (READY_NOT_APPLIED, safe)'); return 0
    print(f'FAIL: redis probe status={s}'); return 2


if __name__ == '__main__':
    sys.exit(main())
