#!/usr/bin/env python3
"""Validator: PROJECT-GENERIC-ROUTER-TRAINING-DETAIL (v56 Track C)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
SCREEN = os.path.join(ROOT, 'frontend/app/visual-battle-preview-router.tsx')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/generic_router_training_detail_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v56_MEGA_RELEASE_ACCELERATION_5_TRAINING_VISUAL_PREVIEW_LOCAL_DUMMY_SEED'

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(SCREEN): fail('missing screen')
else:
    s = open(SCREEN).read()
    # Existing v55 invariants preserved
    for needle in (
        'export default function VisualBattlePreviewRouterScreen',
        'useLocalSearchParams',
        'Visual Battle Preview Router',
        'Preview visuale non autoritativa',
        'Nessun reward verr',
        'Routing preview only',
    ):
        if needle not in s: fail(f'screen missing needle (v55 invariant): {needle}')
    # New v56 training detail block
    for needle in (
        "mode === 'training'",
        'Training Dummy Seed Details',
        'local_dummy_seed_wired_v56',
    ):
        if needle not in s: fail(f'screen missing v56 training needle: {needle}')
    # Forbidden: no backend fetch / no claim
    for forb in (
        'import pymongo','from pymongo','import motor','from motor','import redis','from redis',
        "fetch('/api/battle/simulate",'fetch("/api/battle/simulate',
        "fetch('/api/story/battle",'fetch("/api/story/battle',
        "fetch('/api/",'fetch("/api/',
    ):
        if forb in s: fail(f'screen forbidden token: {forb}')
    for bad in ('Claim live', 'Riscuoti subito', 'Riscatta reward'):
        if bad in s: fail(f'screen forbidden claim label: {bad}')

if not os.path.exists(MARKER): fail('missing marker')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('marker_version','generic_router_training_detail_marker_v1'),
        ('track','C'),
        ('public_sync_tag',TAG),
        ('screen_path','frontend/app/visual-battle-preview-router.tsx'),
        ('screen_route','/visual-battle-preview-router'),
        ('deeplink_only',True),
        ('home_menu_mandatory_routing',False),
        ('calls_backend',False),
        ('calls_battle_engine',False),
        ('claim_button_present',False),
        ('db_writes',0),
        ('training_detail_block_added',True),
        ('shows_local_dummy_seed_wired_v56',True),
        ('material_raid_behavior_unchanged',True),
        ('handles_missing_params_without_crash',True),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-GENERIC-ROUTER-TRAINING-DETAIL validator')
    sys.exit(1)
print('[PASS] PROJECT-GENERIC-ROUTER-TRAINING-DETAIL validator')
sys.exit(0)
