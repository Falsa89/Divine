#!/usr/bin/env python3
"""v63 Track D — Rollback + Manual Approval + Canary Scope validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
RB=os.path.join(ROOT,'data/design/economy/material_raid_claim_rollback_compensation_plan_v1.json')
MA=os.path.join(ROOT,'data/design/economy/material_raid_claim_manual_approval_matrix_v1.json')
CN=os.path.join(ROOT,'data/design/economy/material_raid_claim_canary_scope_matrix_v1.json')
MK=os.path.join(ROOT,'data/design/economy/material_raid_rollback_manual_approval_canary_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/375_MATERIAL_RAID_ROLLBACK_MANUAL_APPROVAL_CANARY_SCOPE.md')
F=[]
def f(m): F.append(m)
for p in (RB,MA,CN,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(RB):
    d=json.load(open(RB))
    for k,v in (('design_only',True),('rollback_required',True),
                ('rollback_test_required_before_live',True),
                ('compensation_required_if_partial_grant',True),
                ('db_writes',0)):
        if d.get(k)!=v: f(f'rollback {k}!={v} (got {d.get(k)})')
    steps=d.get('rollback_steps') or []
    if len(steps)<4: f('rollback_steps too few')
if os.path.exists(MA):
    m=json.load(open(MA))
    for k,v in (('manual_approval_required',True),('approval_phrase_required',True),
                ('checksum_required',True),('db_writes',0)):
        if m.get(k)!=v: f(f'approval {k}!={v}')
    gates=m.get('approval_gates') or []
    if len(gates)<3: f('approval_gates too few')
if os.path.exists(CN):
    c=json.load(open(CN))
    if c.get('canary_user_allowlist_required') is not True:
        f('canary_user_allowlist_required must be true')
    if c.get('db_writes')!=0: f('canary db_writes!=0')
    lim=c.get('canary_limits') or {}
    if lim.get('material_raid_only') is not True: f('canary material_raid_only must be true')
    if lim.get('max_users_first_wave_min')!=1: f('canary min!=1')
    if lim.get('max_users_first_wave_max')!=5: f('canary max!=5')
    if lim.get('max_claims_per_user')!=1: f('canary max_claims_per_user!=1')
    if lim.get('max_total_claims_first_wave')!=10: f('canary max_total!=10')
    if lim.get('premium_currency_allowed') is not False:
        f('canary premium_currency_allowed must be false')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-ROLLBACK-MANUAL-APPROVAL-CANARY-SCOPE'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-ROLLBACK-MANUAL-APPROVAL-CANARY-SCOPE'); sys.exit(0)
