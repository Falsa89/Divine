#!/usr/bin/env python3
"""validate_menu_public_exposure_approval_handshake_v1

Validator OPTIONAL read-only per il pack v73.
Verifica:
- 3 JSON di contratto presenti (handshake, scope lock, execution forbidden scope)
- approval flags coerenti con stato 'blocked default'
- db_writes=0, no reward grant, no account persistence, no public exposure abilitata
- public_sync_tag v73 presente

Non esegue scritture, non importa moduli runtime, non tocca battle_engine.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-MENU-PUBLIC-EXPOSURE-APPROVAL-HANDSHAKE'
TAG = 'PUBLIC_SYNC_TAG_v73_MEGA_RELEASE_ACCELERATION_22_MENU_EXPOSURE_CLOSED_ALPHA'

FILES = [
    'data/design/navigation/menu_public_exposure_approval_handshake_v1.json',
    'data/design/navigation/menu_public_exposure_scope_lock_v1.json',
    'data/design/navigation/menu_public_exposure_execution_forbidden_scope_v1.json',
    'data/design/navigation/menu_public_exposure_approval_handshake_marker_v1.json',
]


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

    handshake = json.loads((ROOT / FILES[0]).read_text())
    scope_lock = json.loads((ROOT / FILES[1]).read_text())
    forbidden = json.loads((ROOT / FILES[2]).read_text())
    marker = json.loads((ROOT / FILES[3]).read_text())

    # Approval flags
    for key, expected in (
        ('manual_approval_required', True),
        ('manual_approval_received', False),
        ('approval_phrase_required', True),
        ('checksum_required', True),
        ('public_menu_exposure_apply_default', False),
        ('public_menu_exposure_enabled', False),
        ('production_navigation_changed', False),
        ('home_menu_routing_enabled', False),
        ('db_writes', 0),
        ('reward_grant', False),
        ('account_persistence', False),
    ):
        if handshake.get(key) != expected:
            fail(f'handshake.{key}={handshake.get(key)!r} expected {expected!r}')

    if handshake.get('public_sync_tag') != TAG:
        fail('handshake public_sync_tag mismatch')

    # Scope lock
    routes = scope_lock.get('locked_scope', {}).get('routes_allowed', [])
    required_routes = {
        'alpha-preview-hub',
        'first-session-onboarding-preview',
        'training-combat-onboarding-preview',
        'story-alpha-slice-preview',
        'boss-tower-alpha-loop-preview',
        'event-arena-alpha-gate-preview',
        'event-arena-first-alpha-slice-preview',
    }
    if not required_routes.issubset(set(routes)):
        fail(f'scope_lock missing required routes: {required_routes - set(routes)}')
    if scope_lock.get('locked_scope', {}).get('home_root_modification') is not False:
        fail('scope_lock home_root_modification must be False')
    if scope_lock.get('locked_scope', {}).get('db_writes') != 0:
        fail('scope_lock db_writes must be 0')

    # Execution forbidden scope must include critical items
    fb = set(forbidden.get('forbidden', []))
    needed = {
        'public_menu_exposure_apply_without_approval_phrase',
        'production_navigation_change_without_approval',
        'reward_grant',
        'db_writes',
        'real_asset_import_or_copy',
        'validator_weakening',
        'fake_pass',
    }
    missing = needed - fb
    if missing:
        fail(f'execution_forbidden_scope missing: {missing}')

    # Marker
    if marker.get('public_sync_tag') != TAG:
        fail('marker public_sync_tag mismatch')
    if marker.get('manual_approval_received') is not False:
        fail('marker manual_approval_received must be false')
    if marker.get('db_writes') != 0:
        fail('marker db_writes must be 0')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
