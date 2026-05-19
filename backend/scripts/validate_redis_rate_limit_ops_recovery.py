#!/usr/bin/env python3
"""V25 PART B — Validator wrapper for Redis ops recovery audit."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/redis_rate_limit_ops_recovery_result_v1.json')


def main():
    if not P.exists():
        print('FAIL: audit_missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS':
        print('FAIL: audit_verdict_not_pass', d.get('fails', [])[:5]); return 2
    print('PASS: AF2-N-V25-REDIS-OPS-RECOVERY'); return 0


if __name__ == '__main__':
    sys.exit(main())
