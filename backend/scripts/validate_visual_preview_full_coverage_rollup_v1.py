#!/usr/bin/env python3
"""v62 Track C validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
PACK='MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN_AND_FULL_COVERAGE_ROLLUP_SUPER_PACK_v62'
TAG='PUBLIC_SYNC_TAG_v62_MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN'
ROLLUP=os.path.join(ROOT,'data/design/release_acceleration/visual_preview_full_coverage_rollup_v1.json')
MARKER=os.path.join(ROOT,'data/design/release_acceleration/visual_preview_full_coverage_rollup_marker_v1.json')
F=[]
def f(m): F.append(m)
if not os.path.exists(ROLLUP): f('missing rollup')
else:
    r=json.load(open(ROLLUP))
    if r.get('version')!='visual_preview_full_coverage_rollup_v1': f('rollup.version')
    if r.get('pack')!=PACK: f('rollup.pack')
    if r.get('public_sync_tag')!=TAG: f('rollup.tag')
    expected={'material_raid':'alpha_loop_closed_v53','training':'local_dummy_seed_wired_v56',
              'boss':'local_dummy_seed_wired_v59','story':'local_dummy_seed_wired_v61',
              'tower':'local_dummy_seed_wired_v59','event':'local_dummy_seed_wired_v60',
              'arena':'local_dummy_seed_wired_v60',
              'guild_war':'autoresolve_with_replay_link_exception_unchanged'}
    ms=r.get('modes_status') or {}
    for k,v in expected.items():
        if ms.get(k)!=v: f(f'rollup.modes_status.{k}!={v}')
    if r.get('payload_contract')!='design_only_v0': f('rollup.payload_contract')
    if r.get('router_adapter')!='adapter_preview_v61_hardened': f('rollup.router_adapter')
    if r.get('runtime_gate_design')!='design_only_v1': f('rollup.runtime_gate_design')
    if r.get('coverage_status')!='visual_preview_local_layer_complete': f('rollup.coverage_status')
    if r.get('missing_preview_modes')!=[]: f('rollup.missing_preview_modes != []')
    if r.get('runtime_modes_enabled')!=[]: f('rollup.runtime_modes_enabled != []')
    for k,v in (('db_writes',0),('battle_engine_runtime_used',False),
                ('reward_grant_enabled',False),('live_claim_enabled',False)):
        if r.get(k)!=v: f(f'rollup.{k}!={v}')
if not os.path.exists(MARKER): f('missing marker')
else:
    mk=json.load(open(MARKER))
    if mk.get('marker_version')!='visual_preview_full_coverage_rollup_marker_v1': f('marker.version')
    if mk.get('coverage_status')!='visual_preview_local_layer_complete': f('marker.coverage_status')
    for k,v in (('pack',PACK),('public_sync_tag',TAG),('db_writes',0),
                ('battle_engine_runtime_used',False),('reward_grant_enabled',False),
                ('live_claim_enabled',False),('validator_weakening',False),('fake_pass',False)):
        if mk.get(k)!=v: f(f'marker.{k}!={v}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-VISUAL-PREVIEW-FULL-COVERAGE-ROLLUP'); sys.exit(1)
print('[PASS] PROJECT-VISUAL-PREVIEW-FULL-COVERAGE-ROLLUP'); sys.exit(0)
