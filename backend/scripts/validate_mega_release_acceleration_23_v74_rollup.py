#!/usr/bin/env python3
"""validate_mega_release_acceleration_23_v74_rollup

Rollup meta validator pack v74.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'MEGA-RELEASE-ACCELERATION-23-v74-ROLLUP'
TAG = 'PUBLIC_SYNC_TAG_v74_MEGA_RELEASE_ACCELERATION_23_MENU_EXPOSURE_APPLY_CLOSED_ALPHA_KICKOFF'

ROLLUP = 'data/design/release_acceleration/mega_release_acceleration_23_v74_rollup_marker_v1.json'

ALL_ARTIFACTS = [
    # Lane 1 - Approval verification
    'data/design/navigation/menu_public_exposure_approval_verification_v1.json',
    # Lane 2 - Apply contract + result
    'data/design/navigation/menu_public_exposure_apply_contract_v1.json',
    'data/design/navigation/menu_public_exposure_apply_result_v1.json',
    'data/design/navigation/menu_public_exposure_apply_marker_v1.json',
    # Lane 3 - Observation
    'data/design/navigation/menu_public_exposure_observation_result_v1.json',
    'data/design/navigation/menu_public_exposure_observation_marker_v1.json',
    # Lane 4 - Closed alpha kickoff
    'data/design/qa/closed_alpha_kickoff_gate_v1.json',
    'data/design/qa/closed_alpha_kickoff_runbook_v1.json',
    'data/design/qa/closed_alpha_kickoff_packet_v1.json',
    'data/design/qa/closed_alpha_kickoff_gate_marker_v1.json',
    # Lane 5 - P3 carry-forward
    'data/design/qa/v72_p3_polish_carryforward_v1.json',
    'data/design/qa/v72_p3_polish_carryforward_marker_v1.json',
    # Lane 6 - Progress v18
    'data/design/release_acceleration/alpha_readiness_progress_report_v18.json',
    'data/design/release_acceleration/alpha_readiness_progress_report_v18_marker_v1.json',
    # Rollup
    ROLLUP,
    # New screen
    'frontend/app/alpha-menu-preview.tsx',
    # Docs
    'docs/divine/446_MENU_PUBLIC_EXPOSURE_APPROVAL_VERIFICATION.md',
    'docs/divine/447_MENU_PUBLIC_EXPOSURE_APPLY_CONTROLLED.md',
    'docs/divine/448_MENU_PUBLIC_EXPOSURE_OBSERVATION_RESULT.md',
    'docs/divine/449_CLOSED_ALPHA_KICKOFF_GATE_RUNBOOK_PACKET.md',
    'docs/divine/450_v72_P3_POLISH_CARRYFORWARD.md',
    'docs/divine/451_ALPHA_READINESS_PROGRESS_v18.md',
    'docs/divine/452_MEGA_RELEASE_ACCELERATION_23_MENU_EXPOSURE_APPLY_CLOSED_ALPHA_KICKOFF_v74.md',
    # Validators
    'backend/scripts/validate_menu_public_exposure_approval_verification_v1.py',
    'backend/scripts/validate_menu_public_exposure_apply_controlled_v1.py',
    'backend/scripts/validate_menu_public_exposure_observation_result_v1.py',
    'backend/scripts/validate_closed_alpha_kickoff_gate_v1.py',
    'backend/scripts/validate_v72_p3_polish_carryforward_v1.py',
    'backend/scripts/validate_alpha_readiness_progress_v18_v1.py',
]

ROLLUP_FLAGS = {
    'applied': True,
    'apply_verdict': 'APPLIED_CONTROLLED_SAFE',
    'approval_phrase_received': True,
    'approval_checksum_verified': True,
    'exposed_route_count': 7,
    'production_navigation_changed': False,
    'home_root_changed': False,
    'tab_bar_changed': False,
    'public_menu_routing_enabled': False,
    'home_menu_routing_enabled': False,
    'alpha_preview_menu_section_exposed': True,
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


def fail(msg: str) -> None:
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main() -> None:
    for rel in ALL_ARTIFACTS:
        if not (ROOT / rel).exists():
            fail(f'missing artifact {rel}')

    rollup = json.loads((ROOT / ROLLUP).read_text())
    if rollup.get('public_sync_tag') != TAG:
        fail('rollup.public_sync_tag mismatch')
    for k, v in ROLLUP_FLAGS.items():
        if rollup.get(k) != v:
            fail(f'rollup.{k}={rollup.get(k)!r} expected {v!r}')
    if rollup.get('new_screens') != ['frontend/app/alpha-menu-preview.tsx']:
        fail('rollup.new_screens mismatch')
    if rollup.get('patched_screens'):
        fail('rollup.patched_screens must be empty')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
