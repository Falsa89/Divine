#!/usr/bin/env python3
"""Validator: PROJECT-GENERIC-VISUAL-BATTLE-PREVIEW-ROUTER (v55 Track B)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
SCREEN = os.path.join(ROOT, 'frontend/app/visual-battle-preview-router.tsx')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/generic_visual_battle_preview_router_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v55_MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW'

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(SCREEN): fail(f'missing screen: {SCREEN}')
else:
    s = open(SCREEN).read()
    for needle in (
        'export default function VisualBattlePreviewRouterScreen',
        'useLocalSearchParams',
        'useRouter',
        'Visual Battle Preview Router',
        'Preview visuale non autoritativa',
        'Nessun reward verr',
        'Routing preview only',
        'mode', 'source_route', 'track_id', 'stage_id', 'chapter_id',
        'battle_seed_preview', 'team_power', 'recommended_power', 'enemy_family_preview',
    ):
        if needle not in s: fail(f'screen missing needle: {needle}')
    for forb in (
        'import pymongo','from pymongo','import motor','from motor','import redis','from redis',
        'AsyncIOMotorClient(','MongoClient(',
        "fetch('/api/battle/simulate", 'fetch("/api/battle/simulate',
        "fetch('/api/story/battle", 'fetch("/api/story/battle',
    ):
        if forb in s: fail(f'screen forbidden token: {forb}')
    # No claim CTAs / no live grant labels
    for bad in ('Claim live', 'Riscuoti subito', 'Riscatta reward', 'Riscossione live attiva'):
        if bad in s: fail(f'screen forbidden claim label: {bad}')

if not os.path.exists(MARKER): fail('missing marker')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('marker_version','generic_visual_battle_preview_router_marker_v1'),
        ('track','B'),
        ('public_sync_tag',TAG),
        ('screen_path','frontend/app/visual-battle-preview-router.tsx'),
        ('screen_route','/visual-battle-preview-router'),
        ('deeplink_only',True),
        ('home_menu_mandatory_routing',False),
        ('calls_backend',False),
        ('calls_battle_engine',False),
        ('calls_battle_simulate',False),
        ('calls_story_battle',False),
        ('claim_button_present',False),
        ('reward_grant_enabled',False),
        ('reward_claim_enabled',False),
        ('materials_granted',False),
        ('inventory_mutation',False),
        ('db_writes',0),
        ('text_language','it'),
        ('handles_missing_query_params_without_crash',True),
        ('safe_fallback_when_backend_off',True),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')
    qp = set(m.get('accepts_query_params') or [])
    expected = {'mode','source_route','track_id','stage_id','chapter_id','battle_seed_preview','team_power','recommended_power','enemy_family_preview'}
    if qp != expected: fail(f'marker accepts_query_params mismatch: {sorted(qp)}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-GENERIC-VISUAL-BATTLE-PREVIEW-ROUTER validator')
    sys.exit(1)
print('[PASS] PROJECT-GENERIC-VISUAL-BATTLE-PREVIEW-ROUTER validator')
sys.exit(0)
