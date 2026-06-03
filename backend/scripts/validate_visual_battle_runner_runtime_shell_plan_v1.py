#!/usr/bin/env python3
"""v62 Track A validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
PACK='MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN_AND_FULL_COVERAGE_ROLLUP_SUPER_PACK_v62'
TAG='PUBLIC_SYNC_TAG_v62_MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN'
PLAN=os.path.join(ROOT,'data/design/release_acceleration/visual_battle_runner_runtime_shell_plan_v1.json')
MARKER=os.path.join(ROOT,'data/design/release_acceleration/visual_battle_runner_runtime_shell_plan_marker_v1.json')
F=[]
def f(m): F.append(m)
if not os.path.exists(PLAN): f('missing plan')
else:
    p=json.load(open(PLAN))
    if p.get('version')!='visual_battle_runner_runtime_shell_plan_v1': f('plan.version')
    if p.get('pack')!=PACK: f('plan.pack')
    if p.get('public_sync_tag')!=TAG: f('plan.tag')
    for k,v in (('design_only',True),('runtime_runner_created',False),('runtime_activation_enabled',False),
                ('battle_engine_runtime_enabled',False),('backend_routes_enabled',False),
                ('db_writes',0),('reward_grant_enabled',False),('live_claim_enabled',False),
                ('manual_approval_required',True)):
        if p.get(k)!=v: f(f'plan.{k}!={v}')
    if p.get('planned_future_runner_route')!='/visual-battle-runner-runtime': f('plan.planned_future_runner_route')
    if p.get('current_preview_router')!='/visual-battle-preview-router': f('plan.current_preview_router')
    if p.get('source_contract')!='visual_battle_runner_payload_contract_v0': f('plan.source_contract')
    if p.get('future_contract')!='runtime_runner_payload_v1_draft': f('plan.future_contract')
    if p.get('guild_war_policy')!='autoresolve_with_replay_link_exception': f('plan.guild_war_policy')
    for m in ('material_raid','training','boss','story','tower','event','arena'):
        if m not in (p.get('supported_modes_future') or []): f(f'plan.supported_modes_future missing {m}')
    for c in ('payload_ingestion','timeline_render_adapter','replay_adapter','battle_result_display_adapter',
              'reward_separation_adapter','progress_separation_adapter','rollback_visibility'):
        if c not in (p.get('runtime_shell_components_planned') or []): f(f'plan.components missing {c}')
    for x in ('battle_engine.py changes','/api/battle/simulate changes','/api/story/battle changes',
              'backend route enablement','DB writes','reward grant','inventory mutation','live claim','gacha/shop/VIP/BP changes'):
        if x not in (p.get('forbidden_now') or []): f(f'plan.forbidden_now missing {x}')
if not os.path.exists(MARKER): f('missing marker')
else:
    mk=json.load(open(MARKER))
    if mk.get('marker_version')!='visual_battle_runner_runtime_shell_plan_marker_v1': f('marker.version')
    for k,v in (('pack',PACK),('public_sync_tag',TAG),('design_only',True),
                ('runtime_runner_created',False),('runtime_activation_enabled',False),
                ('battle_engine_runtime_enabled',False),('backend_routes_enabled',False),
                ('db_writes',0),('reward_grant_enabled',False),('live_claim_enabled',False),
                ('manual_approval_required',True),('validator_weakening',False),('fake_pass',False)):
        if mk.get(k)!=v: f(f'marker.{k}!={v}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-VISUAL-BATTLE-RUNNER-RUNTIME-SHELL-PLAN'); sys.exit(1)
print('[PASS] PROJECT-VISUAL-BATTLE-RUNNER-RUNTIME-SHELL-PLAN'); sys.exit(0)
