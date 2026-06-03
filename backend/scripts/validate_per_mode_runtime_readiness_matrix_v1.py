#!/usr/bin/env python3
"""v62 Track D validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
PACK='MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN_AND_FULL_COVERAGE_ROLLUP_SUPER_PACK_v62'
TAG='PUBLIC_SYNC_TAG_v62_MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN'
MAT=os.path.join(ROOT,'data/design/release_acceleration/per_mode_runtime_readiness_matrix_v1.json')
MARKER=os.path.join(ROOT,'data/design/release_acceleration/per_mode_runtime_readiness_matrix_marker_v1.json')
F=[]
def f(m): F.append(m)
if not os.path.exists(MAT): f('missing matrix')
else:
    m=json.load(open(MAT))
    if m.get('version')!='per_mode_runtime_readiness_matrix_v1': f('matrix.version')
    if m.get('pack')!=PACK: f('matrix.pack')
    if m.get('public_sync_tag')!=TAG: f('matrix.tag')
    if m.get('design_only') is not True: f('matrix.design_only')
    if m.get('db_writes')!=0: f('matrix.db_writes')
    modes=m.get('modes') or {}
    expected_priority={'material_raid':'P0_P1','training':'P1','story':'P1','boss':'P2','tower':'P2','event':'P3','arena':'P3'}
    for mode_id, exp_pri in expected_priority.items():
        md=modes.get(mode_id) or {}
        if md.get('mode_id')!=mode_id: f(f'matrix.modes.{mode_id}.mode_id mismatch')
        if md.get('runner_runtime_ready') is not False: f(f'matrix.modes.{mode_id}.runner_runtime_ready != False')
        if md.get('backend_route_ready') is not False: f(f'matrix.modes.{mode_id}.backend_route_ready != False')
        if md.get('manual_approval_ready') is not False: f(f'matrix.modes.{mode_id}.manual_approval_ready != False')
        if md.get('recommended_runtime_priority')!=exp_pri: f(f'matrix.modes.{mode_id}.priority!={exp_pri}')
        for k in ('preview_status','local_timeline_status','payload_contract_ready','runtime_gate_ready',
                  'reward_policy_ready','rollback_plan_ready','qa_smoke_ready','risk_tier'):
            if k not in md: f(f'matrix.modes.{mode_id} missing field {k}')
    # risk tiers
    if 'medium_high' not in (modes.get('material_raid') or {}).get('risk_tier',''): f('material_raid risk tier should be medium-high')
    if 'low' not in (modes.get('training') or {}).get('risk_tier',''): f('training risk should be low')
    if 'high' not in (modes.get('event') or {}).get('risk_tier',''): f('event risk should be high')
    if 'high' not in (modes.get('arena') or {}).get('risk_tier',''): f('arena risk should be high')
if not os.path.exists(MARKER): f('missing marker')
else:
    mk=json.load(open(MARKER))
    if mk.get('marker_version')!='per_mode_runtime_readiness_matrix_marker_v1': f('marker.version')
    for k,v in (('pack',PACK),('public_sync_tag',TAG),('design_only',True),('db_writes',0),
                ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k)!=v: f(f'marker.{k}!={v}')
    lst=mk.get('modes_listed') or []
    for x in ('material_raid','training','story','boss','tower','event','arena'):
        if x not in lst: f(f'marker.modes_listed missing {x}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-PER-MODE-RUNTIME-READINESS-MATRIX'); sys.exit(1)
print('[PASS] PROJECT-PER-MODE-RUNTIME-READINESS-MATRIX'); sys.exit(0)
