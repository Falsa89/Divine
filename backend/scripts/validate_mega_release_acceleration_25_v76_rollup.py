#!/usr/bin/env python3
"""validate_mega_release_acceleration_25_v76_rollup"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'MEGA-RELEASE-ACCELERATION-25-v76-ROLLUP'
TAG = 'PUBLIC_SYNC_TAG_v76_MEGA_RELEASE_ACCELERATION_25_MANUAL_KICKOFF_FEEDBACK_STORE_BETA_READINESS'
ROLLUP = 'data/design/release_acceleration/mega_release_acceleration_25_v76_rollup_marker_v1.json'
ARTIFACTS = [
    'data/design/qa/closed_alpha_manual_kickoff_packet_final_v1.json',
    'data/design/qa/closed_alpha_manual_kickoff_packet_final_marker_v1.json',
    'data/design/qa/closed_alpha_recruitment_user_action_checklist_v1.json',
    'data/design/qa/closed_alpha_recruitment_user_action_checklist_marker_v1.json',
    'data/design/qa/closed_alpha_session_result_placeholder_v1.json',
    'data/design/qa/closed_alpha_session_result_placeholder_marker_v1.json',
    'data/design/qa/closed_alpha_feedback_intake_template_v1.json',
    'data/design/qa/closed_alpha_feedback_intake_template_marker_v1.json',
    'data/design/qa/closed_alpha_post_session_triage_dry_run_v1.json',
    'data/design/qa/closed_alpha_post_session_triage_dry_run_marker_v1.json',
    'data/design/release_acceleration/store_beta_readiness_notes_v1.json',
    'data/design/release_acceleration/store_beta_readiness_notes_marker_v1.json',
    'data/design/release_acceleration/v77_readiness_post_session_triage_plan_v1.json',
    'data/design/release_acceleration/v77_readiness_post_session_triage_plan_marker_v1.json',
    'data/design/release_acceleration/alpha_readiness_progress_report_v20.json',
    'data/design/release_acceleration/alpha_readiness_progress_report_v20_marker_v1.json',
    ROLLUP,
    'docs/divine/461_CLOSED_ALPHA_MANUAL_KICKOFF_PACKET_FINAL.md',
    'docs/divine/462_CLOSED_ALPHA_RECRUITMENT_USER_ACTION_CHECKLIST.md',
    'docs/divine/463_CLOSED_ALPHA_SESSION_RESULT_PLACEHOLDER.md',
    'docs/divine/464_CLOSED_ALPHA_FEEDBACK_INTAKE_TEMPLATE.md',
    'docs/divine/465_CLOSED_ALPHA_POST_SESSION_TRIAGE_DRY_RUN.md',
    'docs/divine/466_STORE_BETA_READINESS_NOTES.md',
    'docs/divine/467_v77_READINESS_POST_SESSION_TRIAGE_PLAN.md',
    'docs/divine/468_ALPHA_READINESS_PROGRESS_v20.md',
    'docs/divine/469_MEGA_RELEASE_ACCELERATION_25_MANUAL_KICKOFF_FEEDBACK_STORE_BETA_v76.md',
    'backend/scripts/validate_closed_alpha_manual_kickoff_packet_final_v1.py',
    'backend/scripts/validate_closed_alpha_recruitment_user_action_checklist_v1.py',
    'backend/scripts/validate_closed_alpha_session_result_placeholder_v1.py',
    'backend/scripts/validate_closed_alpha_feedback_intake_template_v1.py',
    'backend/scripts/validate_closed_alpha_post_session_triage_dry_run_v1.py',
    'backend/scripts/validate_store_beta_readiness_notes_v1.py',
    'backend/scripts/validate_v77_readiness_post_session_triage_plan_v1.py',
    'backend/scripts/validate_alpha_readiness_progress_v20_v1.py',
]
FLAGS = {
    'automated_live_invites': False,
    'email_send_enabled': False,
    'dm_send_enabled': False,
    'public_form_link_creation': False,
    'networking_enabled': False,
    'store_upload_performed': False,
    'play_console_changes_performed': False,
    'appstore_connect_changes_performed': False,
    'testflight_changes_performed': False,
    'build_generation_performed': False,
    'pii_collected_in_repo': False,
    'alpha_preview_menu_section_exposed': True,
    'home_root_changed': False,
    'tab_bar_changed': False,
    'production_navigation_changed': False,
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
    'real_asset_import': False,
    'asset_runtime_resolver_changed': False,
    'broad_commercial_release': False,
    'validator_weakening': False,
    'fake_pass': False,
}

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for rel in ARTIFACTS:
        if not (ROOT / rel).exists(): fail(f'missing {rel}')
    r = json.loads((ROOT / ROLLUP).read_text())
    if r.get('public_sync_tag') != TAG: fail('rollup.tag mismatch')
    for k, v in FLAGS.items():
        if r.get(k) != v: fail(f'rollup.{k}={r.get(k)!r} expected {v!r}')
    if r.get('new_screens'): fail('rollup.new_screens must be empty')
    if r.get('patched_screens'): fail('rollup.patched_screens must be empty')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
