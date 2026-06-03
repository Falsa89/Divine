#!/usr/bin/env python3
"""Validator: PROJECT-TRAINING-VISUAL-PREVIEW-LOCAL-TIMELINE (v56 Track B)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
SCREEN = os.path.join(ROOT, 'frontend/app/training-visual-preview.tsx')
SCHEMA = os.path.join(ROOT, 'data/design/release_acceleration/local_visual_preview_timeline_schema_v1.json')
SCHEMA_MARKER = os.path.join(ROOT, 'data/design/release_acceleration/local_visual_preview_timeline_schema_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v56_MEGA_RELEASE_ACCELERATION_5_TRAINING_VISUAL_PREVIEW_LOCAL_DUMMY_SEED'

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(SCREEN): fail('missing screen')
else:
    s = open(SCREEN).read()
    for needle in (
        'export default function TrainingVisualPreviewScreen',
        "training-alpha-v56",
        'buildLocalTimeline',
        'TimelineStep',
        'step_index',
        'actor_side',
        'actor_label',
        'action_key',
        'target_label',
        'floating_text_preview',
        'hp_delta_preview',
        'pose_hint',
        'vfx_hint',
        'duration_ms',
        'Preview visuale locale non autoritativa',
        'Nessun reward verr',
        'local_dummy_seed_wired_v56',
        'Step successivo',
        'Reset',
        'Apri Visual Battle Preview Router',
        'clearTimeout(timerRef.current)',
    ):
        if needle not in s: fail(f'screen missing needle: {needle}')
    # Forbidden imports / tokens
    for forb in (
        'import pymongo','from pymongo','import motor','from motor','import redis','from redis',
        'AsyncIOMotorClient(','MongoClient(',
        "fetch('/api/battle/simulate",'fetch("/api/battle/simulate',
        "fetch('/api/story/battle",'fetch("/api/story/battle',
        "fetch('/api/",'fetch("/api/',
        'react-native-reanimated', 'useSharedValue', 'withTiming(', 'withSpring(',
        'import Animated', 'from \'react-native-reanimated\'', 'from "react-native-reanimated"',
        "from '../combat", 'from "../combat',
        "from './combat", 'from "./combat',
    ):
        if forb in s: fail(f'screen forbidden token: {forb}')
    for bad in ('Claim live', 'Riscuoti subito', 'Riscatta reward'):
        if bad in s: fail(f'screen forbidden claim label: {bad}')

if not os.path.exists(SCHEMA): fail('missing schema')
else:
    sc = json.load(open(SCHEMA))
    if sc.get('public_sync_tag') != TAG: fail('schema public_sync_tag mismatch')
    if sc.get('deterministic_from_seed') is not True: fail('schema deterministic_from_seed != true')
    req = set(sc.get('required_step_fields') or [])
    expected = {'step_index','actor_side','actor_label','action_key','target_label','floating_text_preview','hp_delta_preview','pose_hint','vfx_hint','duration_ms'}
    if req != expected: fail(f'schema required_step_fields mismatch: {sorted(req)}')
    if set(sc.get('actor_sides_allowed') or []) != {'team','enemy'}: fail('schema actor_sides_allowed mismatch')

if not os.path.exists(SCHEMA_MARKER): fail('missing schema marker')
else:
    sm = json.load(open(SCHEMA_MARKER))
    for k, v in (
        ('marker_version','local_visual_preview_timeline_schema_marker_v1'),
        ('track','A'),
        ('public_sync_tag',TAG),
        ('mode','design_schema'),
        ('deterministic_from_seed',True),
        ('db_writes',0),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if sm.get(k) != v: fail(f'schema marker {k} != {v} (got {sm.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-TRAINING-VISUAL-PREVIEW-LOCAL-TIMELINE validator')
    sys.exit(1)
print('[PASS] PROJECT-TRAINING-VISUAL-PREVIEW-LOCAL-TIMELINE validator')
sys.exit(0)
