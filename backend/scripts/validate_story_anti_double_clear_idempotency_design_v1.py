#!/usr/bin/env python3
"""v66 Track E — Story Anti Double-Clear + Idempotency Design validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
C=os.path.join(ROOT,'data/design/story/story_anti_double_clear_idempotency_design_v1.json')
MK=os.path.join(ROOT,'data/design/story/story_anti_double_clear_idempotency_design_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/396_STORY_ANTI_DOUBLE_CLEAR_IDEMPOTENCY_DESIGN.md')
F=[]
def f(m): F.append(m)
for p in (C,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(C):
    d=json.load(open(C))
    if d.get('idempotency_required') is not True: f('idempotency_required!=true')
    if d.get('anti_double_clear_required') is not True: f('anti_double_clear_required!=true')
    if d.get('no_db_writes') is not True: f('no_db_writes!=true')
    if d.get('db_writes')!=0: f('db_writes!=0')
    kc=d.get('key_components') or []
    for k in ('user_id','server_id','chapter_id','node_id','preview_session_id','attempt_nonce'):
        if k not in kc: f(f'key_components missing {k}')
    st=d.get('statuses') or []
    for s in ('preview_only','cleared_in_preview','duplicate_same_payload','duplicate_conflict','rejected'):
        if s not in st: f(f'statuses missing {s}')
    om=d.get('observation_metrics_design') or []
    if len(om)<4: f('observation_metrics_design too few')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-STORY-ANTI-DOUBLE-CLEAR-IDEMPOTENCY-DESIGN'); sys.exit(1)
print('[PASS] PROJECT-STORY-ANTI-DOUBLE-CLEAR-IDEMPOTENCY-DESIGN'); sys.exit(0)
