#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator: PROJECT_MAIL_REWARD_CLAIM_SAFETY_HARDENING_PACK (v40 Track B)
Phase: PHASE_10B_MAIL_REWARD_CLAIM_SAFETY_HARDENING
Mode:  REWARD_CLAIM_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_CLAIM

Asserisce gli invarianti del nuovo route preview-only Mail claim.
Nessun reward grant live. Nessuna mutazione mail state (no delete, no
read/unread, no claim state). Nessuna mutazione inventory/currency. Nessun
premium users.gems. Nessun BP Delta. Zero DB.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

BACKEND_ROUTE_REL = 'backend/routes/mail_claim_safety_preview.py'
PROOF_REL = 'data/design/economy_safety/mail_claim_safety_proof_marker_v1.json'
DOC_REL = 'docs/divine/252_MAIL_REWARD_CLAIM_SAFETY_HARDENING.md'
VALIDATOR_REL = 'backend/scripts/validate_project_mail_claim_safety_hardening_v1.py'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'

FEATURE_FLAG = 'MAIL_CLAIM_SAFETY_PREVIEW_ENABLED'
NAMESPACE = '/api/mail-claim-safety-preview'
ENDPOINTS = ['/config', '/validate-request', '/guard-plan-preview', '/idempotency-preview']

REQUIRED_REQUEST_FIELDS = [
    'request_id', 'idempotency_key', 'operation_type', 'user_id', 'server_id',
    'mail_message_id', 'mail_reward_slot_ids',
    'expected_mail_version', 'expected_inventory_version',
    'expected_user_wallet_version', 'client_trace_id', 'created_at',
]

REQUIRED_GUARD_CHECKS = [
    'auth_required', 'server_id_required', 'user_server_binding_valid',
    'mail_message_exists', 'mail_belongs_to_user',
    'mail_belongs_to_server_or_account_scope_valid',
    'mail_not_deleted', 'mail_not_expired', 'mail_not_already_claimed',
    'reward_slots_exist', 'reward_payload_schema_valid',
    'bulk_claim_cap_valid', 'sender_system_trust_policy_valid',
    'compensation_policy_requires_admin_marker_future',
    'no_premium_currency_consumption',
    'same_request_id_not_committed', 'idempotency_key_required',
    'conflicting_same_idempotency_key_rejected_future',
    'expected_versions_match',
    'atomic_commit_required_future', 'ledger_entry_required_future',
    'rollback_policy_required_future', 'audit_log_required_future',
    'bp_delta_not_triggered_in_preview',
]

