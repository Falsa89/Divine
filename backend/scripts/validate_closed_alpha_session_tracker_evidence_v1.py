#!/usr/bin/env python3
"""validate_closed_alpha_session_tracker_evidence_v1"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-SESSION-TRACKER-EVIDENCE'
TAG = 'PUBLIC_SYNC_TAG_v75_MEGA_RELEASE_ACCELERATION_24_CLOSED_ALPHA_KICKOFF_EXECUTION_TRIAGE_P3_POLISH'

TRACKER = 'data/design/qa/closed_alpha_session_tracker_template_v1.json'
EVIDENCE = 'data/design/qa/closed_alpha_session_evidence_template_v1.json'
MRK = 'data/design/qa/closed_alpha_session_tracker_evidence_marker_v1.json'

TRACKER_REQUIRED_COLS = {
    'slot_id', 'device', 'os_version', 'session_start_utc', 'session_end_utc',
    'flow_first_session_onboarding', 'flow_training_preview',
    'flow_story_alpha_slice', 'flow_boss_tower_alpha_loop',
    'flow_event_arena_alpha_preview', 'flow_alpha_preview_hub',
    'feedback_form_submitted', 'bug_reports_count',
}

EVIDENCE_REQUIRED = {'session_id', 'timestamp_utc', 'flow_id', 'step_index', 'event_type'}


def fail(msg):
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main():
    for rel in (TRACKER, EVIDENCE, MRK):
        if not (ROOT / rel).exists():
            fail(f'missing {rel}')
    t = json.loads((ROOT / TRACKER).read_text())
    e = json.loads((ROOT / EVIDENCE).read_text())
    m = json.loads((ROOT / MRK).read_text())

    if t.get('public_sync_tag') != TAG or e.get('public_sync_tag') != TAG:
        fail('public_sync_tag mismatch')
    cols = {c.get('id') for c in t.get('columns', [])}
    if not TRACKER_REQUIRED_COLS.issubset(cols):
        fail(f'tracker missing cols: {TRACKER_REQUIRED_COLS - cols}')
    if t.get('db_writes') != 0:
        fail('tracker.db_writes must be 0')
    if t.get('account_persistence') is not False:
        fail('tracker.account_persistence must be false')
    rows = t.get('prepared_rows', [])
    if len(rows) != 8:
        fail('tracker.prepared_rows must have 8 entries')

    fields = {f.get('id') for f in e.get('evidence_fields', [])}
    if not EVIDENCE_REQUIRED.issubset(fields):
        fail(f'evidence missing fields: {EVIDENCE_REQUIRED - fields}')
    if e.get('in_app_persistence') is not False:
        fail('evidence.in_app_persistence must be false')
    if e.get('db_writes') != 0:
        fail('evidence.db_writes must be 0')
    if e.get('async_storage_persistence') is not False:
        fail('evidence.async_storage_persistence must be false')

    if m.get('in_app_persistence') is not False:
        fail('marker.in_app_persistence must be false')
    if m.get('db_writes') != 0:
        fail('marker.db_writes must be 0')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
