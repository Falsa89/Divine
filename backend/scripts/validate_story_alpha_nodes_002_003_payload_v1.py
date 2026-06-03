#!/usr/bin/env python3
"""v67 Track A — Story Alpha Nodes 002/003 Payload validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
FX=os.path.join(ROOT,'data/design/story/story_alpha_nodes_002_003_fixture_v1.json')
PY=os.path.join(ROOT,'data/design/story/story_alpha_nodes_002_003_runtime_payload_draft_instances_v1.json')
WC=os.path.join(ROOT,'data/design/story/story_runtime_adapter_widening_contract_v1.json')
MK=os.path.join(ROOT,'data/design/story/story_alpha_nodes_002_003_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/399_STORY_ALPHA_NODES_002_003_FIXTURE_AND_PAYLOAD.md')
F=[]
def f(m): F.append(m)
for p in (FX,PY,WC,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(FX):
    d=json.load(open(FX))
    nodes=d.get('nodes') or []
    ids={n.get('node_id') for n in nodes}
    for nid in ('story_alpha_node_002','story_alpha_node_003'):
        if nid not in ids: f(f'fixture missing node {nid}')
    for n in nodes:
        for k in ('chapter_id','node_id','encounter_id','encounter_display_name',
                  'battle_seed','enemy_family_preview','recommended_power_preview',
                  'team_power_preview','background_hint','music_hint','tutorial_hint','steps'):
            if k not in n: f(f'fixture node {n.get("node_id")} missing {k}')
        steps=n.get('steps') or []
        if not (5 <= len(steps) <= 7): f(f'fixture node {n.get("node_id")} steps count={len(steps)} not in 5..7')
if os.path.exists(PY):
    d=json.load(open(PY))
    if d.get('payload_version')!='runtime_runner_payload_v1_draft':
        f('payload payload_version mismatch')
    if d.get('not_consumed_by_runtime') is not True: f('payload not_consumed_by_runtime!=true')
    inst=d.get('instances') or {}
    for nid in ('story_alpha_node_002','story_alpha_node_003'):
        if nid not in inst: f(f'payload instances missing {nid}')
        ip=inst.get(nid) or {}
        for k,v in (('authoritative_runtime',False),('result_authoritative',False),
                    ('battle_engine_runtime_used',False),('db_writes',0),
                    ('reward_grant_enabled',False),('permanent_progress_enabled',False),
                    ('reward_preview_not_granted',True),('progress_preview_not_persisted',True)):
            if ip.get(k)!=v: f(f'payload instance {nid} {k}!={v}')
if os.path.exists(WC):
    d=json.load(open(WC))
    wn=d.get('widened_nodes') or []
    for nid in ('story_alpha_node_001','story_alpha_node_002','story_alpha_node_003'):
        if nid not in wn: f(f'widening contract missing {nid}')
    nim=d.get('no_import_from') or []
    for needed in ('frontend/app/story.tsx','frontend/app/combat.tsx','backend/battle_engine.py'):
        if needed not in nim: f(f'widening contract no_import_from missing {needed}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-STORY-ALPHA-NODES-002-003-PAYLOAD'); sys.exit(1)
print('[PASS] PROJECT-STORY-ALPHA-NODES-002-003-PAYLOAD'); sys.exit(0)
