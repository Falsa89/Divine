#!/usr/bin/env python3
"""validate_mega_release_acceleration_22_v73_rollup

Rollup meta validator per il pack v73.
Verifica esistenza di tutti gli artefatti + flag globali invariati.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'MEGA-RELEASE-ACCELERATION-22-v73-ROLLUP'
TAG = 'PUBLIC_SYNC_TAG_v73_MEGA_RELEASE_ACCELERATION_22_MENU_EXPOSURE_CLOSED_ALPHA'

ROLLUP_MARKER = 'data/design/release_acceleration/mega_release_acceleration_22_v73_rollup_marker_v1.json'

ALL_ARTIFACTS = [
    # Track A
    'data/design/navigation/menu_public_exposure_approval_handshake_v1.json',
    'data/design/navigation/menu_public_exposure_scope_lock_v1.json',
    'data/design/navigation/menu_public_exposure_execution_forbidden_scope_v1.json',
    # Track B
    'data/design/navigation/menu_public_exposure_dry_run_result_v1.json',
    'data/design/navigation/menu_public_exposure_apply_or_blocked_result_v1.json',
    # Track C
    'data/design/navigation/menu_public_exposure_candidate_route_map_v1.json',
    'data/design/navigation/menu_public_exposure_rollback_runbook_v1.json',
    'data/design/navigation/menu_public_exposure_observation_plan_v1.json',
    # Track D
    'data/design/qa/closed_alpha_testing_plan_v1.json',
    'data/design/qa/closed_alpha_tester_onboarding_template_v1.json',
    'data/design/qa/closed_alpha_feedback_form_template_v1.json',
    'data/design/qa/closed_alpha_bug_report_workflow_v1.json',
    # Track E
    'data/design/qa/v72_p3_polish_backlog_plan_v1.json',
    'data/design/qa/v72_p3_polish_deferred_decision_v1.json',
    # Track F
    'data/design/qa/menu_exposure_closed_alpha_readiness_matrix_v1.json',
    'data/design/release_acceleration/alpha_readiness_progress_report_v17.json',
    # Markers
    'data/design/navigation/menu_public_exposure_approval_handshake_marker_v1.json',
    'data/design/navigation/menu_public_exposure_dryrun_blocked_marker_v1.json',
    'data/design/navigation/menu_public_exposure_route_rollback_marker_v1.json',
    'data/design/qa/closed_alpha_testing_plan_marker_v1.json',
    'data/design/qa/v72_p3_polish_backlog_marker_v1.json',
    'data/design/qa/menu_exposure_closed_alpha_readiness_marker_v1.json',
    ROLLUP_MARKER,
    # Docs
    'docs/divine/439_MENU_PUBLIC_EXPOSURE_APPROVAL_HANDSHAKE.md',
    'docs/divine/440_MENU_PUBLIC_EXPOSURE_DRY_RUN_AND_BLOCKED_APPLY.md',
    'docs/divine/441_MENU_PUBLIC_EXPOSURE_ROUTE_MAP_ROLLBACK.md',
    'docs/divine/442_CLOSED_ALPHA_TESTING_PLAN.md',
    'docs/divine/443_v72_P3_POLISH_BACKLOG_PLAN.md',
    'docs/divine/444_MENU_EXPOSURE_CLOSED_ALPHA_READINESS_QA.md',
    'docs/divine/445_MEGA_RELEASE_ACCELERATION_22_MENU_EXPOSURE_CLOSED_ALPHA_v73.md',
    # Validators
    'backend/scripts/validate_menu_public_exposure_approval_handshake_v1.py',
    'backend/scripts/validate_menu_public_exposure_dryrun_blocked_v1.py',
    'backend/scripts/validate_menu_public_exposure_route_rollback_v1.py',
    'backend/scripts/validate_closed_alpha_testing_plan_v1.py',
    'backend/scripts/validate_v72_p3_polish_backlog_v1.py',
    'backend/scripts/validate_menu_exposure_closed_alpha_readiness_v1.py',
]

ROLLUP_FLAGS_REQUIRED = {
    'public_menu_exposure_enabled': False,
    'production_navigation_changed': False,
    'home_menu_routing_enabled': False,
    'manual_approval_received': False,
    'approval_phrase_required': True,
    'public_menu_exposure_apply_result': 'BLOCKED_NOT_APPLIED_SAFE',
    'closed_alpha_invites_enabled': False,
    'db_writes': 0,
    'reward_grant_enabled': False,
    'permanent_progress_enabled': False,
    'battle_engine_runtime_used': False,
    'backend_route_changed': False,
    'server_py_changed': False,
    'story_tsx_changed': False,
    'combat_tsx_changed': False,
    'event_currency_enabled': False,
    'arena_ranking_enabled': False,
    'matchmaking_live': False,
    'account_flag_writes': False,
    'async_storage_persistence': False,
    'real_asset_import': False,
    'asset_runtime_resolver_changed': False,
    'character_bible_changed': False,
    'hero_roster_changed': False,
    'validator_weakening': False,
    'fake_pass': False,
}


def fail(msg: str) -> None:
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main() -> None:
    for rel in ALL_ARTIFACTS:
        p = ROOT / rel
        if not p.exists():
            fail(f'missing artifact {rel}')

    rollup = json.loads((ROOT / ROLLUP_MARKER).read_text())
    if rollup.get('public_sync_tag') != TAG:
        fail('rollup public_sync_tag mismatch')
    for k, v in ROLLUP_FLAGS_REQUIRED.items():
        if rollup.get(k) != v:
            fail(f'rollup.{k}={rollup.get(k)!r} expected {v!r}')

    if rollup.get('new_screens'):
        fail('rollup.new_screens must be empty')
    if rollup.get('patched_screens'):
        fail('rollup.patched_screens must be empty')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
