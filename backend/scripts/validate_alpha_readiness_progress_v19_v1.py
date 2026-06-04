#!/usr/bin/env python3
"""validate_alpha_readiness_progress_v19_v1"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-ALPHA-READINESS-PROGRESS-v19'
TAG = 'PUBLIC_SYNC_TAG_v75_MEGA_RELEASE_ACCELERATION_24_CLOSED_ALPHA_KICKOFF_EXECUTION_TRIAGE_P3_POLISH'

REP = 'data/design/release_acceleration/alpha_readiness_progress_report_v19.json'
MRK = 'data/design/release_acceleration/alpha_readiness_progress_report_v19_marker_v1.json'

EXPECTED = {
    'closed_alpha_kickoff_execution': 'manual_recruitment_readiness_ready_v75',
    'closed_alpha_manual_recruitment_plan': 'ready_v75',
    'closed_alpha_session_tracker_template': 'ready_v75',
    'closed_alpha_session_evidence_template': 'ready_v75',
    'closed_alpha_findings_triage_workflow': 'ready_v75',
    'closed_alpha_kickoff_dry_run': 'DRY_RUN_PASS_READY_FOR_MANUAL_KICKOFF',
    'closed_alpha_invites_enabled': False,
    'automated_live_invites': False,
    'closed_alpha_manual_recruitment_only': True,
    'alpha_preview_menu_section_exposed': True,
    'alpha_p3_backlog': 'applied_v75',
    'alpha_p3_backlog_count': 0,
    'v72_p3_polish_batch': 'applied_v75',
    'home_root_changed': False,
    'tab_bar_changed': False,
    'production_navigation_changed': False,
    'db_writes': 0,
    'broad_commercial_release': False,
    'manual_approval_received': True,
    'approval_checksum_verified': True,
}


def fail(msg):
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main():
    for rel in (REP, MRK):
        if not (ROOT / rel).exists():
            fail(f'missing {rel}')
    r = json.loads((ROOT / REP).read_text())
    m = json.loads((ROOT / MRK).read_text())

    if r.get('public_sync_tag') != TAG:
        fail('report.public_sync_tag mismatch')
    for k, v in EXPECTED.items():
        if r.get(k) != v:
            fail(f'report.{k}={r.get(k)!r} expected {v!r}')

    if m.get('public_sync_tag') != TAG:
        fail('marker.public_sync_tag mismatch')
    if m.get('closed_alpha_kickoff_execution') != 'manual_recruitment_readiness_ready_v75':
        fail('marker mismatch')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
