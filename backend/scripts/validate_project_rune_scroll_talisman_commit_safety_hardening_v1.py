#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator: PROJECT_RUNE_SCROLL_TALISMAN_COMMIT_SAFETY_HARDENING_PACK (v38 Track B)
Phase: PHASE_8B_RUNE_SCROLL_TALISMAN_COMMIT_SAFETY_HARDENING
Mode:  BUILD_SYSTEM_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_COMMIT

Asserisce gli invarianti del nuovo route preview-only Rune/Scroll/Talisman.
Distinzione canonica Rune ≠ Gemme ≠ Artifact ≠ Divine Weapon esplicita.
Nessuna mutazione hero rune slot / rune inventory. Nessun consumo
materiali/oro/gemme. Nessun premium users.gems. Nessun BP Delta. Zero DB.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

BACKEND_ROUTE_REL = 'backend/routes/rune_scroll_talisman_safety_preview.py'
DESIGN_REL = 'data/design/rune_scroll_talisman/rune_scroll_talisman_commit_safety_hardening_v1.json'
SCHEMA_REL = 'data/design/rune_scroll_talisman/rune_scroll_talisman_commit_request_schema_v1.json'
GUARD_REL = 'data/design/rune_scroll_talisman/rune_scroll_talisman_guard_policy_v1.json'
PROOF_REL = 'data/design/rune_scroll_talisman/rune_scroll_talisman_safety_proof_marker_v1.json'
DOC_REL = 'docs/divine/243_RUNE_SCROLL_TALISMAN_COMMIT_SAFETY_HARDENING.md'
VALIDATOR_REL = 'backend/scripts/validate_project_rune_scroll_talisman_commit_safety_hardening_v1.py'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'
LEGACY_FORGE_REL = 'backend/routes/forge.py'

FEATURE_FLAG = 'RUNE_SCROLL_TALISMAN_SAFETY_PREVIEW_ENABLED'
NAMESPACE = '/api/rune-scroll-talisman-safety-preview'
ENDPOINTS = ['/config', '/validate-request', '/guard-plan-preview', '/idempotency-preview']

REQUIRED_REQUEST_FIELDS = [
    'request_id', 'idempotency_key', 'operation_type', 'user_id', 'server_id',
    'hero_instance_id', 'rune_instance_id', 'target_slot_index',
    'fodder_rune_instance_ids',
    'expected_hero_version', 'expected_rune_inventory_version',
    'expected_materials_version', 'client_trace_id', 'created_at',
]

REQUIRED_GUARD_CHECKS = [
    'auth_required', 'user_owns_hero', 'user_owns_rune', 'hero_exists',
    'rune_exists', 'rune_not_locked', 'rune_not_favorite',
    'rune_not_equipped_elsewhere', 'target_slot_index_valid',
    'target_slot_unlocked_by_hero_level_or_stars',
    'rune_family_valid_for_slot', 'rune_type_valid_for_hero',
    'rune_rarity_valid', 'rune_role_element_faction_restrictions_future',
    'fodder_runes_owned', 'fodder_runes_not_locked',
    'fodder_runes_not_equipped', 'no_duplicate_fodder_ids',
    'base_rune_not_in_fodder',
    'hero_not_in_active_battle_commit_window',
    'hero_pvp_defense_policy_defined',
    'hero_guild_war_defense_policy_defined',
    'material_cost_policy_defined_but_not_charged',
    'currency_cost_policy_defined_but_not_charged',
    'same_request_id_not_committed', 'idempotency_key_required',
    'expected_versions_match', 'premium_users_gems_not_used',
    'atomic_commit_required_future', 'rollback_policy_required_future',
    'audit_log_required_future', 'bp_delta_not_triggered_in_preview',
]

PROOF_REQUIRED = {
    'rune_scroll_talisman_safety_preview_route_created': True,
    'rune_scroll_talisman_live_commit_enabled': False,
    'hero_rune_slot_mutation_enabled': False,
    'rune_inventory_mutation_enabled': False,
    'materials_consumed': False,
    'currency_consumed': False,
    'premium_gems_currency_used': False,
    'bp_delta_triggered': False,
    'reward_grant_enabled': False,
    'exp_grant_enabled': False,
    'rune_is_not_gemme': True,
    'rune_is_not_artifact': True,
    'rune_is_not_divine_weapon': True,
    'economy_changed': False,
    'gacha_changed': False,
    'bp_vip_shop_changed': False,
    'material_raid_changed': False,
    'gem_socket_changed': False,
    'forge_legacy_changed': False,
    'battle_engine_changed': False,
    'combat_tsx_changed': False,
    'story_tsx_changed': False,
    'home_routes_changed': False,
    'artifact_runtime_changed': False,
    'divine_weapon_runtime_changed': False,
    'guild_war_runtime_changed': False,
}

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def repo(p: str) -> str:
    return os.path.join(REPO_ROOT, p)


def read_text(rel: str) -> str:
    return open(repo(rel), 'r', encoding='utf-8').read()


