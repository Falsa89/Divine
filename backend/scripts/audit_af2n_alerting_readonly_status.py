#!/usr/bin/env python3
"""V25 PART D — Validator for alerting read-only status."""
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_alerting_readonly_status_result_v1.json')


def main():
    if not P.exists(): print('FAIL: status_missing'); return 2
    d = json.loads(P.read_text())
    if d.get('verdict') != 'PASS': print('FAIL: status_verdict'); return 2
    if d.get('mutation_attempted') is True: print('FAIL: mutation_attempted'); return 2
    if not d.get('safety', {}).get('read_only'): print('FAIL: not_read_only'); return 2
    print('PASS: AF2-N-V25-ALERTING-READONLY-STATUS'); return 0


if __name__ == '__main__':
    sys.exit(main())
