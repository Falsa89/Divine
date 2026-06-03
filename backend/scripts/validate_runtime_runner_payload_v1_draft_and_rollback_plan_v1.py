#!/usr/bin/env python3
"""v62 Track E validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
PACK='MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN_AND_FULL_COVERAGE_ROLLUP_SUPER_PACK_v62'
TAG='PUBLIC_SYNC_TAG_v62_MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN'
DRAFT=os.path.join(ROOT,'data/design/release_acceleration/runtime_runner_payload_v1_draft_contract.json')
ROLL=os.path.join(ROOT,'data/design/release_acceleration/runtime_runner_rollback_and_observation_plan_v1.json')
MARKER=os.path.join(ROOT,'data/design/release_acceleration/runtime_runner_payload_v1_draft_marker_v1.json')
F=[]
def f(m): F.append(m)
if not os.path.exists(DRAFT): f('missing draft')
else:
    d=json.load(open(DRAFT))
    if d.get('version')!='runtime_runner_payload_v1_draft_contract': f('draft.version')
    if d.get('pack')!=PACK: f('draft.pack')
    if d.get('public_sync_tag')!=TAG: f('draft.tag')
    for k,v in (('design_only',True),('not_consumed_by_runtime',True),
                ('result_authoritative_allowed',False),('battle_engine_result_allowed',False),
                ('reward_grant_allowed',False),('db_writes_allowed',False)):
        if d.get(k)!=v: f(f'draft.{k}!={v}')
    for field in ('payload_version','mode','source_route','battle_seed','runtime_session_id',
                  'preview_session_id','timeline_steps','result_authoritative',
                  'battle_engine_runtime_used','reward_policy_ref','rollback_token_ref','observation_window_ref'):
        if field not in (d.get('fields') or []): f(f'draft.fields missing {field}')
if not os.path.exists(ROLL): f('missing rollback plan')
else:
    r=json.load(open(ROLL))
    if r.get('version')!='runtime_runner_rollback_and_observation_plan_v1': f('roll.version')
    if r.get('design_only') is not True: f('roll.design_only')
    if r.get('rollback_required') is not True: f('roll.rollback_required')
    if r.get('observation_window_required') is not True: f('roll.observation_window_required')
    if r.get('suggested_window_minutes')!=30: f('roll.suggested_window_minutes')
    esc=r.get('escalation_levels') or []
    for x in ('P0','P1','P2','P3'):
        if x not in esc: f(f'roll.escalation_levels missing {x}')
    stop=r.get('stop_on') or []
    for x in ('DB write outside allowlist','reward duplication','battle_engine exception',
              'client crash rate spike','mismatch preview/result','missing idempotency key','unauthorized route exposure'):
        if x not in stop: f(f'roll.stop_on missing {x}')
if not os.path.exists(MARKER): f('missing marker')
else:
    mk=json.load(open(MARKER))
    if mk.get('marker_version')!='runtime_runner_payload_v1_draft_marker_v1': f('marker.version')
    for k,v in (('pack',PACK),('public_sync_tag',TAG),('design_only',True),
                ('not_consumed_by_runtime',True),('result_authoritative_allowed',False),
                ('battle_engine_result_allowed',False),('reward_grant_allowed',False),
                ('db_writes_allowed',False),('rollback_required',True),
                ('observation_window_required',True),
                ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k)!=v: f(f'marker.{k}!={v}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-RUNTIME-RUNNER-PAYLOAD-v1-DRAFT-AND-ROLLBACK-PLAN'); sys.exit(1)
print('[PASS] PROJECT-RUNTIME-RUNNER-PAYLOAD-v1-DRAFT-AND-ROLLBACK-PLAN'); sys.exit(0)
