#!/usr/bin/env python3
"""Validator: PROJECT-TRAINING-VISUAL-PREVIEW-DEEPLINK (v55 Track C)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
SCREEN = os.path.join(ROOT, 'frontend/app/training-visual-preview.tsx')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/training_visual_preview_deeplink_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v55_MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW'

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(SCREEN): fail(f'missing screen: {SCREEN}')
else:
    s = open(SCREEN).read()
    for needle in (
        'export default function TrainingVisualPreviewScreen',
        'useRouter',
        'Training Visual Preview',
        'Preview visuale non autoritativa',
        'Nessun reward verr',
        '/visual-battle-preview-router?mode=training',
        'source_route=training_visual_preview',
        'battle_seed_preview=training-alpha-v55',
        'safe_sandbox',
    ):
        if needle not in s: fail(f'screen missing needle: {needle}')
    for forb in (
        'import pymongo','from pymongo','import motor','from motor','import redis','from redis',
        'AsyncIOMotorClient(','MongoClient(',
        "fetch('/api/battle/simulate", 'fetch("/api/battle/simulate',
        "fetch('/api/story/battle", 'fetch("/api/story/battle',
        "fetch('/api/", 'fetch("/api/',
    ):
        if forb in s: fail(f'screen forbidden token: {forb}')
    for bad in ('Claim live', 'Riscuoti subito', 'Riscatta reward'):
        if bad in s: fail(f'screen forbidden claim label: {bad}')

if not os.path.exists(MARKER): fail('missing marker')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('marker_version','training_visual_preview_deeplink_marker_v1'),
        ('track','C'),
        ('public_sync_tag',TAG),
        ('screen_path','frontend/app/training-visual-preview.tsx'),
        ('screen_route','/training-visual-preview'),
        ('deeplink_only',True),
        ('static',True),
        ('calls_backend',False),
        ('calls_battle_engine',False),
        ('claim_button_present',False),
        ('reward_grant_enabled',False),
        ('home_menu_mandatory_routing',False),
        ('safe_sandbox',True),
        ('links_to_router_route','/visual-battle-preview-router'),
        ('db_writes',0),
        ('text_language','it'),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-TRAINING-VISUAL-PREVIEW-DEEPLINK validator')
    sys.exit(1)
print('[PASS] PROJECT-TRAINING-VISUAL-PREVIEW-DEEPLINK validator')
sys.exit(0)
