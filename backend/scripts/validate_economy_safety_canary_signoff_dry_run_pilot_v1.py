#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator Track C: PROJECT-ECONOMY-SAFETY-CANARY-SIGNOFF-DRY-RUN-PILOT
Pack: MEGA_ECONOMY_SAFETY_ACCELERATION_6_DRY_RUN_RUNTIME_INSTRUMENTATION_PACK_v42

Asserisce che il pilot canary/signoff per material_raid_claim sia presente,
coerente, e che signoff/canary/live restino disabilitati in questo pack.
"""
from __future__ import annotations
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PILOT_REL = 'data/design/economy_safety/economy_safety_canary_signoff_dry_run_pilot_v1.json'
MARKER_REL = 'data/design/economy_safety/economy_safety_canary_signoff_dry_run_proof_marker_v1.json'
DOC_REL = 'docs/divine/258_ECONOMY_SAFETY_CANARY_SIGNOFF_DRY_RUN_PILOT.md'
ROLLBACK_REL = 'data/design/economy_safety/economy_safety_pre_signoff_rollback_templates_v1.json'

REQUIRED_APPROVERS = {'game_director', 'technical_producer', 'qa_owner', 'rollback_owner'}
REQUIRED_ALERTS = {
    'ALERT_DB_WRITES_NONZERO',
    'ALERT_LIVE_CLAIM_NONZERO',
    'ALERT_REWARD_GRANTS_NONZERO',
}

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def repo(p: str) -> str:
    return os.path.join(REPO_ROOT, p)


def load_json(rel: str):
    return json.load(open(repo(rel), 'r', encoding='utf-8'))


# [1] file esistenti
for rel in (PILOT_REL, MARKER_REL, DOC_REL, ROLLBACK_REL):
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing required file: {rel}')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT-ECONOMY-SAFETY-CANARY-SIGNOFF-DRY-RUN-PILOT validator')
    sys.exit(1)

pilot = load_json(PILOT_REL)
marker = load_json(MARKER_REL)
rollback = load_json(ROLLBACK_REL)

# [2] pilot top-level invariants
if pilot.get('runtime_activation') is not False:
    fail('[2] pilot.runtime_activation must be false')
if pilot.get('db_writes') != 0:
    fail('[2] pilot.db_writes must be 0')
if pilot.get('mode') != 'DESIGN_CONTRACT_AUDIT_ONLY':
    fail('[2] pilot.mode must be DESIGN_CONTRACT_AUDIT_ONLY')

# [3] pilot block
p = pilot.get('pilot') or {}
for key, exp in [
    ('operation_family', 'material_raid_claim'),
    ('signoff_state', 'pending'),
    ('approved_by', None),
    ('approved_at_utc', None),
    ('canary_enabled', False),
    ('canary_percentage', 0),
    ('live_enabled', False),
    ('live_claim_enabled', False),
    ('reward_grant_enabled', False),
    ('material_grant_enabled', False),
    ('premium_currency_use_enabled', False),
    ('bp_delta_runtime_enabled', False),
    ('db_writes', 0),
    ('feature_flag', 'MATERIAL_RAID_CLAIM_SAFETY_PREVIEW_ENABLED'),
    ('kill_switch_env_var', 'MATERIAL_RAID_CLAIM_CANARY_KILL_SWITCH'),
    ('kill_switch_default_state', 'engaged_kill'),
]:
    if p.get(key) != exp:
        fail(f'[3] pilot.{key} must be {exp!r} (got {p.get(key)!r})')

approvers = set(p.get('approval_required_from') or [])
miss_app = REQUIRED_APPROVERS - approvers
if miss_app:
    fail(f'[3] pilot.approval_required_from missing: {sorted(miss_app)}')

alerts = set(p.get('required_alerts') or [])
miss_al = REQUIRED_ALERTS - alerts
if miss_al:
    fail(f'[3] pilot.required_alerts missing: {sorted(miss_al)}')

rl = p.get('rollback_template_link') or ''
if 'economy_safety_pre_signoff_rollback_templates_v1.json' not in rl:
    fail('[3] pilot.rollback_template_link must reference rollback templates v1')
if 'material_raid_claim' not in rl:
    fail('[3] pilot.rollback_template_link must target material_raid_claim')

if 'economy_safety_overview_v1' not in (p.get('required_dashboards') or []):
    fail('[3] pilot.required_dashboards must include economy_safety_overview_v1')

# [4] global invariants
gi = pilot.get('global_invariants') or {}
for key, exp in [
    ('signoff_state_must_be_pending_in_this_pack', True),
    ('canary_must_remain_disabled_in_this_pack', True),
    ('live_must_remain_disabled_in_this_pack', True),
    ('reward_grant_must_remain_disabled_in_this_pack', True),
    ('material_grant_must_remain_disabled_in_this_pack', True),
    ('db_writes', 0),
]:
    if gi.get(key) != exp:
        fail(f'[4] pilot.global_invariants.{key} must be {exp!r}')

# [5] marker invariants
for key, exp in [
    ('runtime_activation', False), ('db_writes', 0),
    ('live_apply_allowed', False), ('live_commit_allowed', False),
    ('live_claim_allowed', False), ('reward_grant_enabled', False),
    ('material_grant_enabled', False),
    ('signoff_state', 'pending'),
    ('canary_enabled', False), ('canary_percentage', 0),
]:
    if marker.get(key) != exp:
        fail(f'[5] marker.{key} must be {exp!r}')
refs = marker.get('references') or {}
if refs.get('suite_tuple') != 'PROJECT-ECONOMY-SAFETY-CANARY-SIGNOFF-DRY-RUN-PILOT':
    fail('[5] marker.references.suite_tuple mismatch')

# [6] rollback templates ancora coerenti per material_raid_claim
rtt = rollback.get('rollback_templates') or {}
mr = rtt.get('material_raid_claim', {}) or {}
if mr.get('rollback_idempotent') is not True:
    fail('[6] rollback template material_raid_claim.rollback_idempotent must be true')
if mr.get('db_writes') != 0:
    fail('[6] rollback template material_raid_claim.db_writes must be 0')

if FAILURES:
    for f in FAILURES:
        print('FAIL:', f)
    print('[FAIL] PROJECT-ECONOMY-SAFETY-CANARY-SIGNOFF-DRY-RUN-PILOT validator')
    sys.exit(1)

print('[PASS] PROJECT-ECONOMY-SAFETY-CANARY-SIGNOFF-DRY-RUN-PILOT validator')
sys.exit(0)
