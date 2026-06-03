#!/usr/bin/env python3
"""Validator: PROJECT-VISUAL-BATTLE-RUNNER-PAYLOAD-CONTRACT-v0 (v59 Track A).

Verifica payload_contract_v0 + stop_gates + marker.
design_only=true, runtime_runner_created=false, db_writes=0,
battle_engine_runtime_used=false, backend_used=false.
No fake PASS. No validator weakening.
"""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_8_LOCAL_TIMELINE_AND_RUNNER_PAYLOAD_CONTRACT_BATCH_PACK_v59'
TAG = 'PUBLIC_SYNC_TAG_v59_MEGA_RELEASE_ACCELERATION_8_LOCAL_TIMELINE_AND_RUNNER_PAYLOAD_CONTRACT_BATCH'
CONTRACT = os.path.join(ROOT, 'data/design/release_acceleration/visual_battle_runner_payload_contract_v0.json')
STOPS = os.path.join(ROOT, 'data/design/release_acceleration/visual_battle_runner_payload_contract_stop_gates_v0.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/visual_battle_runner_payload_contract_v0_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(CONTRACT):
    fail(f'missing contract: {CONTRACT}')
else:
    c = json.load(open(CONTRACT))
    if c.get('version') != 'visual_battle_runner_payload_contract_v0': fail('contract.version mismatch')
    if c.get('payload_version') != 'visual_battle_runner_payload_v0': fail('contract.payload_version mismatch')
    if c.get('pack') != PACK: fail('contract.pack mismatch')
    if c.get('public_sync_tag') != TAG: fail('contract.public_sync_tag mismatch')
    for k, v in (
        ('design_only', True), ('runtime_runner_created', False),
        ('battle_engine_runtime_used', False), ('battle_engine_py_changed', False),
        ('combat_tsx_changed', False), ('backend_used', False), ('db_writes', 0),
        ('result_authoritative', False), ('reward_grant_enabled', False),
        ('reward_claim_enabled', False), ('live_claim_enabled', False),
    ):
        if c.get(k) != v: fail(f'contract.{k} != {v} (got {c.get(k)})')
    if c.get('consumer_future_route') != '/visual-battle-preview-router':
        fail('contract.consumer_future_route mismatch')
    if c.get('guild_war_policy') != 'autoresolve_with_replay_link_exception':
        fail('contract.guild_war_policy mismatch')
    modes = c.get('compatible_modes') or []
    for m in ('material_raid','training','boss','story','tower','event','arena'):
        if m not in modes: fail(f'contract.compatible_modes missing {m}')
    req = c.get('required_fields') or []
    for f in ('mode','source_route','battle_seed_preview','result_authoritative',
              'battle_engine_runtime_used','db_writes','reward_grant_enabled','reward_claim_enabled'):
        if f not in req: fail(f'contract.required_fields missing {f}')
    opt = c.get('optional_fields') or []
    for f in ('stage_id','chapter_id','tower_id','floor_id','event_id','arena_bracket_preview',
              'boss_family_id','team_power','recommended_power','enemy_family_preview',
              'background_hint','music_hint','tutorial_hint'):
        if f not in opt: fail(f'contract.optional_fields missing {f}')

if not os.path.exists(STOPS):
    fail(f'missing stop gates: {STOPS}')
else:
    s = json.load(open(STOPS))
    if s.get('version') != 'visual_battle_runner_payload_contract_stop_gates_v0': fail('stops.version mismatch')
    if s.get('design_only') is not True: fail('stops.design_only != True')
    if s.get('db_writes') != 0: fail('stops.db_writes != 0')
    gates = s.get('stop_gates') or []
    if len(gates) < 5: fail(f'stops.stop_gates count too low: {len(gates)}')
    rules = {g.get('rule') for g in gates}
    for r in ('no_runtime_runner_without_director_approval',
              'no_battle_engine_wiring_without_separate_pack',
              'no_reward_result_without_economy_approval',
              'no_backend_route_without_api_approval',
              'no_db_writes_without_manual_approval_checksum'):
        if r not in rules: fail(f'stops missing rule {r}')

if not os.path.exists(MARKER):
    fail(f'missing marker: {MARKER}')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'visual_battle_runner_payload_contract_v0_marker_v1': fail('marker.version mismatch')
    for k, v in (('pack',PACK),('public_sync_tag',TAG),('design_only',True),
                 ('runtime_runner_created',False),('battle_engine_runtime_used',False),
                 ('backend_used',False),('db_writes',0),
                 ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k) != v: fail(f'marker.{k} != {v} (got {mk.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-VISUAL-BATTLE-RUNNER-PAYLOAD-CONTRACT-v0')
    sys.exit(1)
print('[PASS] PROJECT-VISUAL-BATTLE-RUNNER-PAYLOAD-CONTRACT-v0')
sys.exit(0)
