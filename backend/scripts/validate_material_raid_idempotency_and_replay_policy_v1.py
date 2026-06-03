#!/usr/bin/env python3
"""v63 Track B — Idempotency + Replay Detection validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
ID=os.path.join(ROOT,'data/design/economy/material_raid_claim_idempotency_policy_v2.json')
RP=os.path.join(ROOT,'data/design/economy/material_raid_claim_replay_detection_policy_v1.json')
MK=os.path.join(ROOT,'data/design/economy/material_raid_idempotency_replay_policy_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/373_MATERIAL_RAID_IDEMPOTENCY_AND_REPLAY_POLICY.md')
F=[]
def f(m): F.append(m)
for p in (ID,RP,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(ID):
    d=json.load(open(ID))
    if d.get('idempotency_required') is not True: f('idempotency_required must be true')
    if d.get('anti_double_claim_required') is not True: f('anti_double_claim_required must be true')
    if d.get('db_writes')!=0: f('idempotency db_writes!=0')
    kc=d.get('key_components') or []
    for k in ('user_id','server_id','material_raid_run_id','mode_id',
              'reward_table_version','preview_session_id','claim_attempt_nonce'):
        if k not in kc: f(f'key_components missing {k}')
    st=d.get('statuses') or []
    for s in ('preview_only','staged_pending','staged_committed',
              'duplicate_same_payload','duplicate_conflict',
              'rollback_required','rejected'):
        if s not in st: f(f'statuses missing {s}')
if os.path.exists(RP):
    r=json.load(open(RP))
    if r.get('replay_detection_required') is not True: f('replay_detection_required must be true')
    if r.get('db_writes')!=0: f('replay db_writes!=0')
    sigs=r.get('replay_signals') or []
    if len(sigs)<3: f('replay_signals too few')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-IDEMPOTENCY-AND-REPLAY-POLICY'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-IDEMPOTENCY-AND-REPLAY-POLICY'); sys.exit(0)
