#!/usr/bin/env python3
"""validate_closed_alpha_findings_triage_workflow_v1"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-CLOSED-ALPHA-FINDINGS-TRIAGE-WORKFLOW'
TAG = 'PUBLIC_SYNC_TAG_v75_MEGA_RELEASE_ACCELERATION_24_CLOSED_ALPHA_KICKOFF_EXECUTION_TRIAGE_P3_POLISH'

WF = 'data/design/qa/closed_alpha_findings_triage_workflow_v1.json'
MRK = 'data/design/qa/closed_alpha_findings_triage_workflow_marker_v1.json'

REQUIRED_BUCKETS = {'P0', 'P1', 'P2', 'P3'}
FORBIDDEN_ITEMS = {
    'public_live_ticketing_system',
    'persistent_bug_db_writes_app_side',
    'automatic_backend_route_creation',
    'automated_invite_or_notification',
}


def fail(msg):
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main():
    for rel in (WF, MRK):
        if not (ROOT / rel).exists():
            fail(f'missing {rel}')
    w = json.loads((ROOT / WF).read_text())
    m = json.loads((ROOT / MRK).read_text())

    if w.get('public_sync_tag') != TAG:
        fail('workflow.public_sync_tag mismatch')
    if set(w.get('buckets', [])) != REQUIRED_BUCKETS:
        fail('buckets mismatch')
    defs = w.get('bucket_definitions', {})
    for b in REQUIRED_BUCKETS:
        if b not in defs:
            fail(f'bucket_definitions missing {b}')
    sla = w.get('sla_minutes', {})
    if sla.get('P0') != 60:
        fail('sla P0 must be 60')
    if sla.get('P3') is not None:
        fail('sla P3 must be null')
    fb = set(w.get('forbidden', []))
    if not FORBIDDEN_ITEMS.issubset(fb):
        fail(f'workflow.forbidden missing: {FORBIDDEN_ITEMS - fb}')
    if w.get('db_writes') != 0:
        fail('workflow.db_writes must be 0')

    if set(m.get('buckets', [])) != REQUIRED_BUCKETS:
        fail('marker.buckets mismatch')
    if m.get('db_writes') != 0:
        fail('marker.db_writes must be 0')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