def load_json(rel: str):
    return json.load(open(repo(rel), 'r', encoding='utf-8'))


def _strip_python_comments_and_docstrings(src: str) -> str:
    out = re.sub(r'"""[\s\S]*?"""', '', src)
    out = re.sub(r"'''[\s\S]*?'''", '', out)
    out = re.sub(r'#[^\n]*', '', out)
    return out


# [1] file richiesti
for rel in [BACKEND_ROUTE_REL, DESIGN_REL, SCHEMA_REL, GUARD_REL, PROOF_REL,
            DOC_REL, VALIDATOR_REL, SUITE_REL, LEGACY_FORGE_REL]:
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing required file: {rel}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT_RUNE_SCROLL_TALISMAN_COMMIT_SAFETY_HARDENING validator')
    sys.exit(1)

route_text = read_text(BACKEND_ROUTE_REL)
route_code = _strip_python_comments_and_docstrings(route_text)

# [2] namespace
if NAMESPACE not in route_text:
    fail(f'[2] route must contain namespace {NAMESPACE}')

# [3] feature flag
if FEATURE_FLAG not in route_text:
    fail(f'[3] route must reference {FEATURE_FLAG}')

# [4] default 503
if 'status_code=503' not in route_text:
    fail('[4] route must raise HTTP 503 when disabled')
if '"status": "disabled"' not in route_text and "'status': 'disabled'" not in route_text:
    fail('[4] route must include status:disabled envelope')

# [5] endpoints presenti
for ep in ENDPOINTS:
    g = f'@router.get("{ep}")'
    p = f'@router.post("{ep}")'
    if g not in route_text and p not in route_text:
        fail(f'[5] route missing endpoint decorator for {ep}')

# [6] required request fields
for fld in REQUIRED_REQUEST_FIELDS:
    if f'"{fld}"' not in route_text:
        fail(f'[6] route missing request field reference: {fld}')

# [7] guard checks referenziati
for gc in REQUIRED_GUARD_CHECKS:
    if f'"{gc}"' not in route_text:
        fail(f'[7] route missing guard check: {gc}')

# [8] safety flags chiave
for needle in [
    '"commit_enabled": False',
    '"live_mutation_enabled": False',
    '"hero_rune_slot_mutation_enabled": False',
    '"rune_inventory_mutation_enabled": False',
    '"materials_consumed": False',
    '"currency_consumed": False',
    '"premium_gems_currency_used": False',
    '"bp_delta_triggered": False',
    '"db_writes": 0',
    '"reward_grant_enabled": False',
    '"exp_grant_enabled": False',
    '"calls_battle_engine": False',
    '"calls_api_battle_simulate": False',
    '"calls_api_story_battle": False',
    '"calls_forge_legacy": False',
]:
    if needle not in route_text:
        fail(f'[8] route must contain safety token: {needle}')

# [9] no battle_engine import
for tok in ['from battle_engine', 'import battle_engine', 'battle_engine.']:
    if tok in route_code:
        fail(f'[9] route must not reference battle_engine token: {tok}')

# [10] no chiamate a forge legacy / battle
for tok in ['/api/battle/simulate', '/api/story/battle', 'from routes.forge',
            'import routes.forge', 'routes.forge.']:
    if tok in route_code:
        fail(f'[10] route must not call/import: {tok}')

# [11] no DB tokens
db_tokens = [
    'db.users', 'db.user_heroes', 'db.user_materials', 'db.user_gems',
    'db.user_gear', 'db.user_runes', 'db.server_profiles',
    '.update_one(', '.update_many(', '.insert_one(', '.insert_many(',
    '.delete_one(', '.delete_many(', 'find_one_and_update',
    'find_one_and_replace', 'pymongo', 'AsyncIOMotorClient',
    'motor.motor_asyncio',
]
for tok in db_tokens:
    if tok in route_text:
        fail(f'[11] route must not contain DB write token: {tok}')

# [12] no premium users.gems usage (executable code only)
for tok in [r'users\.gems', r'user\.gems', r'\$inc.*gems', r'users\["gems"\]', 'gems_balance']:
    if re.search(tok, route_code):
        fail(f'[12] route must not reference premium gems token: {tok}')

# [13] no BP delta trigger
for tok in ['bp_delta_grant', 'bp_delta_event', 'trigger_bp_delta',
            'battle_pass_delta', 'battlepass_delta']:
    if tok in route_text:
        fail(f'[13] route must not trigger BP delta: {tok}')

# [14] Rune/Gemme distinction esplicita
for needle in ['rune_is_not_gemme', 'rune_is_not_artifact', 'rune_is_not_divine_weapon']:
    if needle not in route_text:
        fail(f'[14] route must declare canonical distinction: {needle}')

# [15] design coerente
design = load_json(DESIGN_REL)
if design.get('feature_flag') != FEATURE_FLAG:
    fail(f'[15] design feature_flag must be {FEATURE_FLAG}')
if design.get('default_runtime_enabled') is not False:
    fail('[15] design default_runtime_enabled must be false')
