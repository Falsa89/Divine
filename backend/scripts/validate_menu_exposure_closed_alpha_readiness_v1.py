#!/usr/bin/env python3
"""validate_menu_exposure_closed_alpha_readiness_v1

Verifica readiness matrix + progress report v17.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-MENU-EXPOSURE-CLOSED-ALPHA-READINESS'
TAG = 'PUBLIC_SYNC_TAG_v73_MEGA_RELEASE_ACCELERATION_22_MENU_EXPOSURE_CLOSED_ALPHA'

FILES = [
    'data/design/qa/menu_exposure_closed_alpha_readiness_matrix_v1.json',
    'data/design/release_acceleration/alpha_readiness_progress_report_v17.json',
    'data/design/qa/menu_exposure_closed_alpha_readiness_marker_v1.json',
]

REQUIRED_AREAS = {
    'approval_handshake', 'scope_lock', 'dry_run_evidence', 'route_map',
    'rollback_runbook', 'observation_plan', 'closed_alpha_plan',
    'feedback_form', 'bug_report_workflow', 'p3_polish_backlog',
}

EXPECTED_PROGRESS = {
    'menu_public_exposure_execution': 'blocked_not_applied_safe_v73',
    'menu_public_exposure_design': 'ready_v72',
    'closed_alpha_testing_plan': 'ready_v73',
    'closed_alpha_invites_enabled': False,
    'public_menu_exposure': False,
    'production_navigation_changed': False,
    'home_menu_routing_enabled': False,
    'alpha_internal_qa_run': 'completed_v72',
    'alpha_p3_backlog': 'deferred_v73',
    'hero_asset_staging_import': 'deferred_waiting_for_real_asset_pack',
    'reward_grant': False,
    'permanent_progress': False,
    'account_persistence': False,
    'db_writes': 0,
    'battle_engine_runtime': False,
    'real_asset_import': False,
}


def fail(msg: str) -> None:
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main() -> None:
    for rel in FILES:
        p = ROOT / rel
        if not p.exists():
            fail(f'missing {rel}')
        try:
            json.loads(p.read_text())
        except Exception as e:
            fail(f'invalid JSON {rel}: {e}')

    mat = json.loads((ROOT / FILES[0]).read_text())
    prog = json.loads((ROOT / FILES[1]).read_text())
    mrk = json.loads((ROOT / FILES[2]).read_text())

    cells = {c.get('area'): c.get('state') for c in mat.get('cells', [])}
    if set(cells.keys()) != REQUIRED_AREAS:
        fail(f'matrix areas mismatch: missing {REQUIRED_AREAS - set(cells.keys())}')
    for area, state in cells.items():
        if state != 'ready':
            fail(f'matrix area {area} state must be ready, got {state}')
    if mat.get('public_menu_exposure_apply_state') != 'blocked':
        fail('matrix.public_menu_exposure_apply_state must be blocked')
    if mat.get('db_writes') != 0:
        fail('matrix.db_writes must be 0')

    for k, v in EXPECTED_PROGRESS.items():
        if prog.get(k) != v:
            fail(f'progress.{k}={prog.get(k)!r} expected {v!r}')
    if prog.get('public_sync_tag') != TAG:
        fail('progress.public_sync_tag mismatch')
    if prog.get('manual_approval_received') is not False:
        fail('progress.manual_approval_received must be false')

    if mrk.get('public_sync_tag') != TAG:
        fail('marker.public_sync_tag mismatch')
    if mrk.get('public_menu_exposure_apply_state') != 'blocked':
        fail('marker.public_menu_exposure_apply_state must be blocked')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
