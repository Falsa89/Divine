#!/usr/bin/env python3
"""v66 Track B — Story First Node Alpha Fixture + Runtime Payload Draft validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
FX=os.path.join(ROOT,'data/design/story/story_first_node_alpha_fixture_v1.json')
PY=os.path.join(ROOT,'data/design/story/story_first_node_alpha_runtime_payload_draft_v1.json')
MK=os.path.join(ROOT,'data/design/story/story_first_node_alpha_fixture_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/393_STORY_FIRST_NODE_ALPHA_FIXTURE_AND_PAYLOAD.md')
F=[]
def f(m): F.append(m)
for p in (FX,PY,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(FX):
    d=json.load(open(FX))
    if d.get('node_id')!='story_alpha_node_001': f('fixture node_id mismatch')
    if d.get('permanent_progress') is not False: f('fixture permanent_progress!=false')
    if d.get('reward_grant') is not False: f('fixture reward_grant!=false')
    if d.get('db_writes')!=0: f('fixture db_writes!=0')
    steps=d.get('steps') or []
    if len(steps)<6: f('fixture steps<6')
    kinds={s.get('kind') for s in steps}
    for k in ('narration','choice_hint','mock_skill_cast','damage_tick','enemy_phase','result_preview'):
        if k not in kinds: f(f'fixture steps missing kind {k}')
    rwd=d.get('reward_preview_only') or []
    for r in rwd:
        if r.get('scope')!='preview_only': f('fixture reward scope must be preview_only')
if os.path.exists(PY):
    p=json.load(open(PY))
    if p.get('maps_to_contract')!='runtime_runner_payload_v1_draft':
        f('payload maps_to_contract mismatch')
    if p.get('adapter_version')!='story_runtime_adapter_v1': f('payload adapter_version mismatch')
    if p.get('mode')!='story': f('payload mode!=story')
    if p.get('authoritative_runtime') is not False: f('payload authoritative_runtime!=false')
    fl=p.get('fields') or {}
    if fl.get('permanent_progress') is not False: f('payload fields.permanent_progress!=false')
    if fl.get('reward_grant') is not False: f('payload fields.reward_grant!=false')
    if fl.get('db_writes')!=0: f('payload fields.db_writes!=0')
    if fl.get('steps_count')!=6: f('payload fields.steps_count!=6')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-STORY-FIRST-NODE-ALPHA-FIXTURE-AND-PAYLOAD'); sys.exit(1)
print('[PASS] PROJECT-STORY-FIRST-NODE-ALPHA-FIXTURE-AND-PAYLOAD'); sys.exit(0)
