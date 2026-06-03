#!/usr/bin/env python3
"""v67 Track C — Story Clear Idempotency Simulator validator."""
from __future__ import annotations
import os, sys, json, re, ast
ROOT='/app'
SIM=os.path.join(ROOT,'backend/scripts/story_clear_idempotency_dry_run_simulator_v1.py')
C=os.path.join(ROOT,'data/design/story/story_clear_idempotency_dry_run_simulator_contract_v1.json')
RES=os.path.join(ROOT,'data/design/story/results/story_clear_idempotency_dry_run_simulator_result_v1.json')
MK=os.path.join(ROOT,'data/design/story/story_clear_idempotency_simulator_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/401_STORY_CLEAR_IDEMPOTENCY_DRY_RUN_SIMULATOR.md')
F=[]
def f(m): F.append(m)
for p in (SIM,C,RES,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(SIM):
    src=open(SIM).read()
    try: tree=ast.parse(src)
    except SyntaxError as e: f(f'simulator syntax: {e}'); tree=None
    if tree is not None:
        forb={'pymongo','motor','redis','server','battle_engine'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.split('.')[0] in forb: f(f'simulator forbidden import: {a.name}')
            elif isinstance(node, ast.ImportFrom):
                if (node.module or '').split('.')[0] in forb:
                    f(f'simulator forbidden from-import: {node.module}')
    no_comments=re.sub(r'#[^\n]*','',src)
    no_strings=re.sub(r'""".*?"""','',no_comments,flags=re.DOTALL)
    if 'MONGO_URL' in no_strings: f('simulator reads MONGO_URL in real code')
    for d in ('first_clear_would_stage','duplicate_same_payload_would_return_existing',
              'duplicate_conflict_would_reject','missing_idempotency_key_would_reject',
              'result_hash_mismatch_would_reject'):
        if d not in src: f(f'simulator missing decision: {d}')
if os.path.exists(RES):
    r=json.load(open(RES))
    if r.get('all_match') is not True: f('result all_match!=true')
    if r.get('all_would_grant_rewards_false') is not True: f('result would_grant_rewards not all false')
    if r.get('db_writes')!=0: f('result db_writes!=0')
    if r.get('reward_grant_executed') is not False: f('result reward_grant_executed!=false')
    if r.get('permanent_progress_written') is not False: f('result permanent_progress_written!=false')
    if r.get('collection_created') is not False: f('result collection_created!=false')
    if r.get('total_scenarios',0)<5: f('result too few scenarios')
if os.path.exists(C):
    d=json.load(open(C))
    inv=d.get('result_invariants') or {}
    for k,v in (('reward_grant_executed',False),('permanent_progress_written',False),
                ('db_writes',0),('live_apply_allowed',False)):
        if inv.get(k)!=v: f(f'contract result_invariants {k}!={v}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-STORY-CLEAR-IDEMPOTENCY-SIMULATOR'); sys.exit(1)
print('[PASS] PROJECT-STORY-CLEAR-IDEMPOTENCY-SIMULATOR'); sys.exit(0)
