#!/usr/bin/env python3
"""validate_mega_release_acceleration_26_v77_rollup"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'MEGA-RELEASE-ACCELERATION-26-v77-ROLLUP'
TAG = 'PUBLIC_SYNC_TAG_v77_MEGA_RELEASE_ACCELERATION_26_FEEDBACK_AGGREGATION_TRIAGE_WRAP_v78_READINESS'
ROLLUP = 'data/design/release_acceleration/mega_release_acceleration_26_v77_rollup_marker_v1.json'
ARTIFACTS = [
    'data/design/qa/closed_alpha_feedback_input_discovery_v1.json',
    'data/design/qa/closed_alpha_feedback_input_discovery_marker_v1.json',
    'data/design/qa/closed_alpha_feedback_aggregation_result_v1.json',
    'data/design/qa/closed_alpha_feedback_aggregation_result_marker_v1.json',
    'data/design/qa/closed_alpha_findings_triage_result_v1.json',
    'data/design/qa/closed_alpha_findings_triage_result_marker_v1.json',
    'data/design/qa/closed_alpha_wrap_summary_v1.json',
    'data/design/qa/closed_alpha_wrap_summary_marker_v1.json',
    'data/design/release_acceleration/deferred_store_asset_summary_v1.json',
    'data/design/release_acceleration/deferred_store_asset_summary_marker_v1.json',
    'data/design/release_acceleration/v78_readiness_plan_v1.json',
    'data/design/release_acceleration/v78_readiness_plan_marker_v1.json',
    'data/design/release_acceleration/alpha_readiness_progress_report_v21.json',
    'data/design/release_acceleration/alpha_readiness_progress_report_v21_marker_v1.json',
    ROLLUP,
    'docs/divine/470_CLOSED_ALPHA_FEEDBACK_INPUT_DISCOVERY.md',
    'docs/divine/471_CLOSED_ALPHA_FEEDBACK_AGGREGATION_RESULT.md',
    'docs/divine/472_CLOSED_ALPHA_FINDINGS_TRIAGE_RESULT.md',
    'docs/divine/473_CLOSED_ALPHA_WRAP_SUMMARY.md',
    'docs/divine/474_DEFERRED_STORE_ASSET_SUMMARY.md',
    'docs/divine/475_v78_READINESS_PLAN.md',
    'docs/divine/476_ALPHA_READINESS_PROGRESS_v21.md',
    'docs/divine/477_MEGA_RELEASE_ACCELERATION_26_FEEDBACK_TRIAGE_WRAP_v78_READINESS_v77.md',
    'backend/scripts/validate_closed_alpha_feedback_input_discovery_v1.py',
    'backend/scripts/validate_closed_alpha_feedback_aggregation_result_v1.py',
    'backend/scripts/validate_closed_alpha_findings_triage_result_v1.py',
    'backend/scripts/validate_closed_alpha_wrap_summary_v1.py',
    'backend/scripts/validate_deferred_store_asset_summary_v1.py',
    'backend/scripts/validate_v78_readiness_plan_v1.py',
    'backend/scripts/validate_alpha_readiness_progress_v21_v1.py',
]
FLAGS = {
    'actual_feedback_received': False,
    'input_sessions': 0,
    'open_findings_count': 0,
    'go_no_go_decision': 'DEFERRED_PENDING_FEEDBACK',
    'invented_data': False,
    'network_fetch_performed': False,
    'external_form_fetch_performed': False,
    'automated_live_invites': False,
    'closed_alpha_invites_enabled': False,
    'store_upload_performed': False,
    'play_console_changes_performed': False,
    'appstore_connect_changes_performed': False,
    'testflight_changes_performed': False,
    'build_generation_performed': False,
    'pii_collected_in_repo': False,
    'alias_only': True,
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
