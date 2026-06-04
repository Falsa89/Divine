#!/usr/bin/env python3
"""validate_menu_public_exposure_observation_result_v1

Verifica observation_result + marker.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-MENU-PUBLIC-EXPOSURE-OBSERVATION-RESULT'
TAG = 'PUBLIC_SYNC_TAG_v74_MEGA_RELEASE_ACCELERATION_23_MENU_EXPOSURE_APPLY_CLOSED_ALPHA_KICKOFF'

RES = 'data/design/navigation/menu_public_exposure_observation_result_v1.json'
MRK = 'data/design/navigation/menu_public_exposure_observation_marker_v1.json'


def fail(msg: str) -> None:
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main() -> None:
    for rel in (RES, MRK):
        if not (ROOT / rel).exists():
            fail(f'missing {rel}')

    r = json.loads((ROOT / RES).read_text())
    m = json.loads((ROOT / MRK).read_text())

    if r.get('public_sync_tag') != TAG:
        fail('result.public_sync_tag mismatch')
    if r.get('observation_window_minutes', 0) < 60:
        fail('observation window must be >= 60')
    if r.get('verdict') != 'OBSERVATION_PASS_NO_ROLLBACK_REQUIRED':
        fail('result.verdict must be OBSERVATION_PASS_NO_ROLLBACK_REQUIRED')
    if r.get('rollback_triggered') is not False:
        fail('rollback_triggered must be false')
    if r.get('rollback_required') is not False:
        fail('rollback_required must be false')
    if r.get('db_writes') != 0:
        fail('db_writes must be 0')
    s = r.get('summary', {})
    if s.get('signals_pass', 0) < 8:
        fail('signals_pass must be >= 8')
    if s.get('signals_fail', 99) != 0:
        fail('signals_fail must be 0')
    if s.get('P0_fail', 99) != 0:
        fail('P0_fail must be 0')
    if s.get('P1_fail', 99) != 0:
        fail('P1_fail must be 0')
    sigs = r.get('signals', [])
    expected_ids = {
        'home_render_unchanged', 'tab_bar_unchanged', 'alpha_preview_section_renders',
        'deeplink_routes_resolve', 'no_crash_on_app_start', 'no_unexpected_db_writes',
        'no_unexpected_network_calls_to_battle_engine', 'no_async_storage_unexpected_writes',
    }
    got_ids = {x.get('id') for x in sigs}
    if not expected_ids.issubset(got_ids):
        fail(f'missing signal ids: {expected_ids - got_ids}')
    for sig in sigs:
        if sig.get('status') != 'pass':
            fail(f'signal {sig.get("id")} not pass')

    if m.get('public_sync_tag') != TAG:
        fail('marker.public_sync_tag mismatch')
    if m.get('rollback_triggered') is not False:
        fail('marker.rollback_triggered must be false')
    if m.get('verdict') != 'OBSERVATION_PASS_NO_ROLLBACK_REQUIRED':
        fail('marker.verdict mismatch')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
