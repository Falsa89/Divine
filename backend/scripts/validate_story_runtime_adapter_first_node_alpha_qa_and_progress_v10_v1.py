#!/usr/bin/env python3
"""v66 Track F — QA matrix + Progress Report v10 validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
M=os.path.join(ROOT,'data/design/qa/story_runtime_adapter_and_first_node_alpha_qa_matrix_v1.json')
R=os.path.join(ROOT,'data/design/release_acceleration/visual_preview_runtime_shell_progress_report_v10.json')
MK=os.path.join(ROOT,'data/design/qa/story_runtime_adapter_and_first_node_alpha_qa_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/397_STORY_RUNTIME_ADAPTER_FIRST_NODE_ALPHA_QA_AND_PROGRESS_v10.md')
F=[]
def f(m): F.append(m)
for p in (M,R,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(M):
    d=json.load(open(M))
    ch=d.get('checks') or []
    if len(ch)<18: f('qa checks too few')
    sev=d.get('severity_summary') or {}
    if (sev.get('P0') or 0) < 15: f('qa P0 count too low')
    must={'adapter_contract_exists','first_node_fixture_exists','runtime_payload_draft_exists',
          'new_screen_file_exists','screen_is_deeplink_only','no_import_from_story_tsx',
          'no_import_from_combat_tsx','no_import_from_battle_engine','no_api_calls_in_screen',
          'no_async_storage','no_reanimated','reward_preview_boundary_present',
          'progress_not_persisted','idempotency_design_present','no_backend_route_change',
          'no_server_py_change','no_battle_engine_change','no_story_tsx_change',
          'no_combat_tsx_change','md5_invariants_intact'}
    got={c.get('name') for c in ch}
    miss=must-got
    if miss: f(f'qa missing checks: {sorted(miss)}')
if os.path.exists(R):
    r=json.load(open(R))
    for k,v in (('visual_preview_local_layer','complete'),
                ('story_runtime_adapter','alpha_preview_v66'),
                ('story_first_node_alpha','preview_ready_v66'),
                ('story_runtime_authoritative',False),
                ('story_permanent_progress',False),
                ('story_reward_grant',False)):
        if r.get(k)!=v: f(f'progress v10 {k}!={v}')
    nx=r.get('next_recommended') or []
    if 'story_runtime_adapter_widen_and_idempotency_v67' not in nx:
        f('progress v10 missing v67 next_recommended')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-STORY-RUNTIME-ADAPTER-FIRST-NODE-ALPHA-QA-AND-PROGRESS-v10'); sys.exit(1)
print('[PASS] PROJECT-STORY-RUNTIME-ADAPTER-FIRST-NODE-ALPHA-QA-AND-PROGRESS-v10'); sys.exit(0)
