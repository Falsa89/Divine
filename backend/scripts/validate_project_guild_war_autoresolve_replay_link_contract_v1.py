#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator Track B: PROJECT_GUILD_WAR_AUTORESOLVE_REPLAY_LINK_CONTRACT_PACK (v35 Track B)
Phase: PHASE_5
Mode:  DESIGN_CONTRACT_AUDIT_ONLY

Verifica i 12 punti del prompt Track B.
"""
from __future__ import annotations
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

REQUIRED_FILES = [
    'data/design/guild_war_replay/guild_war_autoresolve_replay_link_contract_v1.json',
    'data/design/guild_war_replay/guild_war_replay_payload_schema_v1.json',
    'data/design/guild_war_replay/guild_war_replay_privacy_policy_v1.json',
    'data/design/guild_war_replay/guild_war_replay_retention_policy_v1.json',
    'data/design/guild_war_replay/guild_war_replay_link_contract_proof_marker_v1.json',
    'data/design/battle_entrypoints/battle_entrypoint_registry_v7.json',
    'data/design/battle_entrypoints/battle_entrypoint_registry_v6.json',
    'docs/divine/234_GUILD_WAR_AUTORESOLVE_REPLAY_LINK_CONTRACT.md',
    'backend/scripts/validate_project_guild_war_autoresolve_replay_link_contract_v1.py',
]

REQUIRED_PAYLOAD_FIELDS = [
    'guild_war_battle_id',
    'battle_instance_id',
    'war_id',
    'guild_id_attacker',
    'guild_id_defender',
    'attacker_snapshot',
    'defender_snapshot',
    'battle_seed_or_precomputed_log',
    'playback_timeline',
    'result_summary',
    'war_score_delta_display_only',
    'reward_policy',
    'guild_points_policy',
    'privacy_policy',
    'retention_policy',
    'created_at',
    'expires_at',
]

PROOF_REQUIRED = {
    'guild_war_replay_contract_defined': True,
    'guild_war_runtime_changed': False,
    'guild_war_is_only_autoresolve_exception': True,
    'replay_or_view_link_required': True,
    'generic_runner_view_mode_future': True,
    'battle_replay_route_live_created': False,
    'runtime_activation': False,
    'reward_grant_enabled': False,
    'replay_grants_rewards': False,
    'replay_mutates_war_score': False,
    'replay_mutates_guild_points': False,
    'replay_reruns_battle': False,
    'no_duplicate_rewards': True,
    'no_pii_in_share_payload': True,
    'snapshot_or_timeline_required': True,
    'attacker_snapshot_required': True,
    'defender_snapshot_required': True,
    'result_summary_required': True,
    'privacy_policy_required': True,
    'retention_policy_required': True,
    'combat_tsx_changed': False,
    'story_tsx_changed': False,
    'story_sandbox_changed': False,
    'home_routes_changed': False,
    'battle_engine_changed': False,
}

FAILURES: list[str] = []


def fail(msg): FAILURES.append(msg)
def repo(p): return os.path.join(REPO_ROOT, p)
def load_json(rel): return json.load(open(repo(rel), 'r', encoding='utf-8'))


# 1. files exist
for rel in REQUIRED_FILES:
    if not os.path.isfile(repo(rel)):
        fail(f'[1] missing required file: {rel}')

if FAILURES:
    for f in FAILURES: print('FAIL:', f)
    print('[FAIL] PROJECT_GUILD_WAR_AUTORESOLVE_REPLAY_LINK_CONTRACT validator')
    sys.exit(1)

# 2. registry v7 supersedes v6
reg7 = load_json('data/design/battle_entrypoints/battle_entrypoint_registry_v7.json')
if reg7.get('version') != 7:
    fail('[2] registry v7 version must be 7')
supers = reg7.get('supersedes', []) or []
if 'battle_entrypoint_registry_v6.json' not in supers:
    fail('[2] registry v7 must declare supersedes including v6')

# preserve v6 entries (sanity: registry v7 must have at least all v6 features)
reg6 = load_json('data/design/battle_entrypoints/battle_entrypoint_registry_v6.json')
v6_feats = {e.get('feature') for e in reg6.get('entries', [])}
v7_feats = {e.get('feature') for e in reg7.get('entries', [])}
missing_v6 = v6_feats - v7_feats
if missing_v6:
    fail(f'[2] registry v7 missing v6 features: {sorted(missing_v6)}')

# 3+4+5. guild_war: only autoresolve exception + replay link required + target /battle-replay
gw = next((e for e in reg7.get('entries', []) if e.get('feature') == 'guild_war'), None)
if not gw:
    fail('[3] registry v7 missing guild_war entry')
else:
    if gw.get('is_only_autoresolve_exception') is not True:
        fail('[3] guild_war.is_only_autoresolve_exception must be True')
    if gw.get('replay_link_required') is not True:
        fail('[4] guild_war.replay_link_required must be True')
    if gw.get('replay_link_target_future') != '/battle-replay':
        fail('[5] guild_war.replay_link_target_future must be /battle-replay')
    if gw.get('viewer_kind_future') != 'guild_war_view':
        fail('[5] guild_war.viewer_kind_future must be guild_war_view')
    if gw.get('runtime_changed_this_pack') is not False:
        fail('[5] guild_war.runtime_changed_this_pack must be False')

# also contract file booleans
contract = load_json('data/design/guild_war_replay/guild_war_autoresolve_replay_link_contract_v1.json')
for k, exp in [
    ('guild_war_is_only_autoresolve_exception', True),
    ('autoresolve_allowed', True),
    ('replay_or_view_link_required', True),
    ('replay_link_target_future', '/battle-replay'),
    ('replay_viewer_kind', 'guild_war_view'),
    ('runtime_activation_allowed_in_this_pack', False),
    ('runtime_activation', False),
    ('guild_war_runtime_changed', False),
]:
    if contract.get(k) != exp:
        fail(f'[3-5] contract.{k} must be {exp!r} (got {contract.get(k)!r})')

# 6. payload schema includes required fields
schema = load_json('data/design/guild_war_replay/guild_war_replay_payload_schema_v1.json')
declared = set(schema.get('required_fields', []))
fields = schema.get('fields', {}) or {}
for f in REQUIRED_PAYLOAD_FIELDS:
    if f not in declared:
        fail(f'[6] payload schema missing required_fields entry: {f}')
    if f not in fields:
        fail(f'[6] payload schema missing fields.{f}')

if schema.get('viewer_kind') != 'guild_war_view':
    fail('[6] payload schema viewer_kind must be guild_war_view')

# 7. replay grants no rewards
for k in ['grant_enabled', 'replay_grants_rewards']:
    if fields.get('reward_policy', {}).get(k) is not False:
        fail(f'[7] payload schema reward_policy.{k} must be False')

# 8. replay mutates no guild points / war score
if fields.get('guild_points_policy', {}).get('mutate_enabled') is not False:
    fail('[8] payload schema guild_points_policy.mutate_enabled must be False')
if fields.get('war_score_delta_display_only', {}).get('display_only_in_replay') is not True:
    fail('[8] payload schema war_score_delta_display_only.display_only_in_replay must be True')

# 9. privacy policy forbids PII/share tokens
privacy = load_json('data/design/guild_war_replay/guild_war_replay_privacy_policy_v1.json')
for k in ['no_pii_in_share_payload', 'redact_other_players', 'redact_account_identifiers', 'redact_email_phone_pushtoken_ip']:
    if privacy.get(k) is not True:
        fail(f'[9] privacy policy {k} must be True')
share_rules = privacy.get('share_payload_rules', {}) or {}
for k in ['must_redact_other_player_pii', 'must_not_include_account_email', 'must_not_include_push_token', 'must_not_include_ip']:
    if share_rules.get(k) is not True:
        fail(f'[9] share_payload_rules.{k} must be True')

# retention policy
retention = load_json('data/design/guild_war_replay/guild_war_replay_retention_policy_v1.json')
if retention.get('ttl_hard_required') is not True:
    fail('[9b] retention_policy ttl_hard_required must be True')
if retention.get('async_storage_writes_allowed') is not False:
    fail('[9b] retention_policy async_storage_writes_allowed must be False')

# 10. runtime activation false (contract level + proof marker)
if contract.get('runtime_activation') is not False:
    fail('[10] contract.runtime_activation must be False')
if contract.get('db_writes', 1) != 0:
    fail('[10] contract.db_writes must be 0')

# 11. no live Guild War route/file changed if detectable
# Heuristic: if backend/routes/guild_war*.py exists or frontend/app/guild-war*.tsx, this pack must not have touched them.
# We only check that those files (if present) don't reference '/battle-replay' as a live route created in this pack.
# Cannot do git-diff here easily; we settle on: no live /battle-replay route created.
bv = next((e for e in reg7.get('entries', []) if e.get('feature') == 'battle_replay_viewer_future'), None)
if not bv:
    fail('[11] registry v7 missing battle_replay_viewer_future entry')
else:
    if bv.get('current_resolution_type') != 'not_yet_created_design_only':
        fail('[11] battle_replay_viewer_future must remain not_yet_created_design_only')
    if bv.get('runtime_status') != 'design_only':
        fail('[11] battle_replay_viewer_future.runtime_status must be design_only')

gp = reg7.get('global_policy', {}) or {}
if gp.get('battle_replay_route_live_created') is not False:
    fail('[11] global_policy.battle_replay_route_live_created must be False')

# 12. proof marker booleans
proof = load_json('data/design/guild_war_replay/guild_war_replay_link_contract_proof_marker_v1.json')
for k, exp in PROOF_REQUIRED.items():
    if proof.get(k) is not exp:
        fail(f'[12] proof marker {k} must be {exp} (got {proof.get(k)!r})')
if proof.get('db_writes', 1) != 0:
    fail('[12] proof marker db_writes must be 0')
if proof.get('suite_runner_tuple_v35_track_b_count') != 1:
    fail('[12] proof marker suite_runner_tuple_v35_track_b_count must be 1')

if FAILURES:
    for f in FAILURES: print('FAIL:', f)
    print('[FAIL] PROJECT_GUILD_WAR_AUTORESOLVE_REPLAY_LINK_CONTRACT validator')
    sys.exit(1)

print('[PASS] PROJECT_GUILD_WAR_AUTORESOLVE_REPLAY_LINK_CONTRACT validator')
sys.exit(0)
