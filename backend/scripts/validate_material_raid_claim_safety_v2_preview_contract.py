#!/usr/bin/env python3
"""v63 Track A — Material Raid Claim Safety v2 Preview Contract validator."""
from __future__ import annotations
import os, sys, json
ROOT='/app'
C=os.path.join(ROOT,'data/design/economy/material_raid_claim_safety_v2_preview_contract.json')
FB=os.path.join(ROOT,'data/design/economy/material_raid_claim_safety_v2_forbidden_scope.json')
MK=os.path.join(ROOT,'data/design/economy/material_raid_claim_safety_v2_preview_marker_v1.json')
DOC=os.path.join(ROOT,'docs/divine/372_MATERIAL_RAID_CLAIM_SAFETY_v2_PREVIEW_CONTRACT.md')
TAG='PUBLIC_SYNC_TAG_v63_MEGA_RELEASE_ACCELERATION_12_MATERIAL_RAID_CLAIM_SAFETY_AND_STAGING_BLUEPRINT'
F=[]
def f(m): F.append(m)
for p in (C,FB,MK,DOC):
    if not os.path.exists(p): f(f'missing {p}')
if os.path.exists(C):
    d=json.load(open(C))
    must={'design_only':True,'preview_only':True,'live_claim_enabled':False,
          'claim_button_enabled':False,'reward_grant_enabled':False,
          'materials_granted':False,'inventory_mutation':False,'wallet_mutation':False,
          'premium_users_gems_mutation':False,'db_writes':0,'real_db_writes':0,
          'backend_route_enabled':False,'battle_engine_runtime_used':False,
          'result_authoritative':False,'idempotency_required':True,
          'anti_double_claim_required':True,'ledger_required_before_live':True,
          'rollback_required_before_live':True,'manual_approval_required':True,
          'future_live_pack_required':True,'future_live_pack_minimum':'v65',
          'mongo_url_used':False,'pymongo_used':False,'motor_used':False,'redis_used':False,
          'fake_pass':False,'validator_weakening':False}
    for k,v in must.items():
        if d.get(k)!=v: f(f'contract {k}!={v} (got {d.get(k)})')
    if d.get('public_sync_tag')!=TAG: f('contract public_sync_tag mismatch')
if os.path.exists(FB):
    fb=json.load(open(FB))
    if fb.get('design_only') is not True: f('forbidden_scope design_only!=true')
    if fb.get('db_writes')!=0: f('forbidden_scope db_writes!=0')
    forb=fb.get('forbidden') or []
    needed=['live_claim','reward_grant','inventory_mutation','wallet_mutation',
            'premium_users_gems_mutation','backend_route_enablement','server_py_change',
            'battle_engine_change','combat_tsx_change','story_tsx_change',
            'api_story_battle_change','api_battle_simulate_change','gacha_rate_change',
            'guild_war_policy_regression','character_bible_change','final_numbers_change',
            'home_menu_mandatory_routing','asset_copy_or_import','real_mongo_use',
            'real_redis_use','validator_weakening','fake_pass']
    for n in needed:
        if n not in forb: f(f'forbidden_scope missing {n}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] PROJECT-MATERIAL-RAID-CLAIM-SAFETY-v2-PREVIEW-CONTRACT'); sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-CLAIM-SAFETY-v2-PREVIEW-CONTRACT'); sys.exit(0)
