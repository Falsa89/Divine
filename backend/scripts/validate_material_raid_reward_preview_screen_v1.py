#!/usr/bin/env python3
"""Validator: PROJECT-MATERIAL-RAID-REWARD-PREVIEW-SCREEN (v53 Track B)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
SCREEN = os.path.join(ROOT, 'frontend/app/material-raid-reward-preview.tsx')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/material_raid_reward_preview_screen_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(SCREEN): fail(f'missing screen: {SCREEN}')
else:
    s = open(SCREEN).read()
    for needle in (
        'export default function MaterialRaidRewardPreviewScreen',
        'useLocalSearchParams',
        'useRouter',
        'track_id', 'stage_id', 'battle_seed_preview',
        'battle_result_preview', 'mvp_hero_id',
        'Reward Summary Preview',
        'Nessun materiale verr',
        'Riscossione live disabilitata',
        '/api/material-raid/alpha-reward-summary-preview',
    ):
        if needle not in s: fail(f'screen missing needle: {needle}')
    # Forbidden in this screen — active patterns only.
    for forb in (
        'import pymongo', 'from pymongo',
        'import motor', 'from motor',
        'import redis', 'from redis',
        'AsyncIOMotorClient(', 'MongoClient(',
        "fetch('/api/battle/simulate", 'fetch("/api/battle/simulate',
        "fetch('/api/story/battle", 'fetch("/api/story/battle',
    ):
        if forb in s: fail(f'screen forbidden active token: {forb}')
    # No claim live UI label.
    for bad in ('Claim live', 'Riscuoti subito', 'Riscatta reward'):
        if bad in s: fail(f'screen forbidden claim label: {bad}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('track', 'B'),
        ('frontend_route', '/material-raid-reward-preview'),
        ('frontend_screen_path', 'frontend/app/material-raid-reward-preview.tsx'),
        ('deeplink_only', True),
        ('home_menu_wiring', False),
        ('handles_missing_query_params_without_crash', True),
        ('safe_fallback_when_backend_off', True),
        ('calls_backend_endpoint', 'POST /api/material-raid/alpha-reward-summary-preview'),
        ('calls_battle_engine', False),
        ('calls_battle_simulate', False),
        ('calls_story_battle', False),
        ('claim_button_present', False),
        ('inventory_mutation', False),
        ('materials_granted', False),
        ('db_writes', 0),
        ('text_language', 'it'),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v53_MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_ALPHA_LOOP_CLOSURE'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')
    qp = set(m.get('accepts_query_params') or [])
    if not {'track_id','stage_id','battle_seed_preview','battle_result_preview','mvp_hero_id'}.issubset(qp):
        fail(f'marker accepts_query_params missing keys: {sorted(qp)}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MATERIAL-RAID-REWARD-PREVIEW-SCREEN validator')
    sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-REWARD-PREVIEW-SCREEN validator')
sys.exit(0)
