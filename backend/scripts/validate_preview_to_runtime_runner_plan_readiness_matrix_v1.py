#!/usr/bin/env python3
"""v62 Track F validator (QA/readiness matrix + progress v7)."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
PACK='MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN_AND_FULL_COVERAGE_ROLLUP_SUPER_PACK_v62'
TAG='PUBLIC_SYNC_TAG_v62_MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN'
MX=os.path.join(ROOT,'data/design/qa/preview_to_runtime_runner_plan_readiness_matrix_v1.json')
MK=os.path.join(ROOT,'data/design/qa/preview_to_runtime_runner_plan_readiness_matrix_marker_v1.json')
REP=os.path.join(ROOT,'data/design/release_acceleration/visual_preview_runtime_shell_progress_report_v7.json')
F=[]
def f(m): F.append(m)
if not os.path.exists(MX): f('missing matrix')
else:
    m=json.load(open(MX))
    if m.get('version')!='preview_to_runtime_runner_plan_readiness_matrix_v1': f('matrix.version')
    if m.get('pack')!=PACK: f('matrix.pack')
    if m.get('public_sync_tag')!=TAG: f('matrix.tag')
    if m.get('db_writes')!=0: f('matrix.db_writes')
    flows=m.get('flows') or []
    if len(flows)<20: f(f'matrix.flows too low: {len(flows)}')
    sevs={x.get('severity') for x in flows}
    for s in ('P0','P1','P2','P3'):
        if s not in sevs: f(f'matrix missing severity {s}')
    fb=m.get('forbidden') or {}
    for k in ('claim_button_present','db_writes_nonzero','backend_fetch_present','battle_engine_called',
              'story_tsx_modified','story_battle_endpoint_called','battle_simulate_endpoint_called',
              'guild_war_policy_regression','runtime_activation_enabled','runtime_runner_created',
              'frontend_runtime_screen_changed','validator_weakening','fake_pass'):
        if fb.get(k) is not False: f(f'matrix.forbidden.{k}!=False')
if not os.path.exists(MK): f('missing matrix marker')
else:
    mk=json.load(open(MK))
    if mk.get('marker_version')!='preview_to_runtime_runner_plan_readiness_matrix_marker_v1': f('mk.version')
    for k,v in (('pack',PACK),('public_sync_tag',TAG),('db_writes',0),
                ('claim_button_present',False),('battle_engine_called',False),
                ('backend_fetch_present',False),('story_tsx_modified',False),
                ('guild_war_policy_regression',False),('runtime_activation_enabled',False),
                ('runtime_runner_created',False),('frontend_runtime_screen_changed',False),
                ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k)!=v: f(f'mk.{k}!={v}')
if not os.path.exists(REP): f('missing progress report')
else:
    r=json.load(open(REP))
    if r.get('version')!='visual_preview_runtime_shell_progress_report_v7': f('rep.version')
    if r.get('pack')!=PACK: f('rep.pack')
    if r.get('public_sync_tag')!=TAG: f('rep.tag')
    for k,v in (('db_writes',0),('battle_engine_runtime_used',False),
                ('reward_grant_enabled',False),('live_claim_enabled',False)):
        if r.get(k)!=v: f(f'rep.{k}!={v}')
    ms=r.get('modes_status') or {}
    expected={'material_raid':'alpha_loop_closed_v53','training':'local_dummy_seed_wired_v56',
              'boss':'local_dummy_seed_wired_v59','story':'local_dummy_seed_wired_v61',
              'tower':'local_dummy_seed_wired_v59','event':'local_dummy_seed_wired_v60',
              'arena':'local_dummy_seed_wired_v60',
              'guild_war':'autoresolve_with_replay_link_exception_unchanged',
              'visual_battle_runner_payload_contract':'design_only_v0',
              'router_adapter_preview':'adapter_preview_v61_hardened',
              'runtime_gate_design':'design_only_v1',
              'visual_preview_local_layer':'complete',
              'runtime_runner_plan':'design_only_v1',
              'preview_to_runtime_transition_plan':'design_only_v1',
              'per_mode_readiness_matrix':'design_only_v1',
              'material_raid_claim_safety':'deferred_to_v63_gated'}
    for k,v in expected.items():
        if ms.get(k)!=v: f(f'rep.modes_status.{k}!={v}')
    nra=r.get('next_recommended_after_batch') or []
    for n in ('material_raid_claim_safety_and_staging_blueprint_super_pack_v63',
              'material_raid_staging_dry_run_and_canary_simulation_v64',
              'material_raid_first_controlled_live_staging_claim_v65'):
        if n not in nra: f(f'rep.next_recommended_after_batch missing {n}')
    da=(r.get('director_approvals') or {}).get('not_approved') or []
    for n in ('runtime_activation','backend_routes','db_writes','reward_grant','battle_engine_runtime'):
        if n not in da: f(f'rep.director_approvals.not_approved missing {n}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-PREVIEW-TO-RUNTIME-RUNNER-PLAN-READINESS-MATRIX'); sys.exit(1)
print('[PASS] PROJECT-PREVIEW-TO-RUNTIME-RUNNER-PLAN-READINESS-MATRIX'); sys.exit(0)
