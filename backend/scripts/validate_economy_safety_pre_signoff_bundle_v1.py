#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator Track C: PROJECT-ECONOMY-SAFETY-PRE-SIGNOFF-ROLLBACK-BUNDLE
Pack: MEGA_ECONOMY_SAFETY_ACCELERATION_5_OBSERVABILITY_SIGNOFF_AND_REQUEST_HASH_PACK_v41

Asserisce che il bundle pre-signoff (readiness matrix, signoff register,
canary/live state, rollback templates) sia presente e coerente con i
vincoli del pack: tutte le 8 famiglie con signoff=pending, canary=false,
live=false, db_writes=0, rollback templates dry-run only.
"""
from __future__ import annotations
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

RM_REL = 'data/design/economy_safety/economy_safety_pre_signoff_readiness_matrix_v1.json'
SR_REL = 'data/design/economy_safety/economy_safety_pre_signoff_signoff_register_v1.json'
CL_REL = 'data/design/economy_safety/economy_safety_pre_signoff_canary_live_state_v1.json'
RT_REL = 'data/design/economy_safety/economy_safety_pre_signoff_rollback_templates_v1.json'
MARKER_REL = 'data/design/economy_safety/economy_safety_pre_signoff_rollback_bundle_proof_marker_v1.json'
DOC_REL = 'docs/divine/256_MEGA_ECONOMY_SAFETY_ACCELERATION_5_OBSERVABILITY_SIGNOFF_AND_REQUEST_HASH_PACK_v41_TRACK_C.md'

REQUIRED_FAMILIES = {
    'gem_socket_commit', 'material_raid_claim',
    'gear_forge_fusion_commit', 'rune_scroll_talisman_commit',
    'artifact_upgrade_commit', 'divine_weapon_upgrade_commit',
    'battle_pass_reward_claim', 'mail_reward_claim',
}

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def repo(p: str) -> str:
    return os.path.join(REPO_ROOT, p)


def load_json(rel: str):
    return json.load(open(repo(rel), 'r', encoding='utf-8'))


# [1] esistenza
for rel in (RM_REL, SR_REL, CL_REL, RT_REL, MARKER_REL, DOC_REL):
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing required file: {rel}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT-ECONOMY-SAFETY-PRE-SIGNOFF-ROLLBACK-BUNDLE validator')
    sys.exit(1)

rm = load_json(RM_REL)
sr = load_json(SR_REL)
cl = load_json(CL_REL)
rt = load_json(RT_REL)
marker = load_json(MARKER_REL)

# [2] runtime/db invariants
for name, obj in [('rm', rm), ('sr', sr), ('cl', cl), ('rt', rt), ('marker', marker)]:
    if obj.get('runtime_activation') is not False:
        fail(f'[2] {name}.runtime_activation must be false')
    if obj.get('db_writes') != 0:
        fail(f'[2] {name}.db_writes must be 0')

# [3] readiness matrix
rmtx = rm.get('readiness_matrix') or {}
miss = REQUIRED_FAMILIES - set(rmtx.keys())
if miss:
    fail(f'[3] readiness_matrix missing families: {sorted(miss)}')
for fam in REQUIRED_FAMILIES:
    node = rmtx.get(fam, {}) or {}
    for k, exp in [
        ('safety_preview_present', True),
        ('validator_present', True),
        ('proof_marker_present', True),
        ('server_registered', True),
        ('request_hash_contract_covered', True),
        ('observability_metrics_covered', True),
        ('observability_alert_rules_covered', True),
        ('rollback_template_present', True),
        ('signoff_state', 'pending'),
        ('canary_enabled', False),
        ('live_enabled', False),
        ('db_writes', 0),
    ]:
        if node.get(k) != exp:
            fail(f'[3] readiness_matrix[{fam}].{k} must be {exp!r} (got {node.get(k)!r})')

gi = rm.get('global_invariants') or {}
for k, exp in [
    ('all_8_operation_families_have_preview_safety_layer', True),
    ('all_8_operation_families_have_validator', True),
    ('all_8_operation_families_have_proof_marker', True),
    ('all_8_operation_families_signoff_pending', True),
    ('all_8_operation_families_canary_disabled', True),
    ('all_8_operation_families_live_disabled', True),
    ('total_db_writes_across_all_families', 0),
    ('live_commit_allowed_in_this_pack', False),
    ('live_claim_allowed_in_this_pack', False),
    ('reward_grant_enabled_in_this_pack', False),
    ('bp_delta_runtime_enabled_in_this_pack', False),
]:
    if gi.get(k) != exp:
        fail(f'[3] readiness_matrix.global_invariants.{k} must be {exp!r} (got {gi.get(k)!r})')

# [4] signoff_register: 8 famiglie tutte pending
sreg = sr.get('signoff_register') or {}
miss = REQUIRED_FAMILIES - set(sreg.keys())
if miss:
    fail(f'[4] signoff_register missing families: {sorted(miss)}')
for fam in REQUIRED_FAMILIES:
    node = sreg.get(fam, {}) or {}
    if node.get('signoff_state') != 'pending':
        fail(f'[4] signoff_register[{fam}].signoff_state must be pending')
    if node.get('approved_by') is not None:
        fail(f'[4] signoff_register[{fam}].approved_by must be null')
    if node.get('approved_at_utc') is not None:
        fail(f'[4] signoff_register[{fam}].approved_at_utc must be null')
ssm = sr.get('signoff_state_machine') or {}
states = set(ssm.get('states') or [])
for s in ('pending', 'approved', 'blocked', 'rolled_back'):
    if s not in states:
        fail(f'[4] signoff_state_machine.states missing {s}')

# [5] canary_live_state: 8 famiglie tutte canary=false, live=false, pct=0
cls = cl.get('canary_live_state') or {}
miss = REQUIRED_FAMILIES - set(cls.keys())
if miss:
    fail(f'[5] canary_live_state missing families: {sorted(miss)}')
for fam in REQUIRED_FAMILIES:
    node = cls.get(fam, {}) or {}
    if node.get('canary_enabled') is not False:
        fail(f'[5] canary_live_state[{fam}].canary_enabled must be false')
    if node.get('live_enabled') is not False:
        fail(f'[5] canary_live_state[{fam}].live_enabled must be false')
    if node.get('canary_pct') != 0:
        fail(f'[5] canary_live_state[{fam}].canary_pct must be 0')
    if not isinstance(node.get('feature_flag'), str) or not node.get('feature_flag'):
        fail(f'[5] canary_live_state[{fam}].feature_flag must be non-empty string')
cl_gi = cl.get('global_invariants') or {}
for k, exp in [
    ('all_canary_disabled', True),
    ('all_live_disabled', True),
    ('max_canary_pct_observed', 0),
    ('db_writes', 0),
]:
    if cl_gi.get(k) != exp:
        fail(f'[5] canary_live_state.global_invariants.{k} must be {exp!r}')

# [6] rollback_templates: 8 famiglie con template idempotent dry-run
rtt = rt.get('rollback_templates') or {}
miss = REQUIRED_FAMILIES - set(rtt.keys())
if miss:
    fail(f'[6] rollback_templates missing families: {sorted(miss)}')
for fam in REQUIRED_FAMILIES:
    node = rtt.get(fam, {}) or {}
    if not isinstance(node.get('template_id'), str) or not node.get('template_id').startswith('ROLLBACK_'):
        fail(f'[6] rollback_templates[{fam}].template_id must start with ROLLBACK_')
    if node.get('rollback_idempotent') is not True:
        fail(f'[6] rollback_templates[{fam}].rollback_idempotent must be true')
    if node.get('db_writes') != 0:
        fail(f'[6] rollback_templates[{fam}].db_writes must be 0')
    steps = node.get('steps_dry_run_only') or []
    if not isinstance(steps, list) or len(steps) == 0:
        fail(f'[6] rollback_templates[{fam}].steps_dry_run_only must be non-empty list')
    triggers = node.get('trigger_conditions') or []
    if 'manual_safety_override' not in triggers:
        fail(f'[6] rollback_templates[{fam}].trigger_conditions must include manual_safety_override')
rt_gi = rt.get('global_invariants') or {}
for k, exp in [
    ('all_8_operation_families_have_rollback_template', True),
    ('rollback_idempotent_for_all', True),
    ('rollback_dry_run_only_in_this_pack', True),
    ('db_writes', 0),
]:
    if rt_gi.get(k) != exp:
        fail(f'[6] rollback_templates.global_invariants.{k} must be {exp!r}')

# [7] marker references
refs = marker.get('references') or {}
for key in ('readiness_matrix', 'signoff_register', 'canary_live_state',
            'rollback_templates', 'doc', 'validator', 'suite_tuple'):
    if not refs.get(key):
        fail(f'[7] marker.references.{key} missing')
if refs.get('suite_tuple') != 'PROJECT-ECONOMY-SAFETY-PRE-SIGNOFF-ROLLBACK-BUNDLE':
    fail('[7] marker.references.suite_tuple mismatch')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT-ECONOMY-SAFETY-PRE-SIGNOFF-ROLLBACK-BUNDLE validator')
    sys.exit(1)

print('[PASS] PROJECT-ECONOMY-SAFETY-PRE-SIGNOFF-ROLLBACK-BUNDLE validator')
sys.exit(0)
