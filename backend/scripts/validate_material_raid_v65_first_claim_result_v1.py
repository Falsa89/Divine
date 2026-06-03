#!/usr/bin/env python3
"""v65 Track D — First Claim Result (apply OR blocked) validator.

Exactly one of {apply_result, blocked_result} must exist. We accept BOTH
paths but blocked-safe is mandatory when no isolated staging is present.
"""
from __future__ import annotations
import os, sys, json
ROOT='/app'
APPLY=os.path.join(ROOT,'data/design/economy/material_raid_v65_first_controlled_live_staging_claim_apply_result_v1.json')
BLOCKED=os.path.join(ROOT,'data/design/economy/material_raid_v65_first_controlled_live_staging_claim_blocked_result_v1.json')
MK=os.path.join(ROOT,'data/design/economy/material_raid_v65_first_claim_result_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/388_MATERIAL_RAID_v65_FIRST_CONTROLLED_LIVE_STAGING_CLAIM.md')
F=[]
def f(m): F.append(m)
for p in (MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if not (os.path.exists(APPLY) or os.path.exists(BLOCKED)):
    f('neither apply_result nor blocked_result exists')
if os.path.exists(APPLY):
    d=json.load(open(APPLY))
    if d.get('applied') is not True: f('apply_result applied!=true (but file exists)')
    if d.get('total_claim_cap')!=10: f('apply_result total_claim_cap!=10')
    if d.get('per_user_claim_cap')!=1: f('apply_result per_user_claim_cap!=1')
    if d.get('material_only_reward') is not True: f('apply_result material_only_reward!=true')
    if d.get('premium_currency_granted') is not False: f('apply_result premium_currency_granted!=false')
    if d.get('gacha_currency_granted') is not False: f('apply_result gacha_currency_granted!=false')
if os.path.exists(BLOCKED):
    d=json.load(open(BLOCKED))
    if d.get('applied') is not False: f('blocked_result applied!=false')
    if (d.get('db_writes') or 0) != 0: f('blocked_result db_writes!=0')
    if d.get('reward_grant_executed') is not False: f('blocked_result reward_grant_executed!=false')
    if d.get('materials_granted') is not False: f('blocked_result materials_granted!=false')
    if d.get('premium_currency_granted') is not False: f('blocked_result premium_currency_granted!=false')
    if not d.get('reason'): f('blocked_result missing reason')
    if 'failed_gate' not in d: f('blocked_result missing failed_gate field')
    if 'BLOCKED_NOT_APPLIED_SAFE' not in (d.get('verdict') or ''):
        f('blocked_result verdict not BLOCKED_NOT_APPLIED_SAFE')
    if d.get('approval_phrase_received')!='approvo':
        f('blocked_result approval_phrase_received!=approvo')
    if d.get('approval_checksum_verified') is not True:
        f('blocked_result approval_checksum_verified!=true')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-v65-FIRST-CLAIM-RESULT'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-v65-FIRST-CLAIM-RESULT'); sys.exit(0)
