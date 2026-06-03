#!/usr/bin/env python3
"""v65 Track A — Approval Handshake + Scope Lock validator."""
from __future__ import annotations
import os, sys, json, hashlib
ROOT='/app'
H=os.path.join(ROOT,'data/design/economy/material_raid_v65_user_approval_handshake_v1.json')
S=os.path.join(ROOT,'data/design/economy/material_raid_v65_approval_scope_lock_v1.json')
MK=os.path.join(ROOT,'data/design/economy/material_raid_v65_approval_handshake_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/386_MATERIAL_RAID_v65_APPROVAL_HANDSHAKE_AND_SCOPE_LOCK.md')
SCOPE=('v65|material_raid_only|material_only_reward|allowlist_1_to_5|'
       'max_1_claim_per_user|max_10_total_claims|premium_currency_allowed_false|'
       'no_gacha_no_shop_no_vip_no_bp|rollback_required|observation_required')
EXPECTED='f67336fc69a7a4a2bf46fd31f3ae0fb871521c261f1f3c43dd457511ca81f137'
F=[]
def f(m): F.append(m)
for p in (H,S,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
# Verify checksum reproducibility
comp=hashlib.sha256(f'approvo|{SCOPE}'.encode()).hexdigest()
if comp!=EXPECTED: f(f'self-check checksum drift: got {comp}')
if os.path.exists(H):
    d=json.load(open(H))
    for k,v in (('approval_phrase_received','approvo'),
                ('approval_checksum_sha256',EXPECTED),
                ('manual_approval_required',True),('manual_approval_received',True),
                ('checksum_required',True),('checksum_verified',True),
                ('db_writes',0),('reward_grant_executed',False),
                ('live_apply_allowed',False),('broad_rollout_allowed',False),
                ('public_claim_allowed',False),('fake_pass',False)):
        if d.get(k)!=v: f(f'handshake {k}!={v}')
    if d.get('approval_scope')!=SCOPE: f('handshake approval_scope mismatch')
if os.path.exists(S):
    d=json.load(open(S))
    for k,v in (('scope_locked',True),('material_raid_only',True),
                ('material_only_reward',True),('max_allowlisted_users',5),
                ('max_claims_per_user',1),('max_total_claims',10),
                ('premium_currency_allowed',False),('gacha_currency_allowed',False),
                ('shop_mutation_allowed',False),('vip_mutation_allowed',False),
                ('battle_pass_mutation_allowed',False),
                ('broad_rollout_allowed',False),('public_claim_allowed',False)):
        if d.get(k)!=v: f(f'scope_lock {k}!={v}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-v65-APPROVAL-HANDSHAKE'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-v65-APPROVAL-HANDSHAKE'); sys.exit(0)
