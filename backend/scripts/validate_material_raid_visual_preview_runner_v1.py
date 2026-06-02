#!/usr/bin/env python3
"""Validator: PROJECT-MATERIAL-RAID-VISUAL-PREVIEW-RUNNER (v52 Track B)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
SCREEN = os.path.join(ROOT, 'frontend/app/material-raid-visual-preview.tsx')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/material_raid_visual_preview_runner_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(SCREEN): fail(f'missing screen: {SCREEN}')
else:
    s = open(SCREEN).read()
    for needle in (
        'export default function MaterialRaidVisualPreviewScreen',
        'useLocalSearchParams',
        'useRouter',
        'track_id', 'stage_id', 'team_power',
        'recommended_power', 'enemy_family_preview', 'battle_seed_preview',
        'Preview visuale non autoritativa',
        'Nessun reward verr',
    ):
        if needle not in s: fail(f'screen missing needle: {needle}')
    # Forbidden in this screen — active patterns only.
    # String mentions in comments/UI disclaimer (e.g. "NON chiama battle_engine.py")
    # are explicit user-facing reassurance, NOT active code paths.
    for forb in (
        'import pymongo', 'from pymongo',
        'import motor', 'from motor',
        'import redis', 'from redis',
        'AsyncIOMotorClient(', 'MongoClient(',
        "fetch('/api/battle/simulate", 'fetch("/api/battle/simulate',
        "fetch('/api/story/battle", 'fetch("/api/story/battle',
        "from 'battle_engine", 'from "battle_engine',
    ):
        if forb in s: fail(f'screen forbidden active token: {forb}')
    # No fetch to backend (this is a pure visualization).
    if 'fetch(' in s: fail('screen must not call fetch (no backend dependency at runtime)')
    # No claim button label.
    for bad in ('Claim live', 'claim_button', 'Claim reward'):
        if bad in s: fail(f'screen must not contain claim ui: {bad}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('track', 'B'),
        ('frontend_route', '/material-raid-visual-preview'),
        ('frontend_screen_path', 'frontend/app/material-raid-visual-preview.tsx'),
        ('deeplink_only', True),
        ('home_menu_wiring', False),
        ('handles_missing_query_params_without_crash', True),
        ('warning_non_authoritative_visible', True),
        ('warning_no_reward_visible', True),
        ('claim_button_present', False),
        ('calls_battle_engine', False),
        ('calls_battle_simulate', False),
        ('calls_story_battle', False),
        ('db_writes', 0),
        ('combat_tsx_changed', False),
        ('text_language', 'it'),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v52_MEGA_RELEASE_ACCELERATION_2_VISUAL_BATTLE_RUNNER_WIRING_FOR_MATERIAL_RAID_ALPHA'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')
    qp = set(m.get('accepts_query_params') or [])
    if not {'track_id','stage_id','team_power','recommended_power','enemy_family_preview','battle_seed_preview'}.issubset(qp):
        fail(f'marker accepts_query_params missing keys: {sorted(qp)}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MATERIAL-RAID-VISUAL-PREVIEW-RUNNER validator')
    sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-VISUAL-PREVIEW-RUNNER validator')
sys.exit(0)
