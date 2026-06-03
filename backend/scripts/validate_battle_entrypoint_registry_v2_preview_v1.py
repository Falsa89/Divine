#!/usr/bin/env python3
"""Validator: PROJECT-BATTLE-ENTRYPOINT-REGISTRY-v2-PREVIEW (v55 Track A)."""
from __future__ import annotations
import os, sys, json, hashlib

ROOT = '/app'
REG = os.path.join(ROOT, 'data/design/release_acceleration/battle_entrypoint_registry_v2_preview.json')
CONTRACT = os.path.join(ROOT, 'data/design/release_acceleration/visual_battle_routing_expansion_contract_v1.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/battle_entrypoint_registry_v2_preview_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v55_MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW'
BATTLE_ENGINE_MD5 = '151ca35ad3bc35f0a6209cb3744ed440'
COMBAT_MD5 = 'fc792a05b2ada6e677d80400732ae5c3'
STORY_MD5 = '8520627b4e63f86821d73d8d3880bac3'

FAILS = []
def fail(m): FAILS.append(m)

def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()

if not os.path.exists(REG): fail(f'missing registry v2: {REG}')
else:
    r = json.load(open(REG))
    if r.get('public_sync_tag') != TAG: fail('registry public_sync_tag mismatch')
    if r.get('runtime_wired') is not False: fail('registry runtime_wired != false')
    if r.get('db_writes') != 0: fail('registry db_writes != 0')
    entries = {e.get('mode_id'): e for e in (r.get('entries') or [])}
    expected_modes = {'material_raid','training','story','boss','tower','event','arena','guild_war'}
    if set(entries.keys()) != expected_modes:
        fail(f'registry modes mismatch: got {sorted(entries.keys())}')
    for mode, e in entries.items():
        # universal invariants
        for k, v in (
            ('result_authoritative', False),
            ('reward_claim_enabled', False),
            ('reward_grant_enabled', False),
            ('db_writes', 0),
            ('battle_engine_runtime_used', False),
        ):
            if e.get(k) != v: fail(f'mode {mode} {k} != {v}')
    mr = entries['material_raid']
    if mr.get('current_state') != 'alpha_loop_closed_v53': fail('material_raid current_state mismatch')
    if mr.get('preview_route') != '/material-raid-visual-preview': fail('material_raid preview_route mismatch')
    if mr.get('reward_preview_route') != '/material-raid-reward-preview': fail('material_raid reward_preview_route mismatch')
    if mr.get('visual_battle_required') is not True: fail('material_raid visual_battle_required != true')
    if mr.get('auto_resolve_allowed') is not False: fail('material_raid auto_resolve_allowed != false')
    tr = entries['training']
    if tr.get('preview_route') != '/training-visual-preview': fail('training preview_route mismatch')
    if tr.get('visual_battle_required') is not True: fail('training visual_battle_required != true')
    if tr.get('auto_resolve_allowed') is not False: fail('training auto_resolve_allowed != false')
    if tr.get('safe_sandbox') is not True: fail('training safe_sandbox != true')
    st = entries['story']
    if st.get('visual_battle_required') is not True: fail('story visual_battle_required != true')
    if st.get('runtime_wiring_deferred') is not True: fail('story runtime_wiring_deferred != true')
    for mode in ('boss','tower','event','arena'):
        e = entries[mode]
        if e.get('visual_battle_required') is not True: fail(f'{mode} visual_battle_required != true')
        if e.get('runtime_wiring_deferred') is not True: fail(f'{mode} runtime_wiring_deferred != true')
    gw = entries['guild_war']
    if gw.get('auto_resolve_allowed') is not True: fail('guild_war auto_resolve_allowed != true')
    if gw.get('replay_link_required') is not True: fail('guild_war replay_link_required != true')
    if gw.get('replay_visualization_required') is not True: fail('guild_war replay_visualization_required != true')

if not os.path.exists(CONTRACT): fail('missing expansion contract')
else:
    c = json.load(open(CONTRACT))
    if c.get('public_sync_tag') != TAG: fail('contract public_sync_tag mismatch')
    if c.get('runtime_wired') is not False: fail('contract runtime_wired != false')
    if c.get('parent_design') != 'data/design/release_acceleration/battle_entrypoint_registry_design_v1.json':
        fail('contract parent_design must reference v54 registry')
    qp = set(c.get('supported_query_params') or [])
    expected_qp = {'mode','source_route','track_id','stage_id','chapter_id','battle_seed_preview','team_power','recommended_power','enemy_family_preview'}
    if qp != expected_qp: fail(f'contract supported_query_params mismatch: {sorted(qp)}')
    inv = c.get('contract_invariants') or {}
    for k, v in (('result_authoritative',False),('reward_claim_enabled',False),('reward_grant_enabled',False),('db_writes',0),('battle_engine_runtime_used',False)):
        if inv.get(k) != v: fail(f'contract_invariants {k} != {v}')
    gw = c.get('guild_war_exception') or {}
    if gw.get('auto_resolve_allowed') is not True: fail('contract guild_war_exception auto_resolve_allowed != true')
    if gw.get('replay_link_required') is not True: fail('contract guild_war_exception replay_link_required != true')
    if gw.get('unchanged_in_v55') is not True: fail('contract guild_war_exception unchanged_in_v55 != true')

# MD5: battle_engine.py / combat.tsx / story.tsx UNCHANGED
if md5(os.path.join(ROOT,'backend/battle_engine.py')) != BATTLE_ENGINE_MD5: fail('battle_engine.py MD5 drift')
if md5(os.path.join(ROOT,'frontend/app/combat.tsx')) != COMBAT_MD5: fail('combat.tsx MD5 drift')
if md5(os.path.join(ROOT,'frontend/app/story.tsx')) != STORY_MD5: fail('story.tsx MD5 drift')

if not os.path.exists(MARKER): fail('missing marker')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('marker_version','battle_entrypoint_registry_v2_preview_marker_v1'),
        ('track','A'),
        ('modes_total',8),
        ('runtime_wired',False),
        ('battle_engine_changed',False),
        ('combat_tsx_changed',False),
        ('story_tsx_changed',False),
        ('battle_simulate_endpoint_changed',False),
        ('story_battle_endpoint_changed',False),
        ('guild_war_policy_regression',False),
        ('db_writes',0),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-BATTLE-ENTRYPOINT-REGISTRY-v2-PREVIEW validator')
    sys.exit(1)
print('[PASS] PROJECT-BATTLE-ENTRYPOINT-REGISTRY-v2-PREVIEW validator')
sys.exit(0)
