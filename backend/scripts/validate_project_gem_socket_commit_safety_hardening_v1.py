#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator: PROJECT_GEM_SOCKET_COMMIT_SAFETY_HARDENING_PACK (v37 Track A)
Phase: PHASE_7A_GEM_SOCKET_COMMIT_SAFETY_HARDENING
Mode:  ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_COMMIT

Asserisce gli invarianti di safety per il nuovo route preview-only di
Gem Socket commit. Nessun live commit. Nessuna mutazione gear/gem.
Nessun uso di premium users.gems. Nessuna scrittura DB.
"""
from __future__ import annotations
import json
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

BACKEND_ROUTE_REL = 'backend/routes/gem_socket_commit_safety_preview.py'
DESIGN_REL = 'data/design/economy_safety/gem_socket_commit_safety_preview_v1.json'
PROOF_REL = 'data/design/economy_safety/gem_socket_commit_safety_preview_proof_marker_v1.json'
DOC_REL = 'docs/divine/238_GEM_SOCKET_COMMIT_SAFETY_HARDENING.md'
VALIDATOR_REL = 'backend/scripts/validate_project_gem_socket_commit_safety_hardening_v1.py'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'
LEGACY_GEM_SOCKET_PREVIEW_REL = 'backend/routes/gem_socket_preview.py'

FEATURE_FLAG = 'GEM_SOCKET_COMMIT_SAFETY_PREVIEW_ENABLED'
NAMESPACE = '/api/gem-socket-commit-safety-preview'
ENDPOINTS = ['/config', '/validate-request', '/guard-plan-preview', '/idempotency-preview']

REQUIRED_REQUEST_FIELDS = [
    'request_id', 'user_id', 'gear_id', 'socket_index', 'gem_id',
    'expected_gear_version', 'expected_gem_version',
    'expected_gear_socket_state_version', 'expected_gem_inventory_version',
    'operation', 'operation_family', 'client_idempotency_key',
]

PROOF_REQUIRED = {
    'gem_socket_commit_safety_preview_route_created': True,
    'gem_socket_live_commit_enabled': False,
    'gear_mutation_enabled': False,
    'gem_inventory_mutation_enabled': False,
    'premium_users_gems_used': False,
    'reward_grant_enabled': False,
    'exp_grant_enabled': False,
    'economy_changed': False,
    'gacha_changed': False,
    'bp_vip_shop_changed': False,
    'material_raid_changed': False,
    'gem_socket_preview_route_changed': False,
    'battle_engine_changed': False,
    'combat_tsx_changed': False,
    'story_tsx_changed': False,
    'home_routes_changed': False,
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


# [1] file richiesti presenti
for rel in [BACKEND_ROUTE_REL, DESIGN_REL, PROOF_REL, DOC_REL, VALIDATOR_REL, SUITE_REL]:
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing required file: {rel}')

# [2] route legacy preview deve esistere e non essere stato eliminato
if not os.path.isfile(repo(LEGACY_GEM_SOCKET_PREVIEW_REL)):
    fail(f'[2] legacy {LEGACY_GEM_SOCKET_PREVIEW_REL} must still exist (unchanged)')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT_GEM_SOCKET_COMMIT_SAFETY_HARDENING validator')
    sys.exit(1)

route_text = read_text(BACKEND_ROUTE_REL)
route_code = _strip_python_comments_and_docstrings(route_text)

# [3] namespace
if NAMESPACE not in route_text:
    fail(f'[3] route must contain namespace {NAMESPACE}')

# [4] feature flag
if FEATURE_FLAG not in route_text:
    fail(f'[4] route must reference {FEATURE_FLAG}')

# [5] default 503 disabled
if 'status_code=503' not in route_text:
    fail('[5] route must raise HTTP 503 when disabled')
if '"status": "disabled"' not in route_text and "'status': 'disabled'" not in route_text:
    fail('[5] route must include status:disabled envelope')

# [6] endpoints presence
for ep in ENDPOINTS:
    g = f'@router.get("{ep}")'
    p = f'@router.post("{ep}")'
    if g not in route_text and p not in route_text:
        fail(f'[6] route missing endpoint decorator for {ep}')

# [7] required fields nella sample request / validate_request
for fld in REQUIRED_REQUEST_FIELDS:
    if f'"{fld}"' not in route_text:
        fail(f'[7] route must reference required request field: {fld}')

# [8] safety flags chiave assenti = false
for needle in [
    '"commit_enabled": False',
    '"gear_mutation_enabled": False',
    '"gem_inventory_mutation_enabled": False',
    '"premium_users_gems_used": False',
    '"db_writes": 0',
    '"reward_grant_enabled": False',
    '"exp_grant_enabled": False',
    '"calls_battle_engine": False',
    '"calls_api_battle_simulate": False',
    '"calls_api_story_battle": False',
]:
    if needle not in route_text:
        fail(f'[8] route must contain safety token: {needle}')

# [9] no battle_engine reference in eseguibile
for tok in ['from battle_engine', 'import battle_engine', 'battle_engine.']:
    if tok in route_code:
        fail(f'[9] route must not reference battle_engine token: {tok}')

# [10] no chiamate a /api/battle/simulate o /api/story/battle in eseguibile
for tok in ['/api/battle/simulate', '/api/story/battle']:
    if tok in route_code:
        fail(f'[10] route must not call {tok}')

# [11] no DB write tokens
db_tokens = [
    'db.users', 'db.user_heroes', 'db.user_materials', 'db.user_gems',
    'db.user_gear', 'db.server_profiles',
    '.update_one(', '.update_many(',
    '.insert_one(', '.insert_many(', '.delete_one(', '.delete_many(',
    'find_one_and_update', 'find_one_and_replace',
    'pymongo', 'AsyncIOMotorClient', 'motor.motor_asyncio',
]
for tok in db_tokens:
    if tok in route_text:
        fail(f'[11] route must not contain DB write token: {tok}')

# [12] design JSON coerente
design = load_json(DESIGN_REL)
if design.get('feature_flag') != FEATURE_FLAG:
    fail(f'[12] design feature_flag must be {FEATURE_FLAG}')
if design.get('default_runtime_enabled') is not False:
    fail('[12] design default_runtime_enabled must be false')
if design.get('default_http_status') != 503:
    fail('[12] design default_http_status must be 503')
if design.get('operation_family') != 'gem_socket_commit':
    fail('[12] design operation_family must be gem_socket_commit')
si = design.get('safety_invariants', {}) or {}
for k, exp in [
    ('commit_enabled', False),
    ('gear_mutation_enabled', False),
    ('gem_inventory_mutation_enabled', False),
    ('premium_users_gems_used', False),
    ('db_writes', 0),
    ('reward_grant_enabled', False),
    ('exp_grant_enabled', False),
    ('stamina_consumed', False),
    ('tickets_consumed', False),
    ('calls_battle_engine', False),
    ('calls_api_battle_simulate', False),
    ('calls_api_story_battle', False),
]:
    if si.get(k) != exp:
        fail(f'[12] design safety_invariants.{k} must be {exp!r} (got {si.get(k)!r})')

# [13] proof marker
proof = load_json(PROOF_REL)
for k, exp in PROOF_REQUIRED.items():
    if proof.get(k) != exp:
        fail(f'[13] proof marker {k} must be {exp!r} (got {proof.get(k)!r})')
if proof.get('db_writes', 1) != 0:
    fail('[13] proof marker db_writes must be 0')
if proof.get('default_http_status') != 503:
    fail('[13] proof marker default_http_status must be 503')
if proof.get('feature_flag') != FEATURE_FLAG:
    fail(f'[13] proof marker feature_flag must be {FEATURE_FLAG}')
if proof.get('suite_runner_tuple_v37_track_a_count') != 1:
    fail('[13] proof marker suite_runner_tuple_v37_track_a_count must be 1')

# [14] server.py registra il router
sv = read_text('backend/server.py')
if 'from routes.gem_socket_commit_safety_preview import router' not in sv:
    fail('[14] server.py must import gem_socket_commit_safety_preview router')
if 'gem_socket_commit_safety_preview_router' not in sv:
    fail('[14] server.py must register gem_socket_commit_safety_preview_router')

# [15] suite runner tuple v37 Track A count = 1
sr = read_text(SUITE_REL)
token = "'PROJECT-GEM-SOCKET-COMMIT-SAFETY-HARDENING'"
cnt = sr.count(token)
if cnt != 1:
    fail(f'[15] suite runner must contain exactly 1 v37 Track A tuple token, got {cnt}')
val_name = 'validate_project_gem_socket_commit_safety_hardening_v1.py'
if sr.count(f"'{val_name}'") != 1:
    fail(f'[15] suite runner must reference {val_name} exactly once')

# [16] no live commit decorator in route (no endpoint chiamato "commit" o "execute" o "apply")
banned_endpoints = ['/commit', '/execute', '/apply', '/live-commit', '/perform']
for ep in banned_endpoints:
    g = f'@router.get("{ep}")'
    p = f'@router.post("{ep}")'
    if g in route_text or p in route_text:
        fail(f'[16] route must not expose live-commit endpoint: {ep}')

# [17] MD5 invariants (5 file core)
import hashlib
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
        fail(f'[17] invariant file missing: {rel}')
        continue
    with open(p, 'rb') as f:
        got = hashlib.md5(f.read()).hexdigest()
    if got != exp:
        fail(f'[17] invariant MD5 mismatch on {rel}: expected {exp}, got {got}')

# Final
if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT_GEM_SOCKET_COMMIT_SAFETY_HARDENING validator')
    sys.exit(1)

print('[PASS] PROJECT_GEM_SOCKET_COMMIT_SAFETY_HARDENING validator')
sys.exit(0)
