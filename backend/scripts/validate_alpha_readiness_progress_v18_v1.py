#!/usr/bin/env python3
"""validate_alpha_readiness_progress_v18_v1

Verifica progress report v18 + marker.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-ALPHA-READINESS-PROGRESS-v18'
TAG = 'PUBLIC_SYNC_TAG_v74_MEGA_RELEASE_ACCELERATION_23_MENU_EXPOSURE_APPLY_CLOSED_ALPHA_KICKOFF'

REPORT = 'data/design/release_acceleration/alpha_readiness_progress_report_v18.json'
MRK = 'data/design/release_acceleration/alpha_readiness_progress_report_v18_marker_v1.json'

EXPECTED = {
    'menu_public_exposure_execution': 'applied_controlled_safe_v74',
    'menu_public_exposure_apply_result': 'APPLIED_CONTROLLED_SAFE',
    'alpha_preview_menu_section_exposed': True,
    'alpha_preview_menu_section_route_count': 7,
    'home_root_changed': False,
    'tab_bar_changed': False,
    'production_navigation_changed': False,
    'public_menu_routing_enabled': False,
    'home_menu_routing_enabled': False,
    'closed_alpha_kickoff_gate': 'ready_v74',
    'closed_alpha_invites_enabled': False,
    'closed_alpha_manual_recruitment_only': True,
    'alpha_internal_qa_run': 'completed_v72',
    'alpha_p3_backlog': 'carryforward_v74',
    'alpha_p3_backlog_count': 3,
    'hero_asset_staging_import': 'deferred_waiting_for_real_asset_pack',
    'reward_grant': False,
    'permanent_progress': False,
    'account_persistence': False,
    'db_writes': 0,
    'battle_engine_runtime': False,
    'real_asset_import': False,
    'broad_commercial_release': False,
    'manual_approval_received': True,
    'approval_checksum_verified': True,
    'validator_weakening': False,
    'fake_pass': False,
}


def fail(msg: str) -> None:
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main() -> None:
    for rel in (REPORT, MRK):
        if not (ROOT / rel).exists():
            fail(f'missing {rel}')
    rep = json.loads((ROOT / REPORT).read_text())
    mrk = json.loads((ROOT / MRK).read_text())

    if rep.get('public_sync_tag') != TAG:
        fail('report.public_sync_tag mismatch')
    for k, v in EXPECTED.items():
        if rep.get(k) != v:
            fail(f'report.{k}={rep.get(k)!r} expected {v!r}')

    if mrk.get('public_sync_tag') != TAG:
        fail('marker.public_sync_tag mismatch')
    if mrk.get('menu_public_exposure_execution') != 'applied_controlled_safe_v74':
        fail('marker mismatch')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
