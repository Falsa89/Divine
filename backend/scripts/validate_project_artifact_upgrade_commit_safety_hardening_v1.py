#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator: PROJECT_ARTIFACT_UPGRADE_COMMIT_SAFETY_HARDENING_PACK (v39 Track A)
Phase: PHASE_9A_ARTIFACT_UPGRADE_COMMIT_SAFETY_HARDENING
Mode:  ENDGAME_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_COMMIT

Asserisce gli invarianti del nuovo route preview-only Artifact upgrade.
Distinzione canonica Artifact ≠ Gear/Gemme/Rune/Divine Weapon esplicita.
Nessuna mutazione artifacts. Nessuna attivazione bonus globali. Nessun
consumo materiali/oro/gemme. Nessun premium users.gems. Nessun BP Delta.
Zero DB. backend/routes/artifacts.py MD5 intoccato.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

BACKEND_ROUTE_REL = 'backend/routes/artifact_upgrade_safety_preview.py'
DESIGN_REL = 'data/design/artifacts/artifact_upgrade_commit_safety_hardening_v1.json'
SCHEMA_REL = 'data/design/artifacts/artifact_upgrade_commit_request_schema_v1.json'
GUARD_REL = 'data/design/artifacts/artifact_upgrade_guard_policy_v1.json'
PROOF_REL = 'data/design/artifacts/artifact_upgrade_safety_proof_marker_v1.json'
DOC_REL = 'docs/divine/247_ARTIFACT_UPGRADE_COMMIT_SAFETY_HARDENING.md'
VALIDATOR_REL = 'backend/scripts/validate_project_artifact_upgrade_commit_safety_hardening_v1.py'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'
LEGACY_ARTIFACTS_REL = 'backend/routes/artifacts.py'
LEGACY_ARTIFACTS_MD5 = '893f244d85fd45cbe825996463995293'

FEATURE_FLAG = 'ARTIFACT_UPGRADE_SAFETY_PREVIEW_ENABLED'
NAMESPACE = '/api/artifact-upgrade-safety-preview'
ENDPOINTS = ['/config', '/validate-request', '/guard-plan-preview', '/idempotency-preview']

REQUIRED_REQUEST_FIELDS = [
    'request_id', 'idempotency_key', 'operation_type', 'user_id', 'server_id',
    'artifact_instance_id', 'fodder_artifact_instance_ids',
    'target_level', 'target_rank',
    'expected_artifact_version', 'expected_inventory_version',
    'expected_materials_version', 'client_trace_id', 'created_at',
]

REQUIRED_GUARD_CHECKS = [
    'auth_required', 'user_owns_artifact', 'user_owns_all_fodder_artifacts',
    'artifact_not_locked', 'artifact_not_favorite',
    'artifact_not_in_restricted_state',
    'fodder_artifacts_not_locked', 'fodder_artifacts_not_favorite',
    'no_duplicate_fodder_ids', 'base_artifact_not_in_fodder',
    'target_level_within_cap', 'target_rank_within_cap',
    'upgrade_recipe_valid', 'duplicate_fusion_recipe_valid',
    'artifact_bible_required_before_live',
    'anti_power_creep_validator_required_before_live',
    'global_bonus_activation_disabled',
    'material_cost_policy_defined_but_not_charged',
    'currency_cost_policy_defined_but_not_charged',
    'same_request_id_not_committed', 'idempotency_key_required',
    'expected_versions_match', 'premium_users_gems_not_used',
    'atomic_commit_required_future', 'rollback_policy_required_future',
    'audit_log_required_future', 'bp_delta_not_triggered_in_preview',
]

