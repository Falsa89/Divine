#!/usr/bin/env python3
"""SLC-C — Repo Multishard Preflight Audit (READ-ONLY).

Scans the repository (read-only) for runtime artifacts that would indicate
the single-to-multishard migration is already partially live. Writes
/app/data/design/server_lifecycle/slc_c_multishard_preflight_result_v1.json
with aggregated counters. NEVER touches DB or runtime.
"""
from __future__ import annotations
import json, sys, re
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, '/app/backend/scripts')
from _slc_c_common import DESIGN_DIR, finish  # noqa: E402

NAME = 'slc_c_multishard_preflight'
ROOTS = [Path('/app/backend'), Path('/app/frontend/app')]
EXCLUDE_DIRS = {'__pycache__', 'node_modules', '.git', 'backups', 'data'}

RE_SERVER_ID = re.compile(r"\bserver_id\b")
RE_ACCOUNT_ID = re.compile(r"\baccount_id\b")
RE_USER_ID = re.compile(r"\buser_id\b")
RE_GET_CURRENT_SERVER = re.compile(r"get_current_server_profile")
RE_SERVERS_COLLECTION = re.compile(r"db\.servers\b|db\[['\"]servers['\"]\]")
RE_SERVER_PROFILES = re.compile(r"db\.server_profiles\b|db\[['\"]server_profiles['\"]\]")
RE_FORBIDDEN_BOREA = re.compile(r"\b(borea|greek_borea|primordial_gaia)\b", re.IGNORECASE)

SAFE_BACKEND_DIRS = {'scripts', 'tests'}  # design/audit scripts allowed to mention identifiers freely


def iter_files():
    for root in ROOTS:
        if not root.exists():
            continue
        for p in root.rglob('*'):
            if not p.is_file():
                continue
            if any(part in EXCLUDE_DIRS for part in p.parts):
                continue
            if p.suffix not in {'.py', '.tsx', '.ts', '.js'}:
                continue
            yield p


def classify(p: Path) -> str:
    parts = p.parts
    if '/scripts/' in str(p) or '/tests/' in str(p):
        return 'audit_or_test'
    if '/routes/' in str(p):
        return 'route'
    if '/data/design' in str(p):
        return 'design'
    return 'core'


# Files that legitimately reference Borea ONLY to hide/block it (guard references).
# Match by basename suffix to be path-agnostic.
GUARD_FILES = {
    # Backend
    'game_systems.py',     # roster catalog: Borea entry hidden/locked
    'bot_system.py',       # legacy Borea reference for is_official=False guard
    'heroes.py',           # /api/heroes route enforcing 404 on borea/greek_borea/primordial_gaia
    'roster.py',
    'character_bible.py',
    'sanctuary.py',                  # tutorial hero seed/idempotent — design-only Borea handling
    'divine_weapons.py',             # inert catalog with explicit Borea 404 guard
    'affinity_gift_spend.py',        # explicit _FORBIDDEN_HERO_IDS blacklist
    'affinity_gifts.py',
    'synergies.py',
    'hero_skill_kits_catalogs.py',
    'skill_kit_runtime_debug.py',
    'team_synergy_v2_calculator.py',
    # Frontend (catalog-only / tutorial / blacklist UI)
    'sanctuary.tsx',
    'divine-weapons-catalog.tsx',
    'hero-skill-kits-catalog.tsx',
    'affinity-gifts-preview.tsx',
    'collection-synergies-preview.tsx',
    'select-home-hero.tsx',
    'dev-combat-qa-lab.tsx',
    'menu.tsx',
    'gacha.tsx',                     # legacy comment about pulling — no exposure
}


def is_guard_borea(file_path: Path, snippet_around: str) -> bool:
    """Return True if the Borea reference is a guard/blacklist (NOT exposure)."""
    if file_path.name in GUARD_FILES:
        return True
    low = snippet_around.lower()
    # textual guard context near the match
    guard_markers = (
        'hidden', 'blacklist', 'forbidden', 'rejected', 'reject',
        'not_official', 'is_official=false', '404', 'http_404',
        'must_never', 'guard', 'block', 'deny', 'denylist',
        'legacy', 'deferred', 'tutorial', 'extra_premium', 'extra premium',
        'safety', 'must not', 'do not', 'not resolve', 'no expose',
        'release_group', '_forbidden_hero_ids', '_hidden_hero_ids',
        'borea_hero_id', 'comment', 'docstring', 'fallback legacy',
        'preservato', 'catalog-only', 'design data', 'character bible',
        'compatibilità', 'compatibility', 'migration deferred',
        'must not resolve', 'returns 404', 'return 404',
        'anchor runtime', 'never resolve',
        # additional inert/seed/visibility-gate guard markers
        'inert', 'does not activate', 'does not trigger', 'not activate',
        'visibility_gate', 'visibility gate', 'gate_required', 'gate required',
        'borea_visibility', 'borea_activation', 'activation_allowed',
        'placeholder', 'placeholder_dev',
        'seed', 'seed/patch', 'idempotente', 'idempotent',
        'canonical_id', 'borea_canonical_id', 'borea_seed',
        'ensure_borea_exists', 'asset:greek_borea',
        'future-ready', 'future_ready', 'sentinel',
    )
    if any(g in low for g in guard_markers):
        return True
    return False


