#!/usr/bin/env python3
"""Validator: PROJECT-MATERIAL-RAID-ALPHA-LOOP-CLOSURE-SMOKE-MATRIX (v53 Track E)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/qa/material_raid_alpha_loop_closure_smoke_matrix_v1.json')
MARKER = os.path.join(ROOT, 'data/design/qa/material_raid_alpha_loop_closure_smoke_matrix_marker_v1.json')

REQUIRED_FLOW_IDS = {
    'alpha_open', 'prepare_battle', 'open_visual_preview', 'visual_preview_missing',
    'open_reward_preview', 'reward_preview_backend_off', 'reward_preview_backend_on',
    'no_claim_button', 'return_to_alpha', 'locked_track_no_loop',
    'underpowered_no_loop', 'mobile_rotation_layout', 'no_db_write_no_grant',
}
REQUIRED_SEVERITY = {'P0', 'P1', 'P2', 'P3'}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'material_raid_alpha_loop_closure_smoke_matrix_v1':
        fail('design contract_version mismatch')
    sev = set(d.get('severity_levels') or [])
    miss_s = REQUIRED_SEVERITY - sev
    if miss_s: fail(f'severity_levels missing: {sorted(miss_s)}')
    flows = d.get('flows') or []
    flow_ids = {f.get('id') for f in flows}
    miss_f = REQUIRED_FLOW_IDS - flow_ids
    if miss_f: fail(f'flows missing: {sorted(miss_f)}')
    for f in flows:
        if f.get('severity') not in REQUIRED_SEVERITY: fail(f'flow {f.get("id")} severity invalid')
        if not f.get('label_it'): fail(f'flow {f.get("id")} label_it missing')
        if not f.get('expected'): fail(f'flow {f.get("id")} expected missing')
    if d.get('db_writes') != 0: fail('design db_writes != 0')
    if d.get('live_apply_allowed') is not False: fail('design live_apply_allowed != False')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('contract_version', 'material_raid_alpha_loop_closure_smoke_matrix_v1'),
        ('track', 'E'),
        ('flows_count', 13),
        ('db_writes', 0),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v53_MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_ALPHA_LOOP_CLOSURE'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')
    if set(m.get('severity_levels') or []) != REQUIRED_SEVERITY:
        fail('marker severity_levels mismatch')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MATERIAL-RAID-ALPHA-LOOP-CLOSURE-SMOKE-MATRIX validator')
    sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-ALPHA-LOOP-CLOSURE-SMOKE-MATRIX validator')
sys.exit(0)
