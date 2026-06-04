#!/usr/bin/env python3
"""validate_closed_alpha_kickoff_dry_run_v1"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-KICKOFF-DRY-RUN'
TAG = 'PUBLIC_SYNC_TAG_v75_MEGA_RELEASE_ACCELERATION_24_CLOSED_ALPHA_KICKOFF_EXECUTION_TRIAGE_P3_POLISH'

DR = 'data/design/qa/closed_alpha_kickoff_dry_run_result_v1.json'
MRK = 'data/design/qa/closed_alpha_kickoff_dry_run_marker_v1.json'


def fail(msg):
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main():
    for rel in (DR, MRK):
        if not (ROOT / rel).exists():
            fail(f'missing {rel}')
    d = json.loads((ROOT / DR).read_text())
    m = json.loads((ROOT / MRK).read_text())

    if d.get('public_sync_tag') != TAG:
        fail('dry_run.public_sync_tag mismatch')
    if d.get('dry_run') is not True:
        fail('dry_run must be true')
    if d.get('applied') is not False:
        fail('applied must be false')
    if d.get('verdict') != 'DRY_RUN_PASS_READY_FOR_MANUAL_KICKOFF':
        fail('verdict must be DRY_RUN_PASS_READY_FOR_MANUAL_KICKOFF')
    if d.get('db_writes') != 0:
        fail('db_writes must be 0')
    if d.get('production_navigation_changed') is not False:
        fail('production_navigation_changed must be false')
    s = d.get('summary', {})
    if s.get('fail', 99) != 0:
        fail('summary.fail must be 0')
    if s.get('pass', 0) < 17:
        fail('summary.pass must be >= 17')
    for c in d.get('checks', []):
        if c.get('status') != 'pass':
            fail(f'check {c.get("id")} not pass')

    if m.get('verdict') != 'DRY_RUN_PASS_READY_FOR_MANUAL_KICKOFF':
        fail('marker.verdict mismatch')
    if m.get('checks_fail', 99) != 0:
        fail('marker.checks_fail must be 0')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
