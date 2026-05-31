#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator: PROJECT_ECONOMY_IDEMPOTENCY_AND_ATOMIC_COMMIT_CONTRACT_PACK (v37 Track C)
Phase: PHASE_7C_ECONOMY_IDEMPOTENCY_AND_ATOMIC_COMMIT_CONTRACT
Mode:  DESIGN_CONTRACT_AUDIT_ONLY

Asserisce che il contract di idempotency / atomic commit / rollback / audit log
sia presente, coerente e che NON attivi alcun runtime live. Nessuna scrittura DB.
"""
from __future__ import annotations
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

DESIGN_REL = 'data/design/economy_safety/economy_idempotency_and_atomic_commit_contract_v1.json'
PROOF_REL = 'data/design/economy_safety/economy_idempotency_and_atomic_commit_contract_proof_marker_v1.json'
DOC_REL = 'docs/divine/240_ECONOMY_IDEMPOTENCY_AND_ATOMIC_COMMIT_CONTRACT.md'
VALIDATOR_REL = 'backend/scripts/validate_project_economy_idempotency_and_atomic_commit_contract_v1.py'
SUITE_REL = 'backend/scripts/run_hero_skill_kit_validator_suite.py'

TRACK_A_ROUTE = 'backend/routes/gem_socket_commit_safety_preview.py'
TRACK_B_ROUTE = 'backend/routes/material_raid_claim_safety_preview.py'

REQUIRED_REQUEST_FIELDS = [
    'request_id', 'user_id', 'operation', 'operation_family',
    'client_idempotency_key', 'expected_state_version_set', 'created_at',
]

REQUIRED_OPERATION_FAMILIES = {
    'gem_socket_commit', 'material_raid_claim',
}

PROOF_REQUIRED = {
    'economy_idempotency_contract_defined': True,
    'atomic_commit_contract_defined': True,
    'rollback_contract_defined': True,
    'audit_log_contract_defined': True,
    'runtime_activation': False,
    'reward_grant_enabled': False,
    'exp_grant_enabled': False,
    'economy_changed': False,
    'gacha_changed': False,
    'bp_vip_shop_changed': False,
    'material_raid_changed': False,
    'gem_socket_changed': False,
    'rune_runtime_changed': False,
    'artifact_runtime_changed': False,
    'divine_weapon_runtime_changed': False,
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


# [1] file richiesti presenti
for rel in [DESIGN_REL, PROOF_REL, DOC_REL, VALIDATOR_REL, SUITE_REL,
            TRACK_A_ROUTE, TRACK_B_ROUTE]:
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing required file: {rel}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT_ECONOMY_IDEMPOTENCY_AND_ATOMIC_COMMIT_CONTRACT validator')
    sys.exit(1)

# [2] design coerente
design = load_json(DESIGN_REL)
if design.get('runtime_activation') is not False:
    fail('[2] design runtime_activation must be false')
if design.get('db_writes') != 0:
    fail('[2] design db_writes must be 0')
if design.get('mode') != 'DESIGN_CONTRACT_AUDIT_ONLY':
    fail('[2] design mode must be DESIGN_CONTRACT_AUDIT_ONLY')

# [3] required request fields
req_fields = set(design.get('required_fields_for_safe_operation_request') or [])
missing = set(REQUIRED_REQUEST_FIELDS) - req_fields
if missing:
    fail(f'[3] design required_fields_for_safe_operation_request missing: {sorted(missing)}')

# [4] idempotency contract
idem = design.get('idempotency_contract', {}) or {}
for k, exp in [
    ('client_idempotency_key_required', True),
    ('retry_same_key_same_payload_returns_same_result', True),
    ('retry_same_key_conflicting_payload_rejected', True),
    ('server_idempotency_persistence_future', True),
    ('client_local_persistence_of_idempotency_keys', False),
]:
    if idem.get(k) != exp:
        fail(f'[4] idempotency_contract.{k} must be {exp!r} (got {idem.get(k)!r})')
ttl = idem.get('server_idempotency_ttl_seconds', 0)
if not isinstance(ttl, int) or ttl <= 0:
    fail('[4] idempotency_contract.server_idempotency_ttl_seconds must be positive int')

# [5] atomic commit contract
ac = design.get('atomic_commit_contract', {}) or {}
for k, exp in [
    ('single_transactional_unit_required', True),
    ('partial_commit_forbidden', True),
    ('reads_must_use_expected_versions', True),
    ('writes_must_check_version_match', True),
    ('on_version_mismatch', 'abort_and_rollback'),
    ('on_any_step_failure', 'abort_and_rollback'),
]:
    if ac.get(k) != exp:
        fail(f'[5] atomic_commit_contract.{k} must be {exp!r} (got {ac.get(k)!r})')

# [6] rollback contract
rb = design.get('rollback_contract', {}) or {}
for k, exp in [
    ('rollback_strategy_required', True),
    ('rollback_must_restore_prior_state', True),
    ('rollback_must_not_leave_partial_state', True),
    ('rollback_audit_log_required', True),
]:
    if rb.get(k) != exp:
        fail(f'[6] rollback_contract.{k} must be {exp!r} (got {rb.get(k)!r})')

# [7] audit log contract
al = design.get('audit_log_contract', {}) or {}
if al.get('audit_log_required') is not True:
    fail('[7] audit_log_contract.audit_log_required must be true')
if al.get('audit_must_not_contain_pii') is not True:
    fail('[7] audit_log_contract.audit_must_not_contain_pii must be true')
fields = set(al.get('audit_fields') or [])
must_have_audit = {'request_id', 'server_idempotency_key', 'operation',
                   'operation_family', 'user_id', 'outcome', 'rolled_back'}
miss = must_have_audit - fields
if miss:
    fail(f'[7] audit_log_contract.audit_fields missing: {sorted(miss)}')

# [8] operation families include almeno Track A + Track B
fams = set(design.get('operation_families') or [])
miss = REQUIRED_OPERATION_FAMILIES - fams
if miss:
    fail(f'[8] design operation_families missing: {sorted(miss)}')

# [9] forbidden list copre i preview tokens chiave
forbidden = set(design.get('forbidden') or [])
must_forbid = {
    'premium_users_gems_use_in_preview',
    'db_write_in_preview',
    'gear_mutation_in_preview',
    'gem_inventory_mutation_in_preview',
    'user_materials_mutation_in_preview',
    'reward_grant_in_preview',
    'exp_grant_in_preview',
    'stamina_consumption_in_preview',
    'tickets_consumption_in_preview',
    'paid_attempt_consumption_in_preview',
}
miss = must_forbid - forbidden
if miss:
    fail(f'[9] design forbidden missing tokens: {sorted(miss)}')

# [10] proof marker
proof = load_json(PROOF_REL)
for k, exp in PROOF_REQUIRED.items():
    if proof.get(k) != exp:
        fail(f'[10] proof marker {k} must be {exp!r} (got {proof.get(k)!r})')
if proof.get('db_writes', 1) != 0:
    fail('[10] proof marker db_writes must be 0')
if proof.get('suite_runner_tuple_v37_track_c_count') != 1:
    fail('[10] proof marker suite_runner_tuple_v37_track_c_count must be 1')

# [11] suite runner tuple v37 Track C count = 1
sr = read_text(SUITE_REL)
token = "'PROJECT-ECONOMY-IDEMPOTENCY-AND-ATOMIC-COMMIT-CONTRACT'"
cnt = sr.count(token)
if cnt != 1:
    fail(f'[11] suite runner must contain exactly 1 v37 Track C tuple token, got {cnt}')
val_name = 'validate_project_economy_idempotency_and_atomic_commit_contract_v1.py'
if sr.count(f"'{val_name}'") != 1:
    fail(f'[11] suite runner must reference {val_name} exactly once')

# [12] MD5 invariants
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
        fail(f'[12] invariant file missing: {rel}')
        continue
    with open(p, 'rb') as f:
        got = hashlib.md5(f.read()).hexdigest()
    if got != exp:
        fail(f'[12] invariant MD5 mismatch on {rel}: expected {exp}, got {got}')

# Final
if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT_ECONOMY_IDEMPOTENCY_AND_ATOMIC_COMMIT_CONTRACT validator')
    sys.exit(1)

print('[PASS] PROJECT_ECONOMY_IDEMPOTENCY_AND_ATOMIC_COMMIT_CONTRACT validator')
sys.exit(0)
