#!/usr/bin/env python3
"""Validator: PROJECT-VISUAL-BATTLE-RUNNER-ROUTER-ADAPTER-PREVIEW (v60 Track A+B)."""
from __future__ import annotations
import os, sys, re, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH_PACK_v60'
TAG = 'PUBLIC_SYNC_TAG_v60_MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH'
CONTRACT = os.path.join(ROOT, 'data/design/release_acceleration/visual_battle_runner_router_adapter_preview_contract_v1.json')
MAPPING = os.path.join(ROOT, 'data/design/release_acceleration/visual_battle_runner_payload_adapter_preview_mapping_v1.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/visual_battle_runner_router_adapter_preview_marker_v1.json')
ROUTER = os.path.join(ROOT, 'frontend/app/visual-battle-preview-router.tsx')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(CONTRACT):
    fail(f'missing contract: {CONTRACT}')
else:
    c = json.load(open(CONTRACT))
    if c.get('version') != 'visual_battle_runner_router_adapter_preview_contract_v1': fail('contract.version mismatch')
    if c.get('pack') != PACK: fail('contract.pack mismatch')
    if c.get('public_sync_tag') != TAG: fail('contract.public_sync_tag mismatch')
    for k, v in (('design_only',True),('adapter_preview_only',True),('runtime_runner_created',False),
                 ('backend_used',False),('battle_engine_runtime_used',False),('db_writes',0),
                 ('result_authoritative',False),('reward_grant_enabled',False),('reward_claim_enabled',False),
                 ('compatible_with_payload_contract_v0',True)):
        if c.get(k) != v: fail(f'contract.{k} != {v} (got {c.get(k)})')
    if c.get('source_contract') != 'visual_battle_runner_payload_contract_v0': fail('contract.source_contract mismatch')
    if c.get('target_route') != '/visual-battle-preview-router': fail('contract.target_route mismatch')
    if c.get('guild_war_policy') != 'autoresolve_with_replay_link_exception': fail('contract.guild_war_policy mismatch')
    modes = c.get('supported_modes') or []
    for m in ('material_raid','training','boss','story','tower','event','arena'):
        if m not in modes: fail(f'contract.supported_modes missing {m}')
    af = c.get('adapter_fields_to_display') or []
    for f in ('mode','source_route','battle_seed_preview','team_power','recommended_power',
              'enemy_family_preview','background_hint','music_hint','tutorial_hint',
              'result_authoritative','battle_engine_runtime_used','db_writes',
              'reward_grant_enabled','reward_claim_enabled'):
        if f not in af: fail(f'contract.adapter_fields_to_display missing {f}')
    gates = c.get('stop_gates') or []
    if len(gates) < 5: fail(f'contract.stop_gates count too low: {len(gates)}')

if not os.path.exists(MAPPING):
    fail(f'missing mapping: {MAPPING}')
else:
    mp = json.load(open(MAPPING))
    if mp.get('version') != 'visual_battle_runner_payload_adapter_preview_mapping_v1': fail('mapping.version mismatch')
    if mp.get('source_contract') != 'visual_battle_runner_payload_contract_v0': fail('mapping.source_contract mismatch')
    if mp.get('db_writes') != 0: fail('mapping.db_writes != 0')
    inv = mp.get('invariant_fields_default_values') or {}
    for k, v in (('result_authoritative',False),('battle_engine_runtime_used',False),
                 ('db_writes',0),('reward_grant_enabled',False),('reward_claim_enabled',False)):
        if inv.get(k) != v: fail(f'mapping.invariant_fields_default_values.{k} != {v}')

if not os.path.exists(ROUTER):
    fail(f'missing router: {ROUTER}')
else:
    src = open(ROUTER).read()
    if 'Payload Contract v0 Adapter Preview' not in src:
        fail('router missing Payload Contract v0 Adapter Preview block')
    if 'visual_battle_runner_payload_contract_v0' not in src:
        fail('router missing reference to payload contract v0')
    # ensure existing mode blocks preserved
    for m in ('training','boss','story','tower','event','arena'):
        if f"mode === '{m}'" not in src:
            fail(f'regression: missing mode block {m}')
    # forbidden
    for pat, desc in [
        (r"from\s+['\"][^'\"]*combat['\"]", 'combat import'),
        (r"from\s+['\"][^'\"]*story['\"]", 'story import'),
        (r'react-native-reanimated', 'reanimated'),
        (r'\bfetch\s*\(', 'fetch call'),
        (r'\baxios\b', 'axios usage'),
        (r"['\"`(]/api/", '/api/ use'),
        (r'battle_engine\s*\(', 'battle_engine call'),
        (r"from\s+['\"][^'\"]*battle_engine", 'battle_engine import'),
        (r'>\s*Claim\s*<', 'Claim CTA'),
    ]:
        if re.search(pat, src):
            fail(f'router forbidden {desc}')

if not os.path.exists(MARKER):
    fail(f'missing marker: {MARKER}')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'visual_battle_runner_router_adapter_preview_marker_v1': fail('marker.version mismatch')
    for k, v in (('pack',PACK),('public_sync_tag',TAG),('design_only',True),
                 ('adapter_preview_only',True),('runtime_runner_created',False),
                 ('backend_used',False),('battle_engine_runtime_used',False),('db_writes',0),
                 ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k) != v: fail(f'marker.{k} != {v} (got {mk.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-VISUAL-BATTLE-RUNNER-ROUTER-ADAPTER-PREVIEW')
    sys.exit(1)
print('[PASS] PROJECT-VISUAL-BATTLE-RUNNER-ROUTER-ADAPTER-PREVIEW')
sys.exit(0)
