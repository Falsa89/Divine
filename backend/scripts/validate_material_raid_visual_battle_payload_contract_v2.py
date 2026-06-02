#!/usr/bin/env python3
"""Validator: PROJECT-MATERIAL-RAID-VISUAL-BATTLE-PAYLOAD-CONTRACT-v2 (v52 Track A)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/release_acceleration/material_raid_visual_battle_payload_contract_v2.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/material_raid_visual_battle_payload_contract_v2_marker.json')
ROUTE = os.path.join(ROOT, 'backend/routes/material_raid_preview.py')

REQUIRED_PAYLOAD_FIELDS = {
    'mode', 'track_id', 'stage_id', 'recommended_power', 'team_power',
    'enemy_family_preview', 'battle_seed_preview', 'battle_visual_required',
    'auto_resolve_allowed', 'result_authoritative', 'reward_claim_enabled',
    'materials_granted', 'db_writes',
}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    for k, v in (
        ('contract_version', 'material_raid_visual_battle_payload_contract_v2'),
        ('source_endpoint', 'POST /api/material-raid/alpha-battle-preview'),
        ('target_frontend_route', '/material-raid-visual-preview'),
        ('mode', 'material_raid'),
        ('visual_battle_required', True),
        ('auto_resolve_allowed', False),
        ('guild_war_exception', False),
        ('battle_engine_runtime_used', False),
        ('battle_engine_py_changed', False),
        ('db_writes', 0),
        ('real_db_writes', 0),
        ('reward_grant_enabled', False),
        ('reward_claim_enabled', False),
        ('materials_granted', False),
        ('result_authoritative', False),
        ('alpha_preview_only', True),
    ):
        if d.get(k) != v: fail(f'design {k} != {v} (got {d.get(k)})')
    fields = set(d.get('required_payload_fields') or [])
    miss = REQUIRED_PAYLOAD_FIELDS - fields
    if miss: fail(f'design required_payload_fields missing: {sorted(miss)}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('contract_version', 'material_raid_visual_battle_payload_contract_v2'),
        ('track', 'A'),
        ('source_endpoint', 'POST /api/material-raid/alpha-battle-preview'),
        ('target_frontend_route', '/material-raid-visual-preview'),
        ('visual_battle_required', True),
        ('auto_resolve_allowed', False),
        ('battle_engine_runtime_used', False),
        ('battle_engine_py_changed', False),
        ('result_authoritative', False),
        ('reward_grant_enabled', False),
        ('materials_granted', False),
        ('db_writes', 0),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v52_MEGA_RELEASE_ACCELERATION_2_VISUAL_BATTLE_RUNNER_WIRING_FOR_MATERIAL_RAID_ALPHA'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

# Verify backend route actually emits the v2 contract fields
if not os.path.exists(ROUTE): fail(f'missing route: {ROUTE}')
else:
    src = open(ROUTE).read()
    for n in (
        '"result_authoritative": False',
        '"alpha_preview_only": True',
        '"battle_engine_runtime_used": False',
        '"reward_grant_enabled": False',
        '"target_frontend_route": "/material-raid-visual-preview"',
        '"background_hint"',
        '"music_hint"',
        '"tutorial_hint"',
        '"reward_preview_hint"',
    ):
        if n not in src: fail(f'route missing v2 contract field: {n}')
    # Sanity: route still does NOT import battle_engine, motor, pymongo, redis.
    for forb in ('import pymongo', 'from pymongo', 'import motor', 'from motor',
                 'import redis', 'from redis',
                 'from backend.battle_engine', 'import battle_engine', 'battle_engine.', 'battle_engine('):
        if forb in src: fail(f'route forbidden token present: {forb}')

# Runtime smoke: with flag ON, response must include v2 contract fields.
import os as _os
_os.environ['MATERIAL_RAID_PLAYABLE_ALPHA_SLICE_ENABLED'] = 'true'
_os.environ['MATERIAL_RAID_RUNTIME_PREVIEW_ENABLED'] = 'true'
sys.path.insert(0, os.path.join(ROOT, 'backend'))
try:
    from fastapi.testclient import TestClient
    from fastapi import FastAPI
    from routes.material_raid_preview import router
    app = FastAPI(); app.include_router(router)
    c = TestClient(app)
    r = c.post('/api/material-raid/alpha-battle-preview', json={
        'track_id': 'gear_material_raid', 'stage_id': 'III', 'team_power': 50000,
    })
    if r.status_code != 200: fail(f'flag ON smoke: status={r.status_code}')
    j = r.json()
    for k, v in (
        ('status', 'alpha_battle_preview_ready'),
        ('result_authoritative', False),
        ('alpha_preview_only', True),
        ('battle_engine_runtime_used', False),
        ('reward_grant_enabled', False),
        ('reward_claim_enabled', False),
        ('materials_granted', False),
        ('db_writes', 0),
        ('target_frontend_route', '/material-raid-visual-preview'),
    ):
        if j.get(k) != v: fail(f'smoke response {k} != {v} (got {j.get(k)})')
    for k in ('background_hint', 'music_hint', 'tutorial_hint', 'reward_preview_hint',
              'battle_seed_preview', 'visual_battle_payload_preview'):
        if k not in j: fail(f'smoke response missing field: {k}')
    vbp = j.get('visual_battle_payload_preview') or {}
    if vbp.get('battle_visual_required') is not True: fail('smoke vbp.battle_visual_required != True')
    if vbp.get('auto_resolve_allowed') is not False: fail('smoke vbp.auto_resolve_allowed != False')
except Exception as e:
    fail(f'smoke error: {e}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MATERIAL-RAID-VISUAL-BATTLE-PAYLOAD-CONTRACT-v2 validator')
    sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-VISUAL-BATTLE-PAYLOAD-CONTRACT-v2 validator')
sys.exit(0)
