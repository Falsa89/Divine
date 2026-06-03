#!/usr/bin/env python3
"""v66 Track A — Story Runtime Adapter v1 Contract validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
C=os.path.join(ROOT,'data/design/story/story_runtime_adapter_v1_contract.json')
MK=os.path.join(ROOT,'data/design/story/story_runtime_adapter_v1_marker.json')
DOC=os.path.join(ROOT,'docs/divine/392_STORY_RUNTIME_ADAPTER_v1_CONTRACT.md')
F=[]
def f(m): F.append(m)
for p in (C,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(C):
    d=json.load(open(C))
    for k,v in (('contract_version','story_runtime_adapter_v1_contract'),
                ('authoritative_runtime',False),('permanent_progress',False),
                ('reward_grant_enabled',False),('db_writes',0),
                ('no_route_added',True),('no_api_story_battle_call',True),
                ('no_api_battle_simulate_call',True)):
        if d.get(k)!=v: f(f'contract {k}!={v}')
    nim=d.get('no_import_from') or []
    for needed in ('story.tsx','combat.tsx','battle_engine.py'):
        if needed not in nim: f(f'contract no_import_from missing {needed}')
    kinds=d.get('steps_kinds_allowed') or []
    for k in ('narration','choice_hint','mock_skill_cast','damage_tick','enemy_phase','result_preview'):
        if k not in kinds: f(f'contract steps_kinds_allowed missing {k}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-STORY-RUNTIME-ADAPTER-v1-CONTRACT'); sys.exit(1)
print('[PASS] PROJECT-STORY-RUNTIME-ADAPTER-v1-CONTRACT'); sys.exit(0)
