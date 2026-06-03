#!/usr/bin/env python3
"""Validator: PROJECT-TRAINING-VISUAL-PREVIEW-LOCAL-DUMMY-SEED-CONTRACT (v56 Track A)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
CONTRACT = os.path.join(ROOT, 'data/design/release_acceleration/training_visual_preview_local_dummy_seed_contract_v1.json')
DELTA = os.path.join(ROOT, 'data/design/release_acceleration/battle_entrypoint_registry_v2_training_delta_v56.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/training_visual_preview_local_dummy_seed_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v56_MEGA_RELEASE_ACCELERATION_5_TRAINING_VISUAL_PREVIEW_LOCAL_DUMMY_SEED'

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(CONTRACT): fail('missing contract')
else:
    c = json.load(open(CONTRACT))
    if c.get('public_sync_tag') != TAG: fail('contract public_sync_tag mismatch')
    for k, v in (
        ('mode_id','training'),
        ('previous_state','preview_shell_v55'),
        ('target_state','local_dummy_seed_wired_v56'),
        ('source_route','/training-visual-preview'),
        ('router_route','/visual-battle-preview-router'),
        ('seed','training-alpha-v56'),
        ('timeline_steps_min',5),
        ('timeline_steps_max',7),
        ('local_only',True),
        ('backend_used',False),
        ('battle_engine_runtime_used',False),
        ('result_authoritative',False),
        ('reward_claim_enabled',False),
        ('reward_grant_enabled',False),
        ('db_writes',0),
        ('no_inventory_mutation',True),
        ('no_wallet_mutation',True),
    ):
        if c.get(k) != v: fail(f'contract {k} != {v} (got {c.get(k)})')
    forb = c.get('forbidden') or {}
    for k in ('backend_fetch','battle_engine_runtime','battle_simulate_endpoint_used','story_battle_endpoint_used','reanimated_used','combat_tsx_imported'):
        if forb.get(k) is not False: fail(f'contract forbidden.{k} != false')

if not os.path.exists(DELTA): fail('missing delta')
else:
    d = json.load(open(DELTA))
    if d.get('public_sync_tag') != TAG: fail('delta public_sync_tag mismatch')
    if d.get('parent_registry') != 'data/design/release_acceleration/battle_entrypoint_registry_v2_preview.json':
        fail('delta parent_registry mismatch')
    if d.get('applies_to') != 'training': fail('delta applies_to != training')
    dl = d.get('delta') or {}
    if dl.get('previous_state') != 'preview_shell_v55': fail('delta previous_state mismatch')
    if dl.get('new_state') != 'local_dummy_seed_wired_v56': fail('delta new_state mismatch')
    if dl.get('seed') != 'training-alpha-v56': fail('delta seed mismatch')
    inv = d.get('preserved_invariants') or {}
    for k, v in (
        ('visual_battle_required',True),
        ('auto_resolve_allowed',False),
        ('result_authoritative',False),
        ('reward_claim_enabled',False),
        ('reward_grant_enabled',False),
        ('db_writes',0),
        ('battle_engine_runtime_used',False),
        ('safe_sandbox',True),
    ):
        if inv.get(k) != v: fail(f'delta preserved_invariants.{k} != {v}')
    other = d.get('other_modes_unchanged') or {}
    for mode in ('material_raid','story','boss','tower','event','arena','guild_war'):
        if mode not in other: fail(f'delta other_modes_unchanged missing {mode}')

if not os.path.exists(MARKER): fail('missing marker')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('marker_version','training_visual_preview_local_dummy_seed_marker_v1'),
        ('track','A'),
        ('public_sync_tag',TAG),
        ('mode_id','training'),
        ('previous_state','preview_shell_v55'),
        ('target_state','local_dummy_seed_wired_v56'),
        ('seed','training-alpha-v56'),
        ('timeline_steps_min',5),
        ('timeline_steps_max',7),
        ('local_only',True),
        ('backend_used',False),
        ('battle_engine_runtime_used',False),
        ('result_authoritative',False),
        ('reward_claim_enabled',False),
        ('reward_grant_enabled',False),
        ('db_writes',0),
        ('no_inventory_mutation',True),
        ('no_wallet_mutation',True),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-TRAINING-VISUAL-PREVIEW-LOCAL-DUMMY-SEED-CONTRACT validator')
    sys.exit(1)
print('[PASS] PROJECT-TRAINING-VISUAL-PREVIEW-LOCAL-DUMMY-SEED-CONTRACT validator')
sys.exit(0)
