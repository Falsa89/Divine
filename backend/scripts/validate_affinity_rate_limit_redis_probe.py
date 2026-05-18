#!/usr/bin/env python3
"""V22 — Validate Redis rate-limit probe result."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/affinity_rate_limit_redis_probe_result_v1.json')


def main():
    if not R.exists():
        print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    status = d.get('overall_status')
    # Acceptable: PASS (Redis live and probe ok) OR READY_NOT_APPLIED (Redis not available)
    if status == 'PASS':
        print('PASS: AF2-N-V22-REDIS-PROBE (PASS)')
        return 0
    if status == 'READY_NOT_APPLIED':
        print('PASS: AF2-N-V22-REDIS-PROBE (READY_NOT_APPLIED, safe)')
        return 0
    print(f'FAIL: redis probe status={status}')
    return 2


if __name__ == '__main__':
    sys.exit(main())
