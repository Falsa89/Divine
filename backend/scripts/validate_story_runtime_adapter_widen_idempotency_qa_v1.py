#!/usr/bin/env python3
"""v67 Track F — QA matrix + Progress Report v11 validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
M=os.path.join(ROOT,'data/design/qa/story_runtime_adapter_widen_idempotency_qa_matrix_v1.json')
R=os.path.join(ROOT,'data/design/release_acceleration/story_runtime_adapter_progress_report_v11.json')
MK=os.path.join(ROOT,'data/design/qa/story_runtime_adapter_widen_idempotency_qa_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/404_STORY_RUNTIME_ADAPTER_WIDEN_IDEMPOTENCY_QA.md')
F=[]
def f(m): F.append(m)
for p in (M,R,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(M):
    d=json.load(open(M))
    ch=d.get('checks') or []
    if len(ch)<20: f('qa checks count too low')
    sev=d.get('severity_summary') or {}
    if (sev.get('P0') or 0) < 15: f('qa P0 count too low')
    must={'v66_safe_state_present','node_002_fixture_exists','node_003_fixture_exists',
          'payload_draft_instances_exist','screen_supports_nodes_1_to_3',
          'no_backend_fetch','no_import_from_story_tsx','no_import_from_combat_tsx',
          'no_battle_engine_reference','no_api_story_battle','no_api_battle_simulate',
          'no_reward_grant','no_permanent_progress','idempotency_simulator_exists',
          'simulator_imports_no_db_libs','scenario_matrix_exists','replay_result_exists',
          'rollback_simulation_exists','observation_result_exists',
          'md5_invariants_intact','typescript_check_pass'}
    got={c.get('name') for c in ch}
    miss=must-got
    if miss: f(f'qa missing checks: {sorted(miss)}')
if os.path.exists(R):
    r=json.load(open(R))
    for k,v in (('story_runtime_adapter','preview_shell_v67_widened'),
                ('story_idempotency_simulation','ready_v67'),
                ('story_reward_grant',False),('story_permanent_progress',False),
                ('story_db_writes',0),('battle_engine_runtime',False)):
        if r.get(k)!=v: f(f'progress v11 {k}!={v}')
    nx=r.get('next_recommended') or []
    if 'story_first_playable_alpha_slice_v68_or_v67_next' not in nx and 'boss_tower_alpha_loop_super_pack' not in nx:
        f('progress v11 missing next_recommended')
    na=r.get('not_approved') or []
    for n in ('story_permanent_progress','story_reward_grant','battle_engine_runtime','db_writes','backend_route_enablement'):
        if n not in na: f(f'progress v11 not_approved missing {n}')
    sn=r.get('story_alpha_nodes_ready') or []
    for nid in ('story_alpha_node_001','story_alpha_node_002','story_alpha_node_003'):
        if nid not in sn: f(f'progress v11 story_alpha_nodes_ready missing {nid}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-STORY-RUNTIME-ADAPTER-WIDEN-IDEMPOTENCY-QA'); sys.exit(1)
print('[PASS] PROJECT-STORY-RUNTIME-ADAPTER-WIDEN-IDEMPOTENCY-QA'); sys.exit(0)
