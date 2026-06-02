#!/usr/bin/env python3
"""Validator: PROJECT-MATERIAL-RAID-POST-VISUAL-REWARD-SUMMARY-CONTRACT-v1 (v53 Track A)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/release_acceleration/material_raid_post_visual_reward_summary_contract_v1.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/material_raid_post_visual_reward_summary_contract_v1_marker.json')
ROUTE = os.path.join(ROOT, 'backend/routes/material_raid_preview.py')

REQUIRED_RESPONSE_FIELDS = {
    'status', 'track_id', 'stage_id', 'reward_preview',
    'materials_granted', 'inventory_mutation', 'claim_button_enabled',
    'claim_flow_state', 'db_writes', 'result_authoritative',
    'reward_claim_enabled', 'reward_grant_enabled',
    'compatible_with_future_material_raid_claim_safety',
    'next_allowed_action', 'source_visual_preview_supported',
}
REQUIRED_QUERY_PARAMS = {'track_id', 'stage_id', 'battle_seed_preview', 'battle_result_preview', 'mvp_hero_id'}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    for k, v in (
        ('contract_version', 'material_raid_post_visual_reward_summary_contract_v1'),
        ('source_frontend_route', '/material-raid-visual-preview'),
        ('target_frontend_route', '/material-raid-reward-preview'),
        ('backend_preview_endpoint', 'POST /api/material-raid/alpha-reward-summary-preview'),
        ('result_authoritative', False),
        ('reward_claim_enabled', False),
        ('reward_grant_enabled', False),
        ('claim_button_enabled', False),
        ('materials_granted', False),
        ('inventory_mutation', False),
        ('db_writes', 0),
        ('real_db_writes', 0),
        ('battle_engine_runtime_used', False),
        ('battle_engine_py_changed', False),
        ('compatible_with_future_material_raid_claim_safety', True),
    ):
        if d.get(k) != v: fail(f'design {k} != {v} (got {d.get(k)})')
    fields = set(d.get('required_backend_response_fields') or [])
    miss = REQUIRED_RESPONSE_FIELDS - fields
    if miss: fail(f'design required_backend_response_fields missing: {sorted(miss)}')
    qparams = set(d.get('required_query_params') or [])
    miss_q = REQUIRED_QUERY_PARAMS - qparams
    if miss_q: fail(f'design required_query_params missing: {sorted(miss_q)}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('contract_version', 'material_raid_post_visual_reward_summary_contract_v1'),
        ('track', 'A'),
        ('source_frontend_route', '/material-raid-visual-preview'),
        ('target_frontend_route', '/material-raid-reward-preview'),
        ('backend_preview_endpoint', 'POST /api/material-raid/alpha-reward-summary-preview'),
        ('result_authoritative', False),
        ('reward_claim_enabled', False),
        ('claim_button_enabled', False),
        ('materials_granted', False),
        ('inventory_mutation', False),
        ('db_writes', 0),
        ('compatible_with_future_material_raid_claim_safety', True),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v53_MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_ALPHA_LOOP_CLOSURE'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

# Check backend route includes v53 refinement fields in alpha-reward-summary-preview response
if not os.path.exists(ROUTE): fail(f'missing route: {ROUTE}')
else:
    src = open(ROUTE).read()
    for n in (
        '"source_visual_preview_supported": True',
        '"result_authoritative": False',
        '"reward_claim_enabled": False',
        '"reward_grant_enabled": False',
        '"battle_engine_runtime_used": False',
        '"next_allowed_action": "return_to_alpha_or_wait_for_staging_claim"',
        '"target_frontend_route": "/material-raid-reward-preview"',
    ):
        if n not in src: fail(f'route missing v53 contract field: {n}')
    for forb in ('import pymongo', 'from pymongo', 'import motor', 'from motor',
                 'import redis', 'from redis',
                 'from backend.battle_engine', 'import battle_engine',
                 'battle_engine.', 'battle_engine('):
        if forb in src: fail(f'route forbidden active token: {forb}')

# Runtime smoke ON: validate response contains v53 fields.
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
    r = c.post('/api/material-raid/alpha-reward-summary-preview', json={
        'track_id': 'gear_material_raid', 'stage_id': 'III',
        'battle_result_preview': 'victory_preview', 'mvp_hero_id': 'hero_001',
    })
    if r.status_code != 200: fail(f'smoke status != 200 (got {r.status_code})')
    j = r.json()
    for k, v in (
        ('status', 'post_battle_reward_summary_preview'),
        ('materials_granted', False),
        ('inventory_mutation', False),
        ('claim_button_enabled', False),
        ('db_writes', 0),
        ('result_authoritative', False),
        ('reward_claim_enabled', False),
        ('reward_grant_enabled', False),
        ('battle_engine_runtime_used', False),
        ('source_visual_preview_supported', True),
        ('next_allowed_action', 'return_to_alpha_or_wait_for_staging_claim'),
        ('target_frontend_route', '/material-raid-reward-preview'),
        ('compatible_with_future_material_raid_claim_safety', True),
    ):
        if j.get(k) != v: fail(f'smoke response {k} != {v} (got {j.get(k)})')
    if 'reward_preview' not in j: fail('smoke response missing reward_preview')
except Exception as e:
    fail(f'smoke error: {e}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MATERIAL-RAID-POST-VISUAL-REWARD-SUMMARY-CONTRACT-v1 validator')
    sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-POST-VISUAL-REWARD-SUMMARY-CONTRACT-v1 validator')
sys.exit(0)
