#!/usr/bin/env python3
"""validate_closed_alpha_kickoff_execution_state_v1

Verifica execution state + marker.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-KICKOFF-EXECUTION-STATE'
TAG = 'PUBLIC_SYNC_TAG_v75_MEGA_RELEASE_ACCELERATION_24_CLOSED_ALPHA_KICKOFF_EXECUTION_TRIAGE_P3_POLISH'

STATE = 'data/design/qa/closed_alpha_kickoff_execution_state_v1.json'
MRK = 'data/design/qa/closed_alpha_kickoff_execution_state_marker_v1.json'


def fail(msg):
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main():
    for rel in (STATE, MRK):
        if not (ROOT / rel).exists():
            fail(f'missing {rel}')
    s = json.loads((ROOT / STATE).read_text())
    m = json.loads((ROOT / MRK).read_text())

    if s.get('public_sync_tag') != TAG:
        fail('state.public_sync_tag mismatch')
    if s.get('kickoff_execution_mode') != 'manual_recruitment_readiness_only':
        fail('kickoff_execution_mode mismatch')
    if s.get('kickoff_execution_started') is not False:
        fail('kickoff_execution_started must be false')
    if s.get('automated_live_invites') is not False:
        fail('automated_live_invites must be false')
    if s.get('email_send_enabled') is not False:
        fail('email_send_enabled must be false')
    if s.get('networking_enabled') is not False:
        fail('networking_enabled must be false')
    if s.get('db_writes') != 0:
        fail('db_writes must be 0')
    if s.get('account_persistence') is not False:
        fail('account_persistence must be false')
    phases = s.get('phases_state', [])
    if len(phases) != 5:
        fail('phases_state must have 5 entries')
    for d in s.get('dependencies', []):
        if d.get('satisfied') is not True:
            fail(f'dependency {d.get("id")} not satisfied')

    if m.get('public_sync_tag') != TAG:
        fail('marker.public_sync_tag mismatch')
    if m.get('automated_live_invites') is not False:
        fail('marker.automated_live_invites must be false')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
