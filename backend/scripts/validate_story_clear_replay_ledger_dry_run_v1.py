#!/usr/bin/env python3
"""v67 Track D — Story Clear Replay + Ledger Dry-Run validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
M=os.path.join(ROOT,'data/design/story/story_clear_idempotency_scenario_matrix_v1.json')
R=os.path.join(ROOT,'data/design/story/story_clear_idempotency_replay_dry_run_result_v1.json')
L=os.path.join(ROOT,'data/design/story/story_clear_ledger_dry_run_expected_output_v1.json')
MK=os.path.join(ROOT,'data/design/story/story_clear_replay_ledger_dry_run_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/402_STORY_CLEAR_REPLAY_AND_LEDGER_DRY_RUN.md')
F=[]
def f(m): F.append(m)
for p in (M,R,L,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(M):
    d=json.load(open(M))
    cats=d.get('scenarios_descriptive_categories') or []
    for needed in ('first clear node 001','first clear node 002','first clear node 003',
                   'duplicate same payload','duplicate conflicting payload',
                   'missing idempotency key','result hash mismatch',
                   'over chapter sequence attempt','rollback token preview',
                   'observation warning threshold','observation critical threshold'):
        if needed not in cats: f(f'scenario matrix missing category: {needed}')
    scs=d.get('scenarios') or []
    if len(scs)<5: f('scenario matrix has too few executable scenarios')
if os.path.exists(R):
    r=json.load(open(R))
    sm=r.get('expected_scenario_status_map') or {}
    for k,v in (('first_clear','staged_pending'),
                ('duplicate_same_payload','duplicate_same_payload'),
                ('duplicate_conflict','rejected'),
                ('missing_idempotency_key','rejected'),
                ('result_hash_mismatch','rejected')):
        if sm.get(k)!=v: f(f'replay map {k}!={v}')
    for k,v in (('collection_created',False),('indexes_created',False),
                ('staged_rows_are_simulated',True),
                ('reward_grant_result','not_executed'),
                ('permanent_progress_result','not_written')):
        if r.get(k)!=v: f(f'replay {k}!={v}')
if os.path.exists(L):
    l=json.load(open(L))
    if l.get('ledger_dry_run_only') is not True: f('ledger ledger_dry_run_only!=true')
    if l.get('collection_created') is not False: f('ledger collection_created!=false')
    flds=l.get('expected_ledger_fields') or []
    for fld in ('idempotency_key','user_id','node_id','payload_hash','result_hash','status'):
        if fld not in flds: f(f'ledger missing field {fld}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-STORY-CLEAR-REPLAY-LEDGER-DRY-RUN'); sys.exit(1)
print('[PASS] PROJECT-STORY-CLEAR-REPLAY-LEDGER-DRY-RUN'); sys.exit(0)
