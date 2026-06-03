#!/usr/bin/env python3
"""Validator: PROJECT-BOSS-VISUAL-PREVIEW-ROUTE-CONTRACT (v57 Track A)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
CONTRACT = os.path.join(ROOT, 'data/design/release_acceleration/boss_visual_preview_route_contract_v1.json')
DELTA = os.path.join(ROOT, 'data/design/release_acceleration/battle_entrypoint_registry_v2_boss_delta_v57.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/boss_visual_preview_route_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v57_MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE'

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(CONTRACT): fail('missing contract')
else:
    c = json.load(open(CONTRACT))
    if c.get('public_sync_tag') != TAG: fail('contract public_sync_tag mismatch')
    for k, v in (
        ('mode_id','boss'),
        ('previous_state','design_only_runtime_deferred'),
        ('target_state','preview_shell_v57'),
        ('source_route','/boss-visual-preview'),
        ('router_route','/visual-battle-preview-router'),
        ('visual_battle_required',True),
        ('auto_resolve_allowed',False),
        ('replay_link_required',False),
        ('local_only',True),
        ('backend_used',False),
        ('backend_preview_endpoint',None),
        ('battle_engine_runtime_used',False),
        ('result_authoritative',False),
        ('reward_claim_enabled',False),
        ('reward_grant_enabled',False),
        ('db_writes',0),
        ('no_inventory_mutation',True),
        ('no_wallet_mutation',True),
        ('default_seed','boss-alpha-v57'),
    ):
        if c.get(k) != v: fail(f'contract {k} != {v} (got {c.get(k)})')
    bfp = c.get('boss_family_preview') or {}
    for k in ('boss_family_id','boss_display_name','boss_phase_preview','weakness_hint_preview','enrage_hint_preview','background_hint','music_hint'):
        if k not in bfp: fail(f'contract boss_family_preview missing {k}')
    df = c.get('default_fallback') or {}
    for k, v in (
        ('boss_family_id','training_boss_preview'),
        ('boss_display_name','Boss Preview'),
        ('boss_phase_preview','phase_1'),
        ('battle_seed_preview','boss-alpha-v57'),
    ):
        if df.get(k) != v: fail(f'contract default_fallback.{k} != {v}')
    forb = c.get('forbidden') or {}
    for k in ('backend_fetch','battle_engine_runtime','battle_simulate_endpoint_used','story_battle_endpoint_used','reanimated_used','combat_tsx_imported','home_menu_mandatory_routing','guild_war_policy_regression'):
        if forb.get(k) is not False: fail(f'contract forbidden.{k} != false')

if not os.path.exists(DELTA): fail('missing delta')
else:
    d = json.load(open(DELTA))
    if d.get('public_sync_tag') != TAG: fail('delta public_sync_tag mismatch')
    if d.get('parent_registry') != 'data/design/release_acceleration/battle_entrypoint_registry_v2_preview.json': fail('delta parent_registry mismatch')
    if d.get('applies_to') != 'boss': fail('delta applies_to != boss')
    dl = d.get('delta') or {}
    if dl.get('previous_state') != 'design_only_runtime_deferred': fail('delta previous_state mismatch')
    if dl.get('new_state') != 'preview_shell_v57': fail('delta new_state mismatch')
    if dl.get('new_frontend_entry_route') != '/boss-visual-preview': fail('delta new_frontend_entry_route mismatch')
    if dl.get('default_seed') != 'boss-alpha-v57': fail('delta default_seed mismatch')
    inv = d.get('preserved_invariants') or {}
    for k, v in (
        ('visual_battle_required',True),
        ('auto_resolve_allowed',False),
        ('result_authoritative',False),
        ('reward_claim_enabled',False),
        ('reward_grant_enabled',False),
        ('db_writes',0),
        ('battle_engine_runtime_used',False),
        ('backend_used',False),
    ):
        if inv.get(k) != v: fail(f'delta preserved_invariants.{k} != {v}')
    other = d.get('other_modes_unchanged') or {}
    if other.get('material_raid') != 'alpha_loop_closed_v53': fail('delta other_modes material_raid mismatch')
    if other.get('training') != 'local_dummy_seed_wired_v56': fail('delta other_modes training mismatch')
    for m in ('story','tower','event','arena','guild_war'):
        if m not in other: fail(f'delta other_modes_unchanged missing {m}')

if not os.path.exists(MARKER): fail('missing marker')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('marker_version','boss_visual_preview_route_marker_v1'),
        ('track','A'),
        ('public_sync_tag',TAG),
        ('mode_id','boss'),
        ('previous_state','design_only_runtime_deferred'),
        ('target_state','preview_shell_v57'),
        ('source_route','/boss-visual-preview'),
        ('default_seed','boss-alpha-v57'),
        ('db_writes',0),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-BOSS-VISUAL-PREVIEW-ROUTE-CONTRACT validator')
    sys.exit(1)
print('[PASS] PROJECT-BOSS-VISUAL-PREVIEW-ROUTE-CONTRACT validator')
sys.exit(0)
