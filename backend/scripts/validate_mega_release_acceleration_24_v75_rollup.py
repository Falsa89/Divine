#!/usr/bin/env python3
"""validate_mega_release_acceleration_24_v75_rollup"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'MEGA-RELEASE-ACCELERATION-24-v75-ROLLUP'
TAG = 'PUBLIC_SYNC_TAG_v75_MEGA_RELEASE_ACCELERATION_24_CLOSED_ALPHA_KICKOFF_EXECUTION_TRIAGE_P3_POLISH'

ROLLUP = 'data/design/release_acceleration/mega_release_acceleration_24_v75_rollup_marker_v1.json'

ALL_ARTIFACTS = [
    'data/design/qa/closed_alpha_kickoff_execution_state_v1.json',
    'data/design/qa/closed_alpha_kickoff_execution_state_marker_v1.json',
    'data/design/qa/closed_alpha_manual_recruitment_plan_v1.json',
    'data/design/qa/closed_alpha_manual_recruitment_marker_v1.json',
    'data/design/qa/closed_alpha_session_tracker_template_v1.json',
    'data/design/qa/closed_alpha_session_evidence_template_v1.json',
    'data/design/qa/closed_alpha_session_tracker_evidence_marker_v1.json',
    'data/design/qa/closed_alpha_findings_triage_workflow_v1.json',
    'data/design/qa/closed_alpha_findings_triage_workflow_marker_v1.json',
    'data/design/qa/closed_alpha_kickoff_dry_run_result_v1.json',
    'data/design/qa/closed_alpha_kickoff_dry_run_marker_v1.json',
    'data/design/qa/v72_p3_polish_batch_applied_v1.json',
    'data/design/qa/v72_p3_polish_batch_applied_marker_v1.json',
    'data/design/release_acceleration/alpha_readiness_progress_report_v19.json',
    'data/design/release_acceleration/alpha_readiness_progress_report_v19_marker_v1.json',
    ROLLUP,
    'docs/divine/453_CLOSED_ALPHA_KICKOFF_EXECUTION_STATE.md',
    'docs/divine/454_CLOSED_ALPHA_MANUAL_RECRUITMENT_PLAN.md',
    'docs/divine/455_CLOSED_ALPHA_SESSION_TRACKER_EVIDENCE.md',
    'docs/divine/456_CLOSED_ALPHA_FINDINGS_TRIAGE_WORKFLOW.md',
    'docs/divine/457_CLOSED_ALPHA_KICKOFF_DRY_RUN.md',
    'docs/divine/458_v72_P3_POLISH_BATCH_APPLIED.md',
    'docs/divine/459_ALPHA_READINESS_PROGRESS_v19.md',
    'docs/divine/460_MEGA_RELEASE_ACCELERATION_24_CLOSED_ALPHA_KICKOFF_TRIAGE_P3_POLISH_v75.md',
    'backend/scripts/validate_closed_alpha_kickoff_execution_state_v1.py',
    'backend/scripts/validate_closed_alpha_manual_recruitment_plan_v1.py',
    'backend/scripts/validate_closed_alpha_session_tracker_evidence_v1.py',
    'backend/scripts/validate_closed_alpha_findings_triage_workflow_v1.py',
    'backend/scripts/validate_closed_alpha_kickoff_dry_run_v1.py',
    'backend/scripts/validate_v72_p3_polish_batch_applied_v1.py',
    'backend/scripts/validate_alpha_readiness_progress_v19_v1.py',
]

FLAGS = {
    'closed_alpha_kickoff_execution_state': 'manual_recruitment_readiness_ready_v75',
    'automated_live_invites': False,
    'closed_alpha_invites_enabled': False,
    'p3_polish_applied': True,
    'p3_polish_applied_count': 3,
    'p3_polish_deferred_count': 0,
    'home_root_changed': False,
    'tab_bar_changed': False,
    'production_navigation_changed': False,
    'public_menu_routing_enabled': False,
    'home_menu_routing_enabled': False,
    'alpha_preview_menu_section_exposed': True,
    'approval_phrase_received': True,
    'approval_checksum_verified': True,
    'db_writes': 0,
    'reward_grant_enabled': False,
    'permanent_progress_enabled': False,
    'battle_engine_runtime_used': False,
    'backend_route_changed': False,
    'server_py_changed': False,
    'story_tsx_changed': False,
    'combat_tsx_changed': False,
    'story_tsx_imported': False,
    'combat_tsx_imported': False,
    'event_currency_enabled': False,
    'arena_ranking_enabled': False,
    'matchmaking_live': False,
    'account_flag_writes': False,
    'async_storage_persistence': False,
    'real_asset_import': False,
    'asset_runtime_resolver_changed': False,
    'character_bible_changed': False,
    'hero_roster_changed': False,
    'broad_commercial_release': False,
    'validator_weakening': False,
    'fake_pass': False,
}


def fail(msg):
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main():
    for rel in ALL_ARTIFACTS:
        if not (ROOT / rel).exists():
            fail(f'missing {rel}')
    r = json.loads((ROOT / ROLLUP).read_text())
    if r.get('public_sync_tag') != TAG:
        fail('rollup.public_sync_tag mismatch')
    for k, v in FLAGS.items():
        if r.get(k) != v:
            fail(f'rollup.{k}={r.get(k)!r} expected {v!r}')
    if r.get('new_screens'):
        fail('rollup.new_screens must be empty')
    if set(r.get('patched_screens', [])) != {'frontend/app/alpha-preview-hub.tsx', 'frontend/app/first-session-onboarding-preview.tsx'}:
        fail('rollup.patched_screens mismatch')
    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
