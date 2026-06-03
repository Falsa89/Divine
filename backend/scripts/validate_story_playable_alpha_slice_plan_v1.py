#!/usr/bin/env python3
"""Validator: PROJECT-STORY-PLAYABLE-ALPHA-SLICE-PLAN (v54 Track F)."""
from __future__ import annotations
import os, sys, json, hashlib

ROOT = '/app'
PLAN = os.path.join(ROOT, 'data/design/release_acceleration/story_playable_alpha_slice_plan_v1.json')
DRAFT = os.path.join(ROOT, 'data/design/release_acceleration/story_visual_battle_transition_contract_draft_v1.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/story_playable_alpha_slice_plan_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v54_MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN'
STORY_MD5 = '8520627b4e63f86821d73d8d3880bac3'
BATTLE_ENGINE_MD5 = '151ca35ad3bc35f0a6209cb3744ed440'

FAILS = []
def fail(m): FAILS.append(m)

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

if not os.path.exists(PLAN): fail('missing plan')
else:
    p = json.load(open(PLAN))
    if p.get('public_sync_tag') != TAG: fail('plan public_sync_tag mismatch')
    if p.get('mode') != 'design_only': fail('plan mode != design_only')
    for k, v in (
        ('runtime_wired',False),
        ('story_tsx_changed',False),
        ('story_battle_endpoint_changed',False),
        ('battle_engine_changed',False),
        ('reward_live',False),
        ('db_writes',0),
    ):
        if p.get(k) != v: fail(f'plan {k} != {v}')
    if not isinstance(p.get('stages'), list) or len(p.get('stages')) < 3:
        fail('plan stages must be list with >=3 entries')
    tr = p.get('alpha_visual_battle_transition') or {}
    if tr.get('required') is not True: fail('plan transition.required != true')

if not os.path.exists(DRAFT): fail('missing draft')
else:
    d = json.load(open(DRAFT))
    if d.get('public_sync_tag') != TAG: fail('draft public_sync_tag mismatch')
    if d.get('mode') != 'design_only_draft': fail('draft mode != design_only_draft')
    if d.get('status') != 'draft': fail('draft status != draft')
    if d.get('runtime_wired') is not False: fail('draft runtime_wired != false')
    if d.get('db_writes') != 0: fail('draft db_writes != 0')
    forb = d.get('forbidden') or {}
    for k in ('story_tsx_modified','story_battle_endpoint_modified','battle_engine_modified','new_runtime_endpoint_created_in_v54'):
        if forb.get(k) is not False: fail(f'draft forbidden.{k} != false')

# MD5: story.tsx and battle_engine.py UNCHANGED
if md5(os.path.join(ROOT, 'frontend/app/story.tsx')) != STORY_MD5: fail('story.tsx MD5 drift')
if md5(os.path.join(ROOT, 'backend/battle_engine.py')) != BATTLE_ENGINE_MD5: fail('battle_engine.py MD5 drift')

if not os.path.exists(MARKER): fail('missing marker')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('marker_version','story_playable_alpha_slice_plan_marker_v1'),
        ('track','F'),
        ('public_sync_tag',TAG),
        ('mode','design_only'),
        ('runtime_wired',False),
        ('story_tsx_changed',False),
        ('story_battle_endpoint_changed',False),
        ('battle_engine_changed',False),
        ('reward_live',False),
        ('db_writes',0),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-STORY-PLAYABLE-ALPHA-SLICE-PLAN validator')
    sys.exit(1)
print('[PASS] PROJECT-STORY-PLAYABLE-ALPHA-SLICE-PLAN validator')
sys.exit(0)
