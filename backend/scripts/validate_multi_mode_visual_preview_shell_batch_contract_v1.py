#!/usr/bin/env python3
"""Validator: PROJECT-MULTI-MODE-VISUAL-PREVIEW-SHELL-BATCH-CONTRACT (v58 Track A).

Verifica:
 - batch contract v1 con i 4 modi (story/tower/event/arena)
 - 4 per-mode contracts (preview_shell_v58, deeplink-only, no backend)
 - multi-mode registry delta v58 con stato preview_shell_v58 per ogni modo
 - shared invariants tutti coerenti (db_writes=0, no runtime, no claim)
 - replaces=MEGA_RELEASE_ACCELERATION_7_STORY_VISUAL_PREVIEW_CONTRACT_TO_DEEPLINK_PACK_v58
No fake PASS. No validator weakening.
"""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
TAG = 'PUBLIC_SYNC_TAG_v58_MEGA_RELEASE_ACCELERATION_7_MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH'
PACK = 'MEGA_RELEASE_ACCELERATION_7_MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH_PACK_v58'
MODES = ['story', 'tower', 'event', 'arena']
BATCH = os.path.join(ROOT, 'data/design/release_acceleration/multi_mode_visual_preview_shell_batch_contract_v1.json')
DELTA = os.path.join(ROOT, 'data/design/release_acceleration/battle_entrypoint_registry_v2_multi_mode_delta_v58.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(BATCH):
    fail(f'missing batch contract: {BATCH}')
else:
    b = json.load(open(BATCH))
    if b.get('version') != 'multi_mode_visual_preview_shell_batch_contract_v1':
        fail(f'batch.version != expected (got {b.get("version")})')
    if b.get('pack') != PACK: fail(f'batch.pack != {PACK}')
    if b.get('public_sync_tag') != TAG: fail(f'batch.public_sync_tag != {TAG}')
    if b.get('modes') != MODES: fail(f'batch.modes != {MODES} (got {b.get("modes")})')
    if b.get('replaces') != 'MEGA_RELEASE_ACCELERATION_7_STORY_VISUAL_PREVIEW_CONTRACT_TO_DEEPLINK_PACK_v58':
        fail(f'batch.replaces invalid (got {b.get("replaces")})')
    si = b.get('shared_invariants') or {}
    for k, v in (
        ('visual_battle_required', True), ('auto_resolve_allowed', False), ('local_only', True),
        ('backend_used', False), ('runtime_used', False), ('battle_engine_runtime_used', False),
        ('result_authoritative', False), ('reward_claim_enabled', False), ('reward_grant_enabled', False),
        ('db_writes', 0), ('no_inventory_mutation', True), ('no_wallet_mutation', True),
    ):
        if si.get(k) != v: fail(f'batch.shared_invariants.{k} != {v} (got {si.get(k)})')
    fg = b.get('forbidden_global') or {}
    for k in ('story_tsx_modified','story_battle_endpoint_modified','battle_engine_modified',
              'combat_tsx_modified','battle_simulate_endpoint_modified','guild_war_policy_regression',
              'new_runtime_endpoint_in_v58','home_menu_mandatory_routing'):
        if fg.get(k) is not False: fail(f'batch.forbidden_global.{k} != False (got {fg.get(k)})')
    refs = b.get('per_mode_contract_refs') or {}
    for m in MODES:
        if m not in refs: fail(f'batch.per_mode_contract_refs missing {m}')

for m in MODES:
    p = os.path.join(ROOT, f'data/design/release_acceleration/{m}_visual_preview_route_contract_v1.json')
    if not os.path.exists(p): fail(f'missing per-mode contract: {p}'); continue
    c = json.load(open(p))
    if c.get('mode_id') != m: fail(f'{m}.mode_id != {m}')
    if c.get('target_state') != 'preview_shell_v58': fail(f'{m}.target_state != preview_shell_v58')
    if c.get('previous_state') != 'design_only_runtime_deferred':
        fail(f'{m}.previous_state mismatch')
    if c.get('pack') != PACK: fail(f'{m}.pack mismatch')
    if c.get('public_sync_tag') != TAG: fail(f'{m}.public_sync_tag mismatch')
    for k, v in (
        ('visual_battle_required', True), ('auto_resolve_allowed', False), ('local_only', True),
        ('backend_used', False), ('runtime_used', False), ('battle_engine_runtime_used', False),
        ('result_authoritative', False), ('reward_claim_enabled', False), ('reward_grant_enabled', False),
        ('db_writes', 0),
    ):
        if c.get(k) != v: fail(f'{m}.{k} != {v} (got {c.get(k)})')
    fb = c.get('forbidden') or {}
    for k in ('backend_fetch','battle_engine_runtime','battle_simulate_endpoint_used',
              'story_battle_endpoint_used','reanimated_used','combat_tsx_imported',
              'story_tsx_imported','home_menu_mandatory_routing','guild_war_policy_regression'):
        if fb.get(k) is not False: fail(f'{m}.forbidden.{k} != False (got {fb.get(k)})')
    if not c.get('default_seed','').endswith('-alpha-v58'):
        fail(f'{m}.default_seed does not end with -alpha-v58')
    if not isinstance(c.get('mode_preview_fields'), list) or len(c.get('mode_preview_fields')) < 7:
        fail(f'{m}.mode_preview_fields invalid')

if not os.path.exists(DELTA):
    fail(f'missing delta: {DELTA}')
else:
    d = json.load(open(DELTA))
    if d.get('version') != 'battle_entrypoint_registry_v2_multi_mode_delta_v58':
        fail('delta.version mismatch')
    if d.get('applies_to') != MODES: fail(f'delta.applies_to != {MODES}')
    deltas = d.get('deltas') or {}
    for m in MODES:
        dm = deltas.get(m) or {}
        if dm.get('new_state') != 'preview_shell_v58': fail(f'delta.{m}.new_state != preview_shell_v58')
        if dm.get('new_implementation_tier') != 'preview_shell': fail(f'delta.{m}.new_implementation_tier != preview_shell')
        if not dm.get('default_seed','').endswith('-alpha-v58'): fail(f'delta.{m}.default_seed mismatch')
    pi = d.get('preserved_invariants') or {}
    for k, v in (('battle_engine_runtime_used', False), ('backend_used', False), ('db_writes', 0)):
        if pi.get(k) != v: fail(f'delta.preserved_invariants.{k} mismatch')
    om = d.get('other_modes_unchanged') or {}
    if om.get('material_raid') != 'alpha_loop_closed_v53': fail('delta.other_modes_unchanged.material_raid mismatch')
    if om.get('training') != 'local_dummy_seed_wired_v56': fail('delta.other_modes_unchanged.training mismatch')
    if om.get('boss') != 'preview_shell_v57': fail('delta.other_modes_unchanged.boss mismatch')
    if om.get('guild_war') != 'autoresolve_with_replay_link_v55': fail('delta.other_modes_unchanged.guild_war mismatch')

marker = os.path.join(ROOT, 'data/design/release_acceleration/multi_mode_visual_preview_shell_batch_marker_v1.json')
if not os.path.exists(marker):
    fail(f'missing track A marker: {marker}')
else:
    mk = json.load(open(marker))
    if mk.get('marker_version') != 'multi_mode_visual_preview_shell_batch_marker_v1': fail('track A marker version mismatch')
    if mk.get('pack') != PACK: fail('track A marker pack mismatch')
    if mk.get('public_sync_tag') != TAG: fail('track A marker tag mismatch')
    if mk.get('db_writes') != 0: fail('track A marker db_writes != 0')
    if mk.get('validator_weakening') is not False: fail('track A marker validator_weakening != False')
    if mk.get('fake_pass') is not False: fail('track A marker fake_pass != False')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MULTI-MODE-VISUAL-PREVIEW-SHELL-BATCH-CONTRACT')
    sys.exit(1)
print('[PASS] PROJECT-MULTI-MODE-VISUAL-PREVIEW-SHELL-BATCH-CONTRACT')
sys.exit(0)
