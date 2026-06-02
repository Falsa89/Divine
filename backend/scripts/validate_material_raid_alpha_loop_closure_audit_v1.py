#!/usr/bin/env python3
"""Validator: PROJECT-MATERIAL-RAID-ALPHA-LOOP-CLOSURE-AUDIT (v53 Track F)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/release_acceleration/material_raid_alpha_loop_closure_audit_v1.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/material_raid_alpha_loop_closure_audit_marker_v1.json')

REQUIRED_STEP_IDS = [
    '/material-raid-alpha',
    'POST /api/material-raid/alpha-battle-preview',
    '/material-raid-visual-preview',
    '/material-raid-reward-preview',
    '/material-raid-alpha',
]

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'material_raid_alpha_loop_closure_audit_v1':
        fail('design contract_version mismatch')
    if d.get('home_menu_routing_required') is not False:
        fail('design home_menu_routing_required must be false')
    if d.get('battle_engine_runtime_used') is not False: fail('battle_engine_runtime_used != False')
    if d.get('battle_engine_py_changed') is not False: fail('battle_engine_py_changed != False')
    if d.get('result_authoritative_anywhere') is not False: fail('result_authoritative_anywhere != False')
    if d.get('reward_grant_enabled') is not False: fail('reward_grant_enabled != False')
    if d.get('reward_claim_enabled') is not False: fail('reward_claim_enabled != False')
    if d.get('materials_granted') is not False: fail('materials_granted != False')
    if d.get('inventory_mutation') is not False: fail('inventory_mutation != False')
    if d.get('db_writes') != 0: fail('db_writes != 0')
    if d.get('compatible_with_future_material_raid_claim_safety') is not True:
        fail('compatible_with_future_material_raid_claim_safety must be true')
    steps = d.get('loop_steps') or []
    if len(steps) != 5: fail(f'loop_steps len != 5 (got {len(steps)})')
    ids = [s.get('id') for s in steps]
    if ids != REQUIRED_STEP_IDS:
        fail(f'loop_steps id sequence mismatch (got {ids})')
    for s in steps:
        if s.get('preview_only') is not True: fail(f'step {s.get("id")} preview_only != True')
        if s.get('db_writes') != 0: fail(f'step {s.get("id")} db_writes != 0')
        if s.get('reward_grant_enabled') is not False: fail(f'step {s.get("id")} reward_grant_enabled != False')
        if s.get('kind') == 'backend_endpoint':
            if s.get('result_authoritative') is not False: fail(f'step {s.get("id")} result_authoritative != False')
            if s.get('battle_engine_runtime_used') is not False: fail(f'step {s.get("id")} battle_engine_runtime_used != False')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('contract_version', 'material_raid_alpha_loop_closure_audit_v1'),
        ('track', 'F'),
        ('loop_steps_count', 5),
        ('home_menu_routing_required', False),
        ('db_writes', 0),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v53_MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_ALPHA_LOOP_CLOSURE'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MATERIAL-RAID-ALPHA-LOOP-CLOSURE-AUDIT validator')
    sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-ALPHA-LOOP-CLOSURE-AUDIT validator')
sys.exit(0)