PROOF_REQUIRED = {
    'mail_claim_safety_preview_route_created': True,
    'mail_live_claim_enabled': False,
    'reward_grant_enabled': False,
    'inventory_mutation_enabled': False,
    'currency_mutation_enabled': False,
    'premium_currency_used': False,
    'mail_state_mutation_enabled': False,
    'mail_delete_enabled': False,
    'mail_read_state_mutation_enabled': False,
    'bp_delta_triggered': False,
    'exp_grant_enabled': False,
    'frontend_battlepass_tsx_changed': False,
    'frontend_vip_tsx_changed': False,
    'battle_engine_changed': False,
    'combat_tsx_changed': False,
    'story_tsx_changed': False,
    'home_routes_changed': False,
    'artifacts_legacy_route_changed': False,
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
for rel in [BACKEND_ROUTE_REL, PROOF_REL, DOC_REL, VALIDATOR_REL, SUITE_REL]:
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing required file: {rel}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT_MAIL_CLAIM_SAFETY_HARDENING validator')
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

# [5] guard checks
for gc in REQUIRED_GUARD_CHECKS:
    if f'"{gc}"' not in route_text:
        fail(f'[5] route missing guard check: {gc}')

# [6] safety flags
for needle in [
    '"claim_enabled": False',
    '"live_mutation_enabled": False',
    '"reward_grant_enabled": False',
    '"inventory_mutation_enabled": False',
    '"currency_mutation_enabled": False',
    '"premium_currency_used": False',
    '"mail_state_mutation_enabled": False',
    '"mail_delete_enabled": False',
    '"mail_read_state_mutation_enabled": False',
    '"bp_delta_triggered": False',
    '"db_writes": 0',
    '"calls_battle_engine": False',
    '"calls_api_battle_simulate": False',
    '"calls_api_story_battle": False',
]:
    if needle not in route_text:
        fail(f'[6] route must contain safety token: {needle}')

# [7] no battle_engine import / battle calls in eseguibile
for tok in ['from battle_engine', 'import battle_engine', 'battle_engine.',
            '/api/battle/simulate', '/api/story/battle']:
    if tok in route_code:
        fail(f'[7] route must not reference token: {tok}')

# [8] no DB tokens
db_tokens = [
    'db.users', 'db.user_heroes', 'db.user_materials', 'db.user_gems',
    'db.user_gear', 'db.user_mail', 'db.mail_messages', 'db.server_profiles',
    '.update_one(', '.update_many(', '.insert_one(', '.insert_many(',
    '.delete_one(', '.delete_many(', 'find_one_and_update',
    'find_one_and_replace', 'pymongo', 'AsyncIOMotorClient',
    'motor.motor_asyncio',
]
for tok in db_tokens:
    if tok in route_text:
        fail(f'[8] route must not contain DB write token: {tok}')

# [9] no premium users.gems usage (executable)
for tok in [r'users\.gems', r'user\.gems', r'\$inc.*gems', r'users\["gems"\]', 'gems_balance']:
    if re.search(tok, route_code):
        fail(f'[9] route must not reference premium gems token: {tok}')

# [10] no BP delta trigger
for tok in ['bp_delta_grant', 'bp_delta_event', 'trigger_bp_delta',
            'battle_pass_delta', 'battlepass_delta']:
    if tok in route_text:
        fail(f'[10] route must not trigger BP delta: {tok}')

# [11] proof marker
proof = load_json(PROOF_REL)
for k, exp in PROOF_REQUIRED.items():
    if proof.get(k) != exp:
        fail(f'[11] proof marker {k} must be {exp!r} (got {proof.get(k)!r})')
if proof.get('db_writes', 1) != 0:
    fail('[11] proof marker db_writes must be 0')
if proof.get('default_http_status') != 503:
    fail('[11] proof marker default_http_status must be 503')
if proof.get('feature_flag') != FEATURE_FLAG:
    fail(f'[11] proof marker feature_flag must be {FEATURE_FLAG}')
if proof.get('suite_runner_tuple_v40_track_b_count') != 1:
    fail('[11] proof marker suite_runner_tuple_v40_track_b_count must be 1')

# [12] server.py registra il router
sv = read_text('backend/server.py')
if 'from routes.mail_claim_safety_preview import router' not in sv:
    fail('[12] server.py must import mail_claim_safety_preview router')
if 'mail_claim_safety_preview_router' not in sv:
    fail('[12] server.py must register mail_claim_safety_preview_router')
if sv.count('app.include_router(mail_claim_safety_preview_router)') != 1:
    fail('[12] server.py include_router(mail_claim_safety_preview_router) count must be 1')

# [13] suite runner tuple v40 Track B count = 1
sr = read_text(SUITE_REL)
token = "'PROJECT-MAIL-CLAIM-SAFETY-HARDENING'"
if sr.count(token) != 1:
    fail(f'[13] suite runner must contain exactly 1 v40 Track B tuple token, got {sr.count(token)}')
val_name = 'validate_project_mail_claim_safety_hardening_v1.py'
if sr.count(f"'{val_name}'") != 1:
    fail(f'[13] suite runner must reference {val_name} exactly once')

# [14] no live claim endpoint exposed
banned_endpoints = ['/commit', '/execute', '/apply', '/live-claim',
                    '/perform', '/claim', '/grant', '/delete', '/mark-read']
for ep in banned_endpoints:
    g = f'@router.get("{ep}")'
    p = f'@router.post("{ep}")'
    if g in route_text or p in route_text:
        fail(f'[14] route must not expose live-claim endpoint: {ep}')

# [15] MD5 invariants core 5
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
        fail(f'[15] invariant file missing: {rel}')
        continue
    with open(p, 'rb') as f:
        got = hashlib.md5(f.read()).hexdigest()
    if got != exp:
        fail(f'[15] invariant MD5 mismatch on {rel}: expected {exp}, got {got}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT_MAIL_CLAIM_SAFETY_HARDENING validator')
    sys.exit(1)

print('[PASS] PROJECT_MAIL_CLAIM_SAFETY_HARDENING validator')
sys.exit(0)
