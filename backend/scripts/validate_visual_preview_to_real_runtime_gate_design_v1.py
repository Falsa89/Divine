#!/usr/bin/env python3
"""Validator: PROJECT-VISUAL-PREVIEW-TO-REAL-RUNTIME-GATE-DESIGN (v61 Track D)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE_SUPER_PACK_v61'
TAG = 'PUBLIC_SYNC_TAG_v61_MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE'
GATE = os.path.join(ROOT, 'data/design/release_acceleration/visual_preview_to_real_runtime_gate_design_v1.json')
MATRIX = os.path.join(ROOT, 'data/design/release_acceleration/per_mode_runtime_activation_gate_matrix_v1.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/visual_preview_to_real_runtime_gate_design_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(GATE): fail('missing gate')
else:
    g = json.load(open(GATE))
    if g.get('version') != 'visual_preview_to_real_runtime_gate_design_v1': fail('gate.version')
    if g.get('pack') != PACK: fail('gate.pack')
    if g.get('public_sync_tag') != TAG: fail('gate.tag')
    for k, v in (('design_only',True),('runtime_activation_enabled',False),
                 ('battle_engine_runtime_enabled',False),('backend_routes_enabled',False),
                 ('db_writes',0),('reward_grant_enabled',False),('live_claim_enabled',False),
                 ('manual_approval_required',True)):
        if g.get(k) != v: fail(f'gate.{k} != {v}')
    if g.get('approved_modes_now') != []: fail('gate.approved_modes_now must be empty list')
    cm = g.get('candidate_modes_future') or []
    for m in ('material_raid','training','boss','story','tower','event','arena'):
        if m not in cm: fail(f'gate.candidate_modes_future missing {m}')
    fb = g.get('forbidden_without_separate_pack') or []
    for x in ('battle_engine.py changes','/api/battle/simulate changes','/api/story/battle changes',
              'DB writes','reward grant','inventory mutation','live claim','gacha/shop/VIP/BP changes'):
        if x not in fb: fail(f'gate.forbidden_without_separate_pack missing {x}')
    gpm = g.get('gates_per_mode') or []
    for x in ('payload_contract_complete','visual_preview_smoke_pass','local_timeline_smoke_pass_where_applicable',
              'runtime_adapter_design_approved','reward_policy_approved','rollback_plan_approved','manual_checksum_approved'):
        if x not in gpm: fail(f'gate.gates_per_mode missing {x}')

if not os.path.exists(MATRIX): fail('missing matrix')
else:
    mx = json.load(open(MATRIX))
    if mx.get('version') != 'per_mode_runtime_activation_gate_matrix_v1': fail('matrix.version')
    if mx.get('db_writes') != 0: fail('matrix.db_writes')
    modes = mx.get('modes') or {}
    for m in ('material_raid','training','boss','story','tower','event','arena'):
        if m not in modes: fail(f'matrix.modes missing {m}')
        for gk in ('payload_contract_complete','visual_preview_smoke_pass','local_timeline_smoke_pass_where_applicable',
                   'runtime_adapter_design_approved','reward_policy_approved','rollback_plan_approved',
                   'manual_checksum_approved','runtime_activated'):
            if modes[m].get(gk) is not False: fail(f'matrix.modes.{m}.{gk} != False')

if not os.path.exists(MARKER): fail('missing marker')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'visual_preview_to_real_runtime_gate_design_marker_v1': fail('marker.version')
    for k, v in (('pack',PACK),('public_sync_tag',TAG),('design_only',True),
                 ('runtime_activation_enabled',False),
                 ('battle_engine_runtime_enabled',False),('backend_routes_enabled',False),
                 ('db_writes',0),('reward_grant_enabled',False),('live_claim_enabled',False),
                 ('manual_approval_required',True),
                 ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k) != v: fail(f'marker.{k} != {v}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-VISUAL-PREVIEW-TO-REAL-RUNTIME-GATE-DESIGN'); sys.exit(1)
print('[PASS] PROJECT-VISUAL-PREVIEW-TO-REAL-RUNTIME-GATE-DESIGN'); sys.exit(0)
