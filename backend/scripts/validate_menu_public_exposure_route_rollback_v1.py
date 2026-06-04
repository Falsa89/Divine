#!/usr/bin/env python3
"""validate_menu_public_exposure_route_rollback_v1

Verifica:
- route map con 7 route candidate
- rollback runbook con <=5 step e nessuna data loss
- observation plan con signals e rollback_trigger
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-MENU-PUBLIC-EXPOSURE-ROUTE-ROLLBACK'
TAG = 'PUBLIC_SYNC_TAG_v73_MEGA_RELEASE_ACCELERATION_22_MENU_EXPOSURE_CLOSED_ALPHA'

FILES = [
    'data/design/navigation/menu_public_exposure_candidate_route_map_v1.json',
    'data/design/navigation/menu_public_exposure_rollback_runbook_v1.json',
    'data/design/navigation/menu_public_exposure_observation_plan_v1.json',
    'data/design/navigation/menu_public_exposure_route_rollback_marker_v1.json',
]

REQUIRED_ROUTES = {
    'alpha-preview-hub',
    'first-session-onboarding-preview',
    'training-combat-onboarding-preview',
    'story-alpha-slice-preview',
    'boss-tower-alpha-loop-preview',
    'event-arena-alpha-gate-preview',
    'event-arena-first-alpha-slice-preview',
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

    rmap = json.loads((ROOT / FILES[0]).read_text())
    rb = json.loads((ROOT / FILES[1]).read_text())
    obs = json.loads((ROOT / FILES[2]).read_text())
    mrk = json.loads((ROOT / FILES[3]).read_text())

    routes = {r.get('route') for r in rmap.get('routes', [])}
    if not REQUIRED_ROUTES.issubset(routes):
        fail(f'route_map missing: {REQUIRED_ROUTES - routes}')
    if rmap.get('total_routes') != 7:
        fail('route_map.total_routes must be 7')
    if rmap.get('production_navigation_changed') is not False:
        fail('route_map.production_navigation_changed must be false')
    if rmap.get('home_menu_routing_enabled') is not False:
        fail('route_map.home_menu_routing_enabled must be false')
    if rmap.get('db_writes') != 0:
        fail('route_map.db_writes must be 0')

    if rb.get('max_steps', 99) > 5:
        fail('rollback.max_steps must be <=5')
    if len(rb.get('steps', [])) > 5:
        fail('rollback steps len > 5')
    if rb.get('data_loss_on_rollback') is not False:
        fail('rollback.data_loss_on_rollback must be false')
    if rb.get('db_writes') != 0:
        fail('rollback.db_writes must be 0')

    if obs.get('observation_window_minutes', 0) <= 0:
        fail('observation.window_minutes must be > 0')
    if not obs.get('signals'):
        fail('observation.signals empty')
    if not obs.get('rollback_trigger'):
        fail('observation.rollback_trigger missing')
    if obs.get('db_writes') != 0:
        fail('observation.db_writes must be 0')

    if mrk.get('public_sync_tag') != TAG:
        fail('marker.public_sync_tag mismatch')
    if mrk.get('route_count') != 7:
        fail('marker.route_count must be 7')
    if mrk.get('db_writes') != 0:
        fail('marker.db_writes must be 0')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
