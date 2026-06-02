#!/usr/bin/env python3
"""Validator: PROJECT-VISUAL-BATTLE-ROUTING-PLAYABLE-SLICE-AUDIT (v51 Track C)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/release_acceleration/visual_battle_routing_playable_slice_audit_v1.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/visual_battle_routing_playable_slice_audit_marker_v1.json')

REQUIRED_MODES = {'story', 'material_raid', 'tower', 'arena', 'guild_war', 'training', 'event', 'boss'}
REQUIRED_FIELDS_PER_MODE = {
    'desired_behavior', 'current_known_state', 'playable_alpha_priority',
    'visual_battle_required', 'auto_resolve_allowed', 'replay_link_required',
    'next_pack_action',
}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'visual_battle_routing_playable_slice_audit_v1':
        fail(f'design contract_version mismatch')
    if d.get('battle_engine_py_changed') is not False: fail('battle_engine_py_changed must be false')
    if d.get('combat_tsx_changed') is not False: fail('combat_tsx_changed must be false')
    if d.get('story_tsx_changed') is not False: fail('story_tsx_changed must be false')
    if d.get('battle_simulate_endpoint_changed') is not False: fail('battle_simulate_endpoint_changed must be false')
    if d.get('story_battle_endpoint_changed') is not False: fail('story_battle_endpoint_changed must be false')
    modes = d.get('modes') or []
    seen = set()
    for entry in modes:
        name = entry.get('mode')
        seen.add(name)
        miss = REQUIRED_FIELDS_PER_MODE - set(entry.keys())
        if miss: fail(f'mode {name} missing fields: {sorted(miss)}')
        if name == 'material_raid':
            if entry.get('visual_battle_required') is not True: fail('material_raid visual_battle_required must be true')
            if entry.get('auto_resolve_allowed') is not False: fail('material_raid auto_resolve_allowed must be false')
        if name == 'story':
            if entry.get('visual_battle_required') is not True: fail('story visual_battle_required must be true')
        if name == 'guild_war':
            if entry.get('auto_resolve_allowed') is not True: fail('guild_war auto_resolve_allowed must be true')
            if entry.get('replay_link_required') is not True: fail('guild_war replay_link_required must be true')
        if name == 'training':
            if entry.get('visual_battle_required') is not True: fail('training visual_battle_required must be true')
        if name == 'arena':
            if entry.get('visual_battle_required') is not True: fail('arena visual_battle_required must be true')
        if name in ('boss', 'event', 'tower'):
            if entry.get('visual_battle_required') is not True: fail(f'{name} visual_battle_required must be true')
    miss_modes = REQUIRED_MODES - seen
    if miss_modes: fail(f'design modes missing: {sorted(miss_modes)}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('contract_version', 'visual_battle_routing_playable_slice_audit_v1'),
        ('track', 'C'),
        ('modes_count', 8),
        ('battle_engine_py_changed', False),
        ('combat_tsx_changed', False),
        ('story_tsx_changed', False),
        ('battle_simulate_endpoint_changed', False),
        ('story_battle_endpoint_changed', False),
        ('db_writes', 0),
        ('real_db_writes', 0),
        ('live_apply_allowed', False),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v51_MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-VISUAL-BATTLE-ROUTING-PLAYABLE-SLICE-AUDIT validator')
    sys.exit(1)
print('[PASS] PROJECT-VISUAL-BATTLE-ROUTING-PLAYABLE-SLICE-AUDIT validator')
sys.exit(0)