if design.get('default_http_status') != 503:
    fail('[15] design default_http_status must be 503')
if design.get('operation_family') != 'rune_scroll_talisman_commit':
    fail('[15] design operation_family must be rune_scroll_talisman_commit')
cd = design.get('canonical_distinction', {}) or {}
for k in ('rune_is_not_gemme', 'rune_is_not_artifact', 'rune_is_not_divine_weapon'):
    if cd.get(k) is not True:
        fail(f'[15] design canonical_distinction.{k} must be true')
si = design.get('safety_invariants', {}) or {}
for k, exp in [
    ('commit_enabled', False), ('live_mutation_enabled', False),
    ('hero_rune_slot_mutation_enabled', False),
    ('rune_inventory_mutation_enabled', False),
    ('materials_consumed', False), ('currency_consumed', False),
    ('premium_gems_currency_used', False), ('bp_delta_triggered', False),
    ('db_writes', 0), ('reward_grant_enabled', False),
    ('exp_grant_enabled', False), ('calls_battle_engine', False),
    ('calls_forge_legacy', False),
]:
    if si.get(k) != exp:
        fail(f'[15] design safety_invariants.{k} must be {exp!r} (got {si.get(k)!r})')

# [16] schema coerente
schema = load_json(SCHEMA_REL)
missing = set(REQUIRED_REQUEST_FIELDS) - set(schema.get('required_fields') or [])
if missing:
    fail(f'[16] schema missing required fields: {sorted(missing)}')

# [17] guard policy coerente
guard = load_json(GUARD_REL)
gmissing = set(REQUIRED_GUARD_CHECKS) - set(guard.get('guard_checks') or [])
if gmissing:
    fail(f'[17] guard_policy missing guard checks: {sorted(gmissing)}')
if guard.get('preview_only') is not True:
    fail('[17] guard_policy.preview_only must be true')

# [18] proof marker
proof = load_json(PROOF_REL)
for k, exp in PROOF_REQUIRED.items():
    if proof.get(k) != exp:
        fail(f'[18] proof marker {k} must be {exp!r} (got {proof.get(k)!r})')
if proof.get('db_writes', 1) != 0:
    fail('[18] proof marker db_writes must be 0')
if proof.get('default_http_status') != 503:
    fail('[18] proof marker default_http_status must be 503')
if proof.get('feature_flag') != FEATURE_FLAG:
    fail(f'[18] proof marker feature_flag must be {FEATURE_FLAG}')
if proof.get('suite_runner_tuple_v38_track_b_count') != 1:
    fail('[18] proof marker suite_runner_tuple_v38_track_b_count must be 1')

# [19] server.py registra il router
sv = read_text('backend/server.py')
if 'from routes.rune_scroll_talisman_safety_preview import router' not in sv:
    fail('[19] server.py must import rune_scroll_talisman_safety_preview router')
if 'rune_scroll_talisman_safety_preview_router' not in sv:
    fail('[19] server.py must register rune_scroll_talisman_safety_preview_router')

# [20] suite runner tuple v38 Track B count = 1
sr = read_text(SUITE_REL)
token = "'PROJECT-RUNE-SCROLL-TALISMAN-COMMIT-SAFETY-HARDENING'"
cnt = sr.count(token)
if cnt != 1:
    fail(f'[20] suite runner must contain exactly 1 v38 Track B tuple token, got {cnt}')
val_name = 'validate_project_rune_scroll_talisman_commit_safety_hardening_v1.py'
if sr.count(f"'{val_name}'") != 1:
    fail(f'[20] suite runner must reference {val_name} exactly once')

# [21] no live commit endpoint esposto
banned_endpoints = ['/commit', '/execute', '/apply', '/live-commit', '/perform',
                    '/equip', '/unsocket', '/fuse', '/upgrade', '/replace']
for ep in banned_endpoints:
    g = f'@router.get("{ep}")'
    p = f'@router.post("{ep}")'
    if g in route_text or p in route_text:
        fail(f'[21] route must not expose live-commit endpoint: {ep}')

# [22] forge.py legacy NON modificato (presenza)
if not os.path.isfile(repo(LEGACY_FORGE_REL)):
    fail(f'[22] legacy {LEGACY_FORGE_REL} must still exist (unchanged)')

# [23] MD5 invariants
INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
}
for rel, exp in INVARIANTS.items():
    p = repo(rel)
    if not os.path.isfile(p):
        fail(f'[23] invariant file missing: {rel}')
        continue
    with open(p, 'rb') as f:
        got = hashlib.md5(f.read()).hexdigest()
    if got != exp:
        fail(f'[23] invariant MD5 mismatch on {rel}: expected {exp}, got {got}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT_RUNE_SCROLL_TALISMAN_COMMIT_SAFETY_HARDENING validator')
    sys.exit(1)

print('[PASS] PROJECT_RUNE_SCROLL_TALISMAN_COMMIT_SAFETY_HARDENING validator')
sys.exit(0)
