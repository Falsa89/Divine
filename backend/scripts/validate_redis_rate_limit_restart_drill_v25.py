#!/usr/bin/env python3
"""V25 PART C — Validate Redis restart drill output."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/redis_rate_limit_restart_drill_v25_result.json')


def main():
    if not P.exists():
        print('FAIL: drill_missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS':
        print('FAIL: drill_verdict_not_pass'); return 2
    print('PASS: AF2-N-V25-REDIS-RESTART-DRILL'); return 0


if __name__ == '__main__':
    sys.exit(main())
