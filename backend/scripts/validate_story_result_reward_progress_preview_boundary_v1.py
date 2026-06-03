#!/usr/bin/env python3
"""v66 Track D — Result/Reward/Progress preview boundary validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
C=os.path.join(ROOT,'data/design/story/story_result_reward_progress_preview_boundary_v1.json')
MK=os.path.join(ROOT,'data/design/story/story_result_reward_progress_preview_boundary_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/395_STORY_RESULT_REWARD_PROGRESS_PREVIEW_BOUNDARY.md')
F=[]
def f(m): F.append(m)
for p in (C,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(C):
    d=json.load(open(C))
    for k,v in (('result_preview_only',True),('reward_preview_only',True),
                ('progress_preview_only',True),('progress_persisted',False),
                ('reward_granted',False),('materials_granted',False),
                ('db_writes',0)):
        if d.get(k)!=v: f(f'boundary {k}!={v}')
    bs=d.get('boundary_segregation') or {}
    if bs.get('no_shared_mutable_state_with_runtime') is not True:
        f('boundary no_shared_mutable_state_with_runtime!=true')
    if bs.get('no_inventory_mutation') is not True: f('boundary no_inventory_mutation!=true')
    if bs.get('no_wallet_mutation') is not True: f('boundary no_wallet_mutation!=true')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-STORY-RESULT-REWARD-PROGRESS-PREVIEW-BOUNDARY'); sys.exit(1)
print('[PASS] PROJECT-STORY-RESULT-REWARD-PROGRESS-PREVIEW-BOUNDARY'); sys.exit(0)
