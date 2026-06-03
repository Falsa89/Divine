#!/usr/bin/env python3
"""Validator: PROJECT-BOSS-VISUAL-PREVIEW-SCREEN (v57 Track B)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
SCREEN = os.path.join(ROOT, 'frontend/app/boss-visual-preview.tsx')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/boss_visual_preview_screen_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v57_MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE'

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(SCREEN): fail(f'missing screen: {SCREEN}')
else:
    s = open(SCREEN).read()
    for needle in (
        'export default function BossVisualPreviewScreen',
        'useLocalSearchParams',
        'useRouter',
        'Boss Visual Preview',
        'Boss Card',
        'Preview visuale boss non autoritativa',
        'Nessun reward verr',
        'boss_family_id',
        'boss_display_name',
        'boss_phase_preview',
        'battle_seed_preview',
        'team_power',
        'recommended_power',
        'training_boss_preview',
        'Boss Preview',
        'phase_1',
        'boss-alpha-v57',
        'Reset preview',
        'Apri Visual Battle Preview Router',
    ):
        if needle not in s: fail(f'screen missing needle: {needle}')
    for forb in (
        'import pymongo','from pymongo','import motor','from motor','import redis','from redis',
        'AsyncIOMotorClient(','MongoClient(',
        "fetch('/api/battle/simulate",'fetch("/api/battle/simulate',
        "fetch('/api/story/battle",'fetch("/api/story/battle',
        "fetch('/api/",'fetch("/api/',
        'react-native-reanimated', 'useSharedValue', 'withTiming(', 'withSpring(',
        "from '../combat", 'from "../combat',
        "from './combat", 'from "./combat',
    ):
        if forb in s: fail(f'screen forbidden token: {forb}')
    for bad in ('Claim live', 'Riscuoti subito', 'Riscatta reward'):
        if bad in s: fail(f'screen forbidden claim label: {bad}')

if not os.path.exists(MARKER): fail('missing marker')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('marker_version','boss_visual_preview_screen_marker_v1'),
        ('track','B'),
        ('public_sync_tag',TAG),
        ('screen_path','frontend/app/boss-visual-preview.tsx'),
        ('screen_route','/boss-visual-preview'),
        ('deeplink_only',True),
        ('static',True),
        ('calls_backend',False),
        ('calls_battle_engine',False),
        ('claim_button_present',False),
        ('reward_grant_enabled',False),
        ('home_menu_mandatory_routing',False),
        ('links_to_router_route','/visual-battle-preview-router'),
        ('handles_missing_query_params_without_crash',True),
        ('default_seed','boss-alpha-v57'),
        ('default_boss_family_id','training_boss_preview'),
        ('db_writes',0),
        ('text_language','it'),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')
    qp = set(m.get('accepts_query_params') or [])
    expected = {'boss_family_id','boss_display_name','boss_phase_preview','battle_seed_preview','team_power','recommended_power'}
    if qp != expected: fail(f'marker accepts_query_params mismatch: {sorted(qp)}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-BOSS-VISUAL-PREVIEW-SCREEN validator')
    sys.exit(1)
print('[PASS] PROJECT-BOSS-VISUAL-PREVIEW-SCREEN validator')
sys.exit(0)
