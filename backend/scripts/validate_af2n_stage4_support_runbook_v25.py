#!/usr/bin/env python3
"""V25 PART E — Validate support runbook V25."""
import sys
from pathlib import Path
P = Path('/app/docs/divine/85_AF2N_STAGE4_SUPPORT_RUNBOOK_V25.md')
REQUIRED = [
    'Incident severity',
    'Borea leak emergency',
    'Unauthorized spend',
    'Negative inventory',
    'Redis outage',
    'Delta mismatch',
    'Rollback commands',
    'Escalation owners',
    'Drill cadence',
    'ensure_redis_rate_limit.sh',
    'AFFINITY_GIFT_RUNTIME_ENABLED',
]


def main():
    if not P.exists(): print('FAIL: runbook_missing'); return 2
    t = P.read_text()
    missing = [k for k in REQUIRED if k not in t]
    if missing:
        for m in missing: print('FAIL: missing_section:', m)
        return 2
    if len(t) < 2000:
        print('FAIL: runbook_too_short'); return 2
    print(f'PASS: AF2-N-V25-SUPPORT-RUNBOOK ({len(t)} chars)'); return 0


if __name__ == '__main__':
    sys.exit(main())
