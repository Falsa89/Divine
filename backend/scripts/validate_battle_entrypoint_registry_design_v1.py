#!/usr/bin/env python3
"""Validator: PROJECT-BATTLE-ENTRYPOINT-REGISTRY-DESIGN (v54 Track B)."""
from __future__ import annotations
import os, sys, json, hashlib

ROOT = '/app'
REG = os.path.join(ROOT, 'data/design/release_acceleration/battle_entrypoint_registry_design_v1.json')
MR = os.path.join(ROOT, 'data/design/release_acceleration/material_raid_battle_entrypoint_registration_preview_v1.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/battle_entrypoint_registry_design_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v54_MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN'
BATTLE_ENGINE_MD5 = '151ca35ad3bc35f0a6209cb3744ed440'
COMBAT_MD5 = 'fc792a05b2ada6e677d80400732ae5c3'
STORY_MD5 = '8520627b4e63f86821d73d8d3880bac3'

FAILS = []
def fail(m): FAILS.append(m)

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

if not os.path.exists(REG): fail(f'missing registry: {REG}')
else:
    r = json.load(open(REG))
    if r.get('public_sync_tag') != TAG: fail('registry public_sync_tag mismatch')
    if r.get('mode') != 'design_only': fail('registry mode != design_only')
    if r.get('runtime_wired') is not False: fail('registry runtime_wired != false')
    if r.get('db_writes') != 0: fail('registry db_writes != 0')
    entries = {e.get('mode'): e for e in (r.get('entries') or [])}
    for mode in ('material_raid', 'guild_war', 'story', 'boss'):
        if mode not in entries: fail(f'registry missing mode {mode}')
    mr = entries.get('material_raid') or {}
    if mr.get('frontend_entry_route') != '/material-raid-alpha': fail('material_raid frontend_entry_route mismatch')
    if mr.get('visual_preview_route') != '/material-raid-visual-preview': fail('material_raid visual_preview_route mismatch')
    if mr.get('reward_preview_route') != '/material-raid-reward-preview': fail('material_raid reward_preview_route mismatch')
    if mr.get('visual_battle_required') is not True: fail('material_raid visual_battle_required != true')
    if mr.get('auto_resolve_allowed') is not False: fail('material_raid auto_resolve_allowed != false')
    if mr.get('reward_claim_enabled') is not False: fail('material_raid reward_claim_enabled != false')
    if mr.get('db_writes') != 0: fail('material_raid db_writes != 0')
    gw = entries.get('guild_war') or {}
    if gw.get('auto_resolve_allowed') is not True: fail('guild_war auto_resolve_allowed != true')
    if gw.get('replay_link_required') is not True: fail('guild_war replay_link_required != true')

if not os.path.exists(MR): fail(f'missing material_raid registration: {MR}')
else:
    rr = json.load(open(MR))
    if rr.get('public_sync_tag') != TAG: fail('material_raid registration public_sync_tag mismatch')
    reg = rr.get('registration') or {}
    for k, v in (
        ('mode','material_raid'),
        ('frontend_entry_route','/material-raid-alpha'),
        ('visual_preview_route','/material-raid-visual-preview'),
        ('reward_preview_route','/material-raid-reward-preview'),
        ('visual_battle_required',True),
        ('auto_resolve_allowed',False),
        ('reward_claim_enabled',False),
        ('battle_engine_runtime_used',False),
        ('result_authoritative',False),
        ('db_writes',0),
    ):
        if reg.get(k) != v: fail(f'material_raid registration {k} != {v}')
    if rr.get('loop_closed') is not True: fail('loop_closed != true')
    if rr.get('loop_steps_count') != 5: fail('loop_steps_count != 5')

# MD5 invariants: battle_engine.py / combat.tsx / story.tsx unchanged
if md5(os.path.join(ROOT,'backend/battle_engine.py')) != BATTLE_ENGINE_MD5:
    fail('battle_engine.py MD5 drift')
if md5(os.path.join(ROOT,'frontend/app/combat.tsx')) != COMBAT_MD5:
    fail('combat.tsx MD5 drift')
if md5(os.path.join(ROOT,'frontend/app/story.tsx')) != STORY_MD5:
    fail('story.tsx MD5 drift')

if not os.path.exists(MARKER): fail('missing marker')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('marker_version','battle_entrypoint_registry_design_marker_v1'),
        ('track','B'),
        ('runtime_wired',False),
        ('battle_engine_changed',False),
        ('combat_tsx_changed',False),
        ('story_tsx_changed',False),
        ('battle_simulate_endpoint_changed',False),
        ('story_battle_endpoint_changed',False),
        ('db_writes',0),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-BATTLE-ENTRYPOINT-REGISTRY-DESIGN validator')
    sys.exit(1)
print('[PASS] PROJECT-BATTLE-ENTRYPOINT-REGISTRY-DESIGN validator')
sys.exit(0)
