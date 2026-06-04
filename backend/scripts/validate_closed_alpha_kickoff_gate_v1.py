#!/usr/bin/env python3
"""validate_closed_alpha_kickoff_gate_v1

Verifica gate + runbook + packet + marker per il closed alpha kickoff.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-KICKOFF-GATE'
TAG = 'PUBLIC_SYNC_TAG_v74_MEGA_RELEASE_ACCELERATION_23_MENU_EXPOSURE_APPLY_CLOSED_ALPHA_KICKOFF'

FILES = [
    'data/design/qa/closed_alpha_kickoff_gate_v1.json',
    'data/design/qa/closed_alpha_kickoff_runbook_v1.json',
    'data/design/qa/closed_alpha_kickoff_packet_v1.json',
    'data/design/qa/closed_alpha_kickoff_gate_marker_v1.json',
]


def fail(msg: str) -> None:
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main() -> None:
    for rel in FILES:
        if not (ROOT / rel).exists():
            fail(f'missing {rel}')

    gate = json.loads((ROOT / FILES[0]).read_text())
    rb = json.loads((ROOT / FILES[1]).read_text())
    pkt = json.loads((ROOT / FILES[2]).read_text())
    mrk = json.loads((ROOT / FILES[3]).read_text())

    for obj, name in ((gate, 'gate'), (rb, 'runbook'), (pkt, 'packet'), (mrk, 'marker')):
        if obj.get('public_sync_tag') != TAG:
            fail(f'{name}.public_sync_tag mismatch')
        if obj.get('db_writes') != 0:
            fail(f'{name}.db_writes must be 0')

    if gate.get('kickoff_gate_enabled') is not True:
        fail('gate.kickoff_gate_enabled must be true')
    if gate.get('kickoff_authorized') is not True:
        fail('gate.kickoff_authorized must be true')
    if gate.get('closed_alpha_invites_enabled') is not False:
        fail('gate.closed_alpha_invites_enabled must be false')
    if gate.get('live_invite_system') is not False:
        fail('gate.live_invite_system must be false')
    if gate.get('manual_recruitment_required') is not True:
        fail('gate.manual_recruitment_required must be true')
    if gate.get('all_prerequisites_satisfied') is not True:
        fail('gate.all_prerequisites_satisfied must be true')
    prereqs = gate.get('prerequisites', [])
    if len(prereqs) < 8:
        fail('gate.prerequisites must have at least 8 entries')
    for p in prereqs:
        if p.get('satisfied') is not True:
            fail(f'prereq {p.get("id")} not satisfied')

    if rb.get('total_steps') != 7:
        fail('runbook.total_steps must be 7')
    if rb.get('max_session_duration_minutes', 0) <= 0:
        fail('runbook.max_session_duration_minutes must be > 0')
    if rb.get('halt_on_p0') is not True:
        fail('runbook.halt_on_p0 must be true')
    steps = rb.get('steps', [])
    if len(steps) != 7:
        fail('runbook.steps must have 7 entries')

    sections = pkt.get('sections', [])
    expected_section_ids = {'welcome', 'how_to_access', 'what_to_test', 'what_is_NOT_real', 'feedback', 'halt'}
    got_ids = {s.get('id') for s in sections}
    if not expected_section_ids.issubset(got_ids):
        fail(f'packet missing sections: {expected_section_ids - got_ids}')

    if mrk.get('kickoff_gate_enabled') is not True:
        fail('marker.kickoff_gate_enabled must be true')
    if mrk.get('closed_alpha_invites_enabled') is not False:
        fail('marker.closed_alpha_invites_enabled must be false')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
