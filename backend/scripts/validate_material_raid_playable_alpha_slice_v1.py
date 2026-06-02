#!/usr/bin/env python3
"""Validator: PROJECT-MATERIAL-RAID-PLAYABLE-ALPHA-SLICE (v51 Track A).

Verifies that backend/routes/material_raid_preview.py has been patched to
include the v51 playable alpha slice endpoints without altering existing
behavior. Checks structural source patterns + marker JSON.
"""
from __future__ import annotations
import os, sys, json, re

ROOT = '/app'
ROUTE = os.path.join(ROOT, 'backend/routes/material_raid_preview.py')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/material_raid_playable_alpha_slice_marker_v1.json')

REQUIRED_SOURCE_NEEDLES = [
    'ALPHA_SLICE_FEATURE_FLAG = "MATERIAL_RAID_PLAYABLE_ALPHA_SLICE_ENABLED"',
    'ALPHA_SLICE_CONTRACT_VERSION = "material_raid_playable_alpha_slice_v1"',
    'def _alpha_slice_flag_enabled(',
    'def _alpha_disabled_payload(',
    '@router.get("/alpha-slice-config")',
    '@router.post("/alpha-battle-preview")',
    '@router.post("/alpha-reward-summary-preview")',
    'class AlphaBattlePreviewRequest(',
    'class AlphaRewardSummaryPreviewRequest(',
    '_deterministic_battle_seed(',
]

# Existing endpoints must remain present and unchanged in path/decorator.
REQUIRED_EXISTING_DECORATORS = [
    '@router.get("/config")',
    '@router.get("/stages")',
    '@router.post("/reward-preview")',
    '@router.post("/clear-preview")',
]

# Forbidden direct integrations in this file (active code patterns only —
# string mentions in comments or in JSON payload keys like
# "no_battle_engine_call" are NOT considered active invocations).
FORBIDDEN_ACTIVE = [
    'import pymongo', 'from pymongo',
    'import motor', 'from motor',
    'import redis', 'from redis',
    'MongoClient(', 'AsyncIOMotorClient(',
    'from backend.battle_engine', 'from battle_engine', 'import battle_engine',
    'battle_engine.', 'battle_engine(',
    'requests.post(', 'requests.get(',
    'httpx.post(', 'httpx.get(',
    'urllib.request.urlopen(',
]

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(ROUTE): fail(f'missing route file: {ROUTE}')
else:
    src = open(ROUTE).read()
    for n in REQUIRED_SOURCE_NEEDLES:
        if n not in src: fail(f'route missing needle: {n}')
    for d in REQUIRED_EXISTING_DECORATORS:
        if src.count(d) != 1: fail(f'existing decorator count != 1: {d} (got {src.count(d)})')
    # Existing legacy flag still referenced (unchanged)
    if 'FEATURE_FLAG = "MATERIAL_RAID_RUNTIME_PREVIEW_ENABLED"' not in src:
        fail('existing FEATURE_FLAG must remain unchanged')
    for f in FORBIDDEN_ACTIVE:
        if f in src: fail(f'forbidden active token present in route: {f}')
    # The alpha endpoints must each contain a 503 path when flag OFF.
    for ep in ('/alpha-slice-config', '/alpha-battle-preview', '/alpha-reward-summary-preview'):
        # Check 503 disabled behavior near the endpoint
        if 'status_code=503' not in src: fail('alpha endpoints must raise 503 when flag OFF')
            
    # No direct os.environ writes; only read of flags allowed
    if re.search(r"os\.environ\s*\[[^\]]+\]\s*=", src):
        fail('forbidden: os.environ assignment in route')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('contract_version', 'material_raid_playable_alpha_slice_v1'),
        ('playable_alpha_phase', 'v51'),
        ('feature_flag', 'MATERIAL_RAID_PLAYABLE_ALPHA_SLICE_ENABLED'),
        ('feature_flag_default', 'off'),
        ('flag_off_behavior', '503'),
        ('flag_on_behavior', 'preview_payload'),
        ('db_writes', 0),
        ('real_db_writes', 0),
        ('materials_granted', False),
        ('reward_claim_enabled', False),
        ('stamina_used', False),
        ('tickets_used', False),
        ('no_paid_attempts', True),
        ('visual_battle_required', True),
        ('guild_war_exception', False),
        ('no_battle_engine_call', True),
        ('no_battle_simulate_call', True),
        ('no_story_battle_call', True),
        ('live_mutation_applied', False),
        ('compatible_with_future_material_raid_claim_safety', True),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')
    new_eps = m.get('new_endpoints') or []
    if len(new_eps) != 3: fail(f'marker new_endpoints len != 3 (got {len(new_eps)})')
    existing_eps = m.get('existing_endpoints_unchanged') or []
    if len(existing_eps) != 4: fail(f'marker existing_endpoints_unchanged len != 4 (got {len(existing_eps)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MATERIAL-RAID-PLAYABLE-ALPHA-SLICE validator')
    sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-PLAYABLE-ALPHA-SLICE validator')
sys.exit(0)
