#!/usr/bin/env python3
"""validate_closed_alpha_manual_recruitment_plan_v1"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-MANUAL-RECRUITMENT-PLAN'
TAG = 'PUBLIC_SYNC_TAG_v75_MEGA_RELEASE_ACCELERATION_24_CLOSED_ALPHA_KICKOFF_EXECUTION_TRIAGE_P3_POLISH'

PLAN = 'data/design/qa/closed_alpha_manual_recruitment_plan_v1.json'
MRK = 'data/design/qa/closed_alpha_manual_recruitment_marker_v1.json'

FORBIDDEN_CHANNELS = {
    'automated_email', 'automated_DM', 'public_form_link',
    'social_media_broadcast', 'in_app_invite_system',
}


def fail(msg):
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main():
    for rel in (PLAN, MRK):
        if not (ROOT / rel).exists():
            fail(f'missing {rel}')
    p = json.loads((ROOT / PLAN).read_text())
    m = json.loads((ROOT / MRK).read_text())

    if p.get('public_sync_tag') != TAG:
        fail('plan.public_sync_tag mismatch')
    if p.get('recruitment_mode') != 'manual_only':
        fail('recruitment_mode must be manual_only')
    if p.get('automated_live_invites') is not False:
        fail('automated_live_invites must be false')
    if p.get('email_send_enabled') is not False:
        fail('email_send_enabled must be false')
    if p.get('dm_send_enabled') is not False:
        fail('dm_send_enabled must be false')
    if p.get('db_writes') != 0:
        fail('db_writes must be 0')
    fb = set(p.get('channels_forbidden', []))
    if not FORBIDDEN_CHANNELS.issubset(fb):
        fail(f'channels_forbidden missing: {FORBIDDEN_CHANNELS - fb}')
    if p.get('target_tester_count', 0) < 4:
        fail('target_tester_count must be >= 4')
    if p.get('minimum_tester_count', 0) < 4:
        fail('minimum_tester_count must be >= 4')
    slots = p.get('prepared_slots', [])
    if len(slots) != 8:
        fail('prepared_slots must have 8 entries')
    for s in slots:
        if s.get('status') != 'prepared':
            fail(f'slot {s.get("slot_id")} status must be prepared')

    if m.get('recruitment_mode') != 'manual_only':
        fail('marker.recruitment_mode mismatch')
    if m.get('automated_live_invites') is not False:
        fail('marker.automated_live_invites must be false')
    if m.get('slot_count') != 8:
        fail('marker.slot_count must be 8')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
