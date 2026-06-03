#!/usr/bin/env python3
"""Validator: PROJECT-MULTI-MODE-VISUAL-BATTLE-PREVIEW-CONTRACTS (v55 Track D)."""
from __future__ import annotations
import os, sys, json, hashlib

ROOT = '/app'
STORY = os.path.join(ROOT, 'data/design/release_acceleration/story_visual_battle_preview_entrypoint_contract_v1.json')
MULTI = os.path.join(ROOT, 'data/design/release_acceleration/multi_mode_visual_battle_preview_entrypoint_contract_v1.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/multi_mode_visual_battle_preview_contracts_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v55_MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW'
STORY_MD5 = '8520627b4e63f86821d73d8d3880bac3'
BATTLE_ENGINE_MD5 = '151ca35ad3bc35f0a6209cb3744ed440'
COMBAT_MD5 = 'fc792a05b2ada6e677d80400732ae5c3'

FAILS = []
def fail(m): FAILS.append(m)

def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()

if not os.path.exists(STORY): fail('missing story contract')
else:
    s = json.load(open(STORY))
    if s.get('public_sync_tag') != TAG: fail('story contract public_sync_tag mismatch')
    if s.get('mode') != 'design_only': fail('story mode != design_only')
    for k, v in (
        ('runtime_wired',False),
        ('story_tsx_changed',False),
        ('story_battle_endpoint_changed',False),
        ('battle_engine_changed',False),
        ('combat_tsx_changed',False),
        ('db_writes',0),
    ):
        if s.get(k) != v: fail(f'story {k} != {v}')
    fp = s.get('future_payload_minimum') or {}
    for k in ('mode','chapter_id','stage_id','battle_seed_preview','team_power','recommended_power','enemy_family_preview','target_frontend_route'):
        if k not in fp: fail(f'story future_payload_minimum missing {k}')
    if fp.get('result_authoritative') is not False: fail('story future_payload result_authoritative != false')
    if fp.get('reward_claim_enabled') is not False: fail('story future_payload reward_claim_enabled != false')
    if fp.get('battle_engine_runtime_used') is not False: fail('story future_payload battle_engine_runtime_used != false')
    forb = s.get('forbidden') or {}
    for k in ('story_tsx_modified','story_battle_endpoint_modified','battle_simulate_endpoint_modified','new_runtime_endpoint_in_v55'):
        if forb.get(k) is not False: fail(f'story forbidden.{k} != false')

if not os.path.exists(MULTI): fail('missing multi contract')
else:
    mu = json.load(open(MULTI))
    if mu.get('public_sync_tag') != TAG: fail('multi public_sync_tag mismatch')
    if mu.get('mode') != 'design_only': fail('multi mode != design_only')
    modes = mu.get('modes') or {}
    for mode in ('boss','tower','event','arena'):
        if mode not in modes: fail(f'multi missing mode {mode}')
        e = modes.get(mode, {})
        if e.get('runtime_wiring_deferred') is not True: fail(f'multi {mode} runtime_wiring_deferred != true')
        fp = e.get('future_payload_minimum') or {}
        if fp.get('mode') != mode: fail(f'multi {mode} future_payload_minimum.mode mismatch')
        if fp.get('result_authoritative') is not False: fail(f'multi {mode} result_authoritative != false')
        if fp.get('reward_claim_enabled') is not False: fail(f'multi {mode} reward_claim_enabled != false')
        if fp.get('battle_engine_runtime_used') is not False: fail(f'multi {mode} battle_engine_runtime_used != false')
    forb = mu.get('forbidden') or {}
    for k in ('battle_engine_modified','combat_tsx_modified','story_tsx_modified','battle_simulate_endpoint_modified','story_battle_endpoint_modified','new_runtime_endpoint_in_v55'):
        if forb.get(k) is not False: fail(f'multi forbidden.{k} != false')

# MD5
if md5(os.path.join(ROOT,'frontend/app/story.tsx')) != STORY_MD5: fail('story.tsx MD5 drift')
if md5(os.path.join(ROOT,'backend/battle_engine.py')) != BATTLE_ENGINE_MD5: fail('battle_engine.py MD5 drift')
if md5(os.path.join(ROOT,'frontend/app/combat.tsx')) != COMBAT_MD5: fail('combat.tsx MD5 drift')

if not os.path.exists(MARKER): fail('missing marker')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('marker_version','multi_mode_visual_battle_preview_contracts_marker_v1'),
        ('track','D'),
        ('public_sync_tag',TAG),
        ('mode','design_only'),
        ('runtime_wired',False),
        ('story_tsx_changed',False),
        ('story_battle_endpoint_changed',False),
        ('battle_engine_changed',False),
        ('combat_tsx_changed',False),
        ('new_runtime_endpoint_in_v55',False),
        ('db_writes',0),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MULTI-MODE-VISUAL-BATTLE-PREVIEW-CONTRACTS validator')
    sys.exit(1)
print('[PASS] PROJECT-MULTI-MODE-VISUAL-BATTLE-PREVIEW-CONTRACTS validator')
sys.exit(0)
