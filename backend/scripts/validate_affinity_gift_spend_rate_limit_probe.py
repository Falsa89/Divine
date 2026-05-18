#!/usr/bin/env python3
"""V21 — Validate rate-limit probe result."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/affinity_gift_spend_rate_limit_probe_result_v1.json')


def main():
    if not R.exists():
        print(f'FAIL: missing {R}'); return 2
    d = json.loads(R.read_text())
    fails = []
    if d.get('overall_status') != 'PASS':
        fails.append('overall_not_pass')
    if not d.get('saw_429_at_least_once'):
        fails.append('did_not_see_429')
    if not d.get('only_safe_status_codes'):
        fails.append('unsafe_codes_observed')
    if not d.get('no_200_for_unauth'):
        fails.append('unauth_got_200')
    if not d.get('no_500_anywhere'):
        fails.append('5xx_observed')
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-V21-RATE-LIMIT-PROBE')
    return 0


if __name__ == '__main__':
    sys.exit(main())