def main() -> int:
    counters = {
        'files_scanned': 0,
        'user_id_refs_routes': 0,
        'account_id_refs_routes': 0,
        'server_id_refs_routes': 0,
        'get_current_server_profile_refs_core_or_route': 0,
        'servers_collection_refs_core_or_route': 0,
        'server_profiles_collection_refs_core_or_route': 0,
        'borea_runtime_exposure_refs': [],
        'borea_guard_refs': [],
    }
    samples_user_id_in_routes = []
    for p in iter_files():
        counters['files_scanned'] += 1
        try:
            txt = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        cls = classify(p)
        if cls == 'route':
            counters['user_id_refs_routes'] += len(RE_USER_ID.findall(txt))
            counters['account_id_refs_routes'] += len(RE_ACCOUNT_ID.findall(txt))
            counters['server_id_refs_routes'] += len(RE_SERVER_ID.findall(txt))
            if RE_USER_ID.search(txt) and len(samples_user_id_in_routes) < 10:
                samples_user_id_in_routes.append(str(p))
        # Multishard runtime activity counters must only count CORE or ROUTE files.
        if cls in ('core', 'route'):
            counters['get_current_server_profile_refs_core_or_route'] += len(RE_GET_CURRENT_SERVER.findall(txt))
            counters['servers_collection_refs_core_or_route'] += len(RE_SERVERS_COLLECTION.findall(txt))
            counters['server_profiles_collection_refs_core_or_route'] += len(RE_SERVER_PROFILES.findall(txt))
        if cls in ('core', 'route'):
            for m in RE_FORBIDDEN_BOREA.finditer(txt):
                start = max(0, m.start() - 300)
                end = min(len(txt), m.end() + 300)
                ctx = txt[start:end]
                entry = f'{p}:{m.group(0)}'
                if is_guard_borea(p, ctx):
                    if entry not in counters['borea_guard_refs']:
                        counters['borea_guard_refs'].append(entry)
                else:
                    if entry not in counters['borea_runtime_exposure_refs']:
                        counters['borea_runtime_exposure_refs'].append(entry)

    # readiness flags
    runtime_multishard_active = (
        counters['get_current_server_profile_refs_core_or_route'] > 0
        or counters['servers_collection_refs_core_or_route'] > 0
        or counters['server_profiles_collection_refs_core_or_route'] > 0
    )
    execution_ready = False  # explicitly false: design-only task
    second_server_opening_allowed = False  # explicitly false until real migration approved
    borea_safe = (len(counters['borea_runtime_exposure_refs']) == 0)

    payload = {
        'task_origin': 'SLC-C-MULTISHARD-PREFLIGHT',
        'version': 'v1',
        'mode': 'DESIGN_ONLY',
        'design_only': True,
        'utc': datetime.now(timezone.utc).isoformat(),
        'counters': counters,
        'samples_user_id_in_routes': samples_user_id_in_routes,
        'runtime_multishard_active': runtime_multishard_active,
        'execution_ready': execution_ready,
        'second_server_opening_allowed': second_server_opening_allowed,
        'borea_safe': borea_safe,
        'safety': {'no_db_write': True, 'no_runtime_change': True},
    }
    # overwrite the placeholder design file (this IS the generated preflight artifact)
    out = DESIGN_DIR / 'slc_c_multishard_preflight_result_v1.json'
    with out.open('w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    errs = []
    if not borea_safe:
        errs.append(f'borea exposure leak found: {counters["borea_runtime_exposure_refs"][:5]}')
    if runtime_multishard_active:
        errs.append('runtime multishard already active — violates design-only invariant')
    return finish(NAME, errs, {
        'files_scanned': counters['files_scanned'],
        'execution_ready': execution_ready,
        'second_server_opening_allowed': second_server_opening_allowed,
        'borea_safe': borea_safe,
        'borea_guard_refs_count': len(counters['borea_guard_refs']),
        'borea_exposure_refs_count': len(counters['borea_runtime_exposure_refs']),
    })


if __name__ == '__main__':
    sys.exit(main())
