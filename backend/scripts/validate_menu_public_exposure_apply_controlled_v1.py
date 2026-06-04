#!/usr/bin/env python3
"""validate_menu_public_exposure_apply_controlled_v1

Verifica:
- apply_contract e apply_result coerenti (applied=true, verdict APPLIED_CONTROLLED_SAFE)
- nuovo screen alpha-menu-preview.tsx presente e free di forbidden import/fetch
- 7 route esposte coincidono con scope lock v73
- home/tab/production navigation NON cambiati
- nessun cambio a story.tsx / combat.tsx / battle_engine / server.py
- nessun fetch/AsyncStorage/DB write nello screen
- MD5 invariants 8/8 confermati
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-MENU-PUBLIC-EXPOSURE-APPLY-CONTROLLED'
TAG = 'PUBLIC_SYNC_TAG_v74_MEGA_RELEASE_ACCELERATION_23_MENU_EXPOSURE_APPLY_CLOSED_ALPHA_KICKOFF'

CONTRACT = 'data/design/navigation/menu_public_exposure_apply_contract_v1.json'
RESULT = 'data/design/navigation/menu_public_exposure_apply_result_v1.json'
MARKER = 'data/design/navigation/menu_public_exposure_apply_marker_v1.json'
SCREEN = 'frontend/app/alpha-menu-preview.tsx'
SCOPE_LOCK = 'data/design/navigation/menu_public_exposure_scope_lock_v1.json'

MD5_INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
    'backend/server.py': '055df030553f4791e8cac14254f1b148',
    'frontend/app/combat.tsx': 'fc792a05b2ada6e677d80400732ae5c3',
    'frontend/app/story.tsx': '8520627b4e63f86821d73d8d3880bac3',
}

# Forbidden patterns nello screen alpha-menu-preview.tsx.
# Note: questi pattern devono NON apparire in linee di CODICE (import/call). I commenti
# che descrivono i guardrail sono ok perche' iniziano con '//'.
FORBIDDEN_IMPORT_PATTERNS = [
    r'^\s*import\s+.*from\s+["\']\.\.?/.*(story|combat).*["\']',
    r'^\s*import\s+.*battle_engine',
    r'^\s*import\s+.*@react-native-async-storage',
    r'^\s*import\s+.*axios',
]
# Active call patterns (non in commenti)
FORBIDDEN_CALL_PATTERNS = [
    (r'\bfetch\s*\(', 'fetch call'),
    (r'\bAsyncStorage\.', 'AsyncStorage call'),
    (r'/api/story/battle', 'api/story/battle path'),
    (r'/api/battle/simulate', 'api/battle/simulate path'),
]


def fail(msg: str) -> None:
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def md5_of(rel: str) -> str:
    return hashlib.md5((ROOT / rel).read_bytes()).hexdigest()


def strip_comments(src: str) -> str:
    # Rimuove line comments // ... e block comments /* ... */ per i check su codice attivo.
    src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)
    out = []
    for line in src.splitlines():
        idx = line.find('//')
        if idx >= 0:
            line = line[:idx]
        out.append(line)
    return '\n'.join(out)


def main() -> None:
    for rel in (CONTRACT, RESULT, MARKER, SCREEN, SCOPE_LOCK):
        if not (ROOT / rel).exists():
            fail(f'missing {rel}')

    contract = json.loads((ROOT / CONTRACT).read_text())
    result = json.loads((ROOT / RESULT).read_text())
    marker = json.loads((ROOT / MARKER).read_text())
    scope_lock = json.loads((ROOT / SCOPE_LOCK).read_text())

    # Tags
    for obj, name in ((contract, 'contract'), (result, 'result'), (marker, 'marker')):
        if obj.get('public_sync_tag') != TAG:
            fail(f'{name}.public_sync_tag mismatch')

    # Apply flags
    if contract.get('applied') is not True:
        fail('contract.applied must be true')
    if result.get('applied') is not True:
        fail('result.applied must be true')
    if result.get('verdict') != 'APPLIED_CONTROLLED_SAFE':
        fail('result.verdict must be APPLIED_CONTROLLED_SAFE')
    if marker.get('verdict') != 'APPLIED_CONTROLLED_SAFE':
        fail('marker.verdict must be APPLIED_CONTROLLED_SAFE')

    # Navigation invariants
    nav_false_keys = (
        'home_root_changed', 'tab_bar_changed', 'production_navigation_changed',
        'public_menu_routing_enabled', 'home_menu_routing_enabled',
    )
    for k in nav_false_keys:
        if contract.get(k) is not False:
            fail(f'contract.{k} must be false')
        if result.get(k) is not False:
            fail(f'result.{k} must be false')
    if marker.get('production_navigation_changed') is not False:
        fail('marker.production_navigation_changed must be false')

    # Exposed routes equality with scope lock
    contract_routes = set(contract.get('exposed_routes', []))
    result_routes = set(result.get('exposed_routes', []))
    scope_routes = set(scope_lock.get('locked_scope', {}).get('routes_allowed', []))
    if contract_routes != scope_routes:
        fail(f'contract.exposed_routes != scope_lock routes_allowed (diff={contract_routes ^ scope_routes})')
    if result_routes != scope_routes:
        fail(f'result.exposed_routes != scope_lock routes_allowed (diff={result_routes ^ scope_routes})')
    if contract.get('exposed_route_count') != 7:
        fail('contract.exposed_route_count must be 7')
    if result.get('exposed_route_count') != 7:
        fail('result.exposed_route_count must be 7')

    # Forbidden scope flags
    forbidden_false = (
        'db_writes', 'reward_grant', 'permanent_progress', 'account_persistence',
        'async_storage_persistence', 'real_asset_import', 'asset_runtime_resolver_changed',
        'backend_route_changed', 'server_py_changed', 'battle_engine_changed',
        'story_tsx_changed', 'combat_tsx_changed', 'story_tsx_imported',
        'combat_tsx_imported', 'api_story_battle_changed', 'api_battle_simulate_changed',
        'event_currency_enabled', 'arena_ranking_enabled', 'matchmaking_live',
        'inventory_mutation', 'wallet_mutation', 'premium_gems_mutation',
        'gacha_mutation', 'shop_mutation', 'vip_mutation', 'battle_pass_mutation',
        'character_bible_changed', 'hero_roster_changed', 'broad_commercial_release',
        'validator_weakening', 'fake_pass',
    )
    for k in forbidden_false:
        v = contract.get(k)
        expected = 0 if k == 'db_writes' else False
        if v != expected:
            fail(f'contract.{k}={v!r} expected {expected!r}')

    # Result must record file changes
    if result.get('files_created') != [SCREEN]:
        fail(f'result.files_created must be [{SCREEN!r}]')
    if result.get('files_modified') != []:
        fail('result.files_modified must be empty list')

    # MD5 invariants verifica live
    for rel, expected in MD5_INVARIANTS.items():
        got = md5_of(rel)
        if got != expected:
            fail(f'MD5 invariant drift on {rel}: got {got} expected {expected}')
    if result.get('md5_invariants_unchanged_after_apply') is not True:
        fail('result.md5_invariants_unchanged_after_apply must be true')

    # Static scan dello screen
    src = (ROOT / SCREEN).read_text()
    src_code = strip_comments(src)
    for pat in FORBIDDEN_IMPORT_PATTERNS:
        for line in src_code.splitlines():
            if re.search(pat, line):
                fail(f'forbidden import pattern {pat!r} in {SCREEN}: {line.strip()[:80]}')
    for pat, label in FORBIDDEN_CALL_PATTERNS:
        if re.search(pat, src_code):
            fail(f'forbidden {label} pattern in {SCREEN}')
    # Default export presente
    if 'export default function AlphaMenuPreview' not in src:
        fail('expected default export AlphaMenuPreview')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
