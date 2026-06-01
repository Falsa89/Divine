#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator Track A: PROJECT-SHARED-REQUEST-HASH-IDEMPOTENCY-CONTRACT
Pack: MEGA_ECONOMY_SAFETY_ACCELERATION_5_OBSERVABILITY_SIGNOFF_AND_REQUEST_HASH_PACK_v41

Asserisce che il contratto condiviso di request hash + idempotency sia
presente, coerente, copra tutte le 8 famiglie operation gia coperte dai
preview safety layer v37-v40, non introduca PII nell'hashing/idempotency,
non attivi alcun runtime, e non produca DB writes.
"""
from __future__ import annotations
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

CONTRACT_REL = 'data/design/economy_safety/shared_request_hash_idempotency_contract_v1.json'
MARKER_REL = 'data/design/economy_safety/shared_request_hash_idempotency_contract_proof_marker_v1.json'
DOC_REL = 'docs/divine/254_MEGA_ECONOMY_SAFETY_ACCELERATION_5_OBSERVABILITY_SIGNOFF_AND_REQUEST_HASH_PACK_v41_TRACK_A.md'
EXTENDS_REL = 'data/design/economy_safety/economy_idempotency_and_atomic_commit_contract_v1.json'

REQUIRED_FAMILIES = {
    'gem_socket_commit', 'material_raid_claim',
    'gear_forge_fusion_commit', 'rune_scroll_talisman_commit',
    'artifact_upgrade_commit', 'divine_weapon_upgrade_commit',
    'battle_pass_reward_claim', 'mail_reward_claim',
}

PII_FIELDS_REQUIRED = {'email', 'ip', 'device_id', 'push_token', 'phone'}

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def repo(p: str) -> str:
    return os.path.join(REPO_ROOT, p)


def load_json(rel: str):
    return json.load(open(repo(rel), 'r', encoding='utf-8'))


# [1] esistenza file
for rel in (CONTRACT_REL, MARKER_REL, DOC_REL, EXTENDS_REL):
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing required file: {rel}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT-SHARED-REQUEST-HASH-IDEMPOTENCY-CONTRACT validator')
    sys.exit(1)

contract = load_json(CONTRACT_REL)
marker = load_json(MARKER_REL)

# [2] runtime flags must be safe
for key, exp in [
    ('runtime_activation', False),
    ('db_writes', 0),
    ('live_commit_allowed', False),
    ('live_claim_allowed', False),
    ('reward_grant_enabled', False),
    ('bp_delta_runtime_enabled', False),
]:
    if contract.get(key) != exp:
        fail(f'[2] contract.{key} must be {exp!r} (got {contract.get(key)!r})')
    if marker.get(key) != exp:
        fail(f'[2] marker.{key} must be {exp!r} (got {marker.get(key)!r})')

# [3] mode
if contract.get('mode') != 'DESIGN_CONTRACT_AUDIT_ONLY':
    fail('[3] contract.mode must be DESIGN_CONTRACT_AUDIT_ONLY')

# [4] extends linkage
if contract.get('extends') != 'economy_idempotency_and_atomic_commit_contract_v1':
    fail('[4] contract.extends must reference economy_idempotency_and_atomic_commit_contract_v1')

# [5] shared_request_hash_contract block
shrc = contract.get('shared_request_hash_contract') or {}
if shrc.get('algorithm') != 'sha256':
    fail('[5] shared_request_hash_contract.algorithm must be sha256')
if shrc.get('truncation_chars') != 32:
    fail('[5] shared_request_hash_contract.truncation_chars must be 32')
if shrc.get('output_lowercase_hex') is not True:
    fail('[5] shared_request_hash_contract.output_lowercase_hex must be true')
canon = shrc.get('canonicalization') or {}
if canon.get('json_keys_sorted_ascending') is not True:
    fail('[5] canonicalization.json_keys_sorted_ascending must be true')
if canon.get('strip_volatile_fields') is not True:
    fail('[5] canonicalization.strip_volatile_fields must be true')
if canon.get('strip_pii_fields') is not True:
    fail('[5] canonicalization.strip_pii_fields must be true')
if canon.get('include_operation_family') is not True:
    fail('[5] canonicalization.include_operation_family must be true')
if canon.get('include_user_id') is not True:
    fail('[5] canonicalization.include_user_id must be true')
pii_listed = set(canon.get('pii_fields') or [])
missing_pii = PII_FIELDS_REQUIRED - pii_listed
if missing_pii:
    fail(f'[5] canonicalization.pii_fields missing: {sorted(missing_pii)}')

# [6] idempotency_conflict_rules
icr = contract.get('idempotency_conflict_rules') or {}
if icr.get('same_key_same_hash') != 'return_cached_result':
    fail('[6] idempotency_conflict_rules.same_key_same_hash must be return_cached_result')
if icr.get('same_key_diff_hash') != 'reject_with_conflict':
    fail('[6] idempotency_conflict_rules.same_key_diff_hash must be reject_with_conflict')
if icr.get('cross_user_collision') != 'forbidden':
    fail('[6] idempotency_conflict_rules.cross_user_collision must be forbidden')
if icr.get('cross_family_collision_with_same_user') != 'forbidden':
    fail('[6] idempotency_conflict_rules.cross_family_collision_with_same_user must be forbidden')
rw = icr.get('replay_window_seconds')
if not isinstance(rw, int) or rw <= 0:
    fail('[6] idempotency_conflict_rules.replay_window_seconds must be positive int')

# [7] per_family_critical_payload_subsets coverage 8/8
pfcps = contract.get('per_family_critical_payload_subsets') or {}
miss = REQUIRED_FAMILIES - set(pfcps.keys())
if miss:
    fail(f'[7] per_family_critical_payload_subsets missing families: {sorted(miss)}')
for fam, subset in pfcps.items():
    if not isinstance(subset, list) or len(subset) == 0:
        fail(f'[7] per_family_critical_payload_subsets[{fam}] must be non-empty list')
    for f_ in (subset or []):
        if f_ in {'email', 'ip', 'device_id', 'push_token', 'phone', 'hwid', 'client_ip'}:
            fail(f'[7] per_family_critical_payload_subsets[{fam}] contains PII field: {f_}')

# [8] operation_families list
fams_list = set(contract.get('operation_families') or [])
if fams_list != REQUIRED_FAMILIES:
    fail(f'[8] operation_families must equal 8 required families, got {sorted(fams_list)}')

# [9] per_family_status
pfs = contract.get('per_family_status') or {}
for fam in REQUIRED_FAMILIES:
    if pfs.get(fam) != 'preview_only_safety_layer_present':
        fail(f'[9] per_family_status[{fam}] must be preview_only_safety_layer_present')

# [10] safety_invariants
si = contract.get('safety_invariants') or {}
for key in [
    'no_pii_in_request_hash', 'no_pii_in_idempotency_key',
    'no_live_apply_in_this_pack', 'no_live_claim_in_this_pack',
    'no_live_commit_in_this_pack', 'no_db_writes_in_this_pack',
    'no_reward_grant_in_this_pack', 'no_premium_currency_use_in_this_pack',
    'no_bp_delta_runtime_in_this_pack', 'no_gear_mutation_in_this_pack',
    'no_gem_inventory_mutation_in_this_pack', 'no_user_materials_mutation_in_this_pack',
]:
    if si.get(key) is not True:
        fail(f'[10] safety_invariants.{key} must be true')

# [11] forbidden list non-empty and contains key terms
forbidden = set(contract.get('forbidden') or [])
for needed in {'hashing_pii', 'db_write_in_preview', 'live_apply_in_preview', 'reward_grant_in_preview'}:
    if needed not in forbidden:
        fail(f'[11] forbidden list missing: {needed}')

# [12] marker references
refs = marker.get('references') or {}
if refs.get('suite_tuple') != 'PROJECT-SHARED-REQUEST-HASH-IDEMPOTENCY-CONTRACT':
    fail('[12] marker.references.suite_tuple mismatch')
if refs.get('validator') != 'backend/scripts/validate_shared_request_hash_idempotency_contract_v1.py':
    fail('[12] marker.references.validator mismatch')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT-SHARED-REQUEST-HASH-IDEMPOTENCY-CONTRACT validator')
    sys.exit(1)

print('[PASS] PROJECT-SHARED-REQUEST-HASH-IDEMPOTENCY-CONTRACT validator')
sys.exit(0)