PROOF_REQUIRED = {
    'artifact_upgrade_safety_preview_route_created': True,
    'artifact_live_upgrade_enabled': False,
    'artifact_live_fusion_enabled': False,
    'artifact_live_pull_enabled': False,
    'artifact_bonus_activation_enabled': False,
    'artifact_mutation_enabled': False,
    'materials_consumed': False,
    'currency_consumed': False,
    'premium_gems_currency_used': False,
    'bp_delta_triggered': False,
    'reward_grant_enabled': False,
    'exp_grant_enabled': False,
    'artifacts_legacy_route_changed': False,
    'artifact_is_not_equip': True,
    'artifact_is_not_gear': True,
    'artifact_is_not_gemme': True,
    'artifact_is_not_rune': True,
    'artifact_is_not_divine_weapon': True,
    'economy_changed': False,
    'gacha_changed': False,
    'bp_vip_shop_changed': False,
    'battle_engine_changed': False,
    'combat_tsx_changed': False,
    'story_tsx_changed': False,
    'home_routes_changed': False,
    'divine_weapon_runtime_changed': False,
    'guild_war_runtime_changed': False,
    'character_bible_changed': False,
    'hero_final_numbers_changed': False,
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


# [1] required files
for rel in [BACKEND_ROUTE_REL, DESIGN_REL, SCHEMA_REL, GUARD_REL, PROOF_REL,
            DOC_REL, VALIDATOR_REL, SUITE_REL, LEGACY_ARTIFACTS_REL]:
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing required file: {rel}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT_ARTIFACT_UPGRADE_COMMIT_SAFETY_HARDENING validator')
    sys.exit(1)

route_text = read_text(BACKEND_ROUTE_REL)
route_code = _strip_python_comments_and_docstrings(route_text)

# [2] namespace / flag / 503
if NAMESPACE not in route_text:
    fail(f'[2] route must contain namespace {NAMESPACE}')
if FEATURE_FLAG not in route_text:
    fail(f'[2] route must reference {FEATURE_FLAG}')
if 'status_code=503' not in route_text:
    fail('[2] route must raise HTTP 503 when disabled')
if '"status": "disabled"' not in route_text and "'status': 'disabled'" not in route_text:
    fail('[2] route must include status:disabled envelope')

# [3] endpoints
for ep in ENDPOINTS:
    g = f'@router.get("{ep}")'
    p = f'@router.post("{ep}")'
    if g not in route_text and p not in route_text:
        fail(f'[3] route missing endpoint decorator for {ep}')

# [4] required request fields
for fld in REQUIRED_REQUEST_FIELDS:
    if f'"{fld}"' not in route_text:
        fail(f'[4] route missing request field reference: {fld}')

# [5] guard checks referenziati
for gc in REQUIRED_GUARD_CHECKS:
    if f'"{gc}"' not in route_text:
        fail(f'[5] route missing guard check: {gc}')

# [6] safety flags
for needle in [
    '"commit_enabled": False',
    '"live_mutation_enabled": False',
    '"artifact_mutation_enabled": False',
    '"artifact_bonus_activation_enabled": False',
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
    '"calls_artifacts_legacy": False',
]:
    if needle not in route_text:
        fail(f'[6] route must contain safety token: {needle}')

# [7] no battle_engine import
for tok in ['from battle_engine', 'import battle_engine', 'battle_engine.']:
    if tok in route_code:
        fail(f'[7] route must not reference battle_engine token: {tok}')

# [8] no chiamate a artifacts legacy / battle
for tok in ['/api/battle/simulate', '/api/story/battle', 'from routes.artifacts',
            'import routes.artifacts', 'routes.artifacts.']:
    if tok in route_code:
        fail(f'[8] route must not call/import: {tok}')

# [9] no DB tokens
db_tokens = [
    'db.users', 'db.user_heroes', 'db.user_materials', 'db.user_gems',
    'db.user_gear', 'db.user_runes', 'db.user_artifacts', 'db.server_profiles',
    '.update_one(', '.update_many(', '.insert_one(', '.insert_many(',
    '.delete_one(', '.delete_many(', 'find_one_and_update',
    'find_one_and_replace', 'pymongo', 'AsyncIOMotorClient',
    'motor.motor_asyncio',
]
for tok in db_tokens:
    if tok in route_text:
        fail(f'[9] route must not contain DB write token: {tok}')

# [10] no premium users.gems usage in executable code
for tok in [r'users\.gems', r'user\.gems', r'\$inc.*gems', r'users\["gems"\]', 'gems_balance']:
    if re.search(tok, route_code):
        fail(f'[10] route must not reference premium gems token: {tok}')

# [11] no BP delta trigger
for tok in ['bp_delta_grant', 'bp_delta_event', 'trigger_bp_delta',
            'battle_pass_delta', 'battlepass_delta']:
    if tok in route_text:
        fail(f'[11] route must not trigger BP delta: {tok}')

# [12] Artifact canonical distinction
for needle in ['artifact_is_not_equip', 'artifact_is_not_gear',
               'artifact_is_not_gemme', 'artifact_is_not_rune',
               'artifact_is_not_divine_weapon']:
    if needle not in route_text:
        fail(f'[12] route must declare canonical distinction: {needle}')

# [13] design coerente
design = load_json(DESIGN_REL)
if design.get('feature_flag') != FEATURE_FLAG:
    fail(f'[13] design feature_flag must be {FEATURE_FLAG}')
if design.get('default_runtime_enabled') is not False:
    fail('[13] design default_runtime_enabled must be false')
if design.get('default_http_status') != 503:
    fail('[13] design default_http_status must be 503')
if design.get('operation_family') != 'artifact_upgrade_commit':
    fail('[13] design operation_family must be artifact_upgrade_commit')
si = design.get('safety_invariants', {}) or {}
for k, exp in [
    ('commit_enabled', False), ('live_mutation_enabled', False),
    ('artifact_mutation_enabled', False),
    ('artifact_bonus_activation_enabled', False),
    ('materials_consumed', False), ('currency_consumed', False),
    ('premium_gems_currency_used', False), ('bp_delta_triggered', False),
    ('db_writes', 0), ('reward_grant_enabled', False),
    ('exp_grant_enabled', False), ('calls_battle_engine', False),
    ('calls_artifacts_legacy', False),
]:
    if si.get(k) != exp:
        fail(f'[13] design safety_invariants.{k} must be {exp!r} (got {si.get(k)!r})')

# [14] schema/guard
schema = load_json(SCHEMA_REL)
missing = set(REQUIRED_REQUEST_FIELDS) - set(schema.get('required_fields') or [])
if missing:
    fail(f'[14] schema missing required fields: {sorted(missing)}')
guard = load_json(GUARD_REL)
gmissing = set(REQUIRED_GUARD_CHECKS) - set(guard.get('guard_checks') or [])
if gmissing:
    fail(f'[14] guard_policy missing guard checks: {sorted(gmissing)}')
if guard.get('preview_only') is not True:
    fail('[14] guard_policy.preview_only must be true')

# [15] proof marker
proof = load_json(PROOF_REL)
for k, exp in PROOF_REQUIRED.items():
    if proof.get(k) != exp:
        fail(f'[15] proof marker {k} must be {exp!r} (got {proof.get(k)!r})')
if proof.get('db_writes', 1) != 0:
    fail('[15] proof marker db_writes must be 0')
if proof.get('default_http_status') != 503:
    fail('[15] proof marker default_http_status must be 503')
if proof.get('feature_flag') != FEATURE_FLAG:
    fail(f'[15] proof marker feature_flag must be {FEATURE_FLAG}')
if proof.get('suite_runner_tuple_v39_track_a_count') != 1:
    fail('[15] proof marker suite_runner_tuple_v39_track_a_count must be 1')

# [16] server.py registra il router
sv = read_text('backend/server.py')
if 'from routes.artifact_upgrade_safety_preview import router' not in sv:
    fail('[16] server.py must import artifact_upgrade_safety_preview router')
if 'artifact_upgrade_safety_preview_router' not in sv:
    fail('[16] server.py must register artifact_upgrade_safety_preview_router')

# [17] suite runner tuple v39 Track A count = 1
sr = read_text(SUITE_REL)
token = "'PROJECT-ARTIFACT-UPGRADE-COMMIT-SAFETY-HARDENING'"
cnt = sr.count(token)
if cnt != 1:
    fail(f'[17] suite runner must contain exactly 1 v39 Track A tuple token, got {cnt}')
val_name = 'validate_project_artifact_upgrade_commit_safety_hardening_v1.py'
if sr.count(f"'{val_name}'") != 1:
    fail(f'[17] suite runner must reference {val_name} exactly once')

# [18] no live commit endpoint
banned_endpoints = ['/commit', '/execute', '/apply', '/live-commit',
                    '/perform', '/upgrade', '/fuse', '/limit-break']
for ep in banned_endpoints:
    g = f'@router.get("{ep}")'
    p = f'@router.post("{ep}")'
    if g in route_text or p in route_text:
        fail(f'[18] route must not expose live-commit endpoint: {ep}')

# [19] artifacts.py legacy NON modificato (presence + MD5 strict)
if not os.path.isfile(repo(LEGACY_ARTIFACTS_REL)):
    fail(f'[19] legacy {LEGACY_ARTIFACTS_REL} must still exist (unchanged)')
else:
    with open(repo(LEGACY_ARTIFACTS_REL), 'rb') as f:
        got = hashlib.md5(f.read()).hexdigest()
    if got != LEGACY_ARTIFACTS_MD5:
        fail(f'[19] {LEGACY_ARTIFACTS_REL} MD5 must remain {LEGACY_ARTIFACTS_MD5} (got {got})')

# [20] MD5 invariants 5 core
INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': LEGACY_ARTIFACTS_MD5,
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
}
for rel, exp in INVARIANTS.items():
    p = repo(rel)
    if not os.path.isfile(p):
        fail(f'[20] invariant file missing: {rel}')
        continue
    with open(p, 'rb') as f:
        got = hashlib.md5(f.read()).hexdigest()
    if got != exp:
        fail(f'[20] invariant MD5 mismatch on {rel}: expected {exp}, got {got}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT_ARTIFACT_UPGRADE_COMMIT_SAFETY_HARDENING validator')
    sys.exit(1)

print('[PASS] PROJECT_ARTIFACT_UPGRADE_COMMIT_SAFETY_HARDENING validator')
sys.exit(0)
