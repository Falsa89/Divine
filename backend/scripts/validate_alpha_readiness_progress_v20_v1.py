#!/usr/bin/env python3
"""validate_alpha_readiness_progress_v20_v1"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-ALPHA-READINESS-PROGRESS-v20'
TAG = 'PUBLIC_SYNC_TAG_v76_MEGA_RELEASE_ACCELERATION_25_MANUAL_KICKOFF_FEEDBACK_STORE_BETA_READINESS'
P = 'data/design/release_acceleration/alpha_readiness_progress_report_v20.json'
M = 'data/design/release_acceleration/alpha_readiness_progress_report_v20_marker_v1.json'
EXPECTED = {
    'closed_alpha_kickoff_execution': 'manual_kickoff_packet_ready_v76',
    'closed_alpha_manual_kickoff_packet_final': 'ready_v76',
    'closed_alpha_recruitment_checklist': 'ready_v76',
    'closed_alpha_session_result_placeholder': 'ready_v76',
    'closed_alpha_feedback_intake_template': 'ready_v76',
    'closed_alpha_post_session_triage_dry_run': 'DRY_RUN_EMPTY_PIPELINE_READY_FOR_REAL_FEEDBACK',
    'store_beta_readiness_notes': 'notes_only_v76',
    'v77_readiness_plan': 'ready_v76',
    'closed_alpha_invites_enabled': False,
    'automated_live_invites': False,
    'store_upload_performed': False,
    'build_generation_performed': False,
    'pii_collected_in_repo': False,
    'production_navigation_changed': False,
    'home_root_changed': False,
    'tab_bar_changed': False,
    'db_writes': 0,
    'broad_commercial_release': False,
}

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    p = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if p.get('public_sync_tag') != TAG: fail('tag mismatch')
    for k, v in EXPECTED.items():
        if p.get(k) != v: fail(f'{k}={p.get(k)!r} expected {v!r}')
    if m.get('closed_alpha_kickoff_execution') != 'manual_kickoff_packet_ready_v76': fail('marker.kickoff_execution mismatch')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
