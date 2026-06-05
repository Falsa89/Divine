#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','closed_alpha','v107d_tsx_md5_supersede_review_v1.json')
d=json.load(open(p,encoding='utf-8'))
lobby=d.get('pre_battle_lobby_tsx') or {}
combat=d.get('combat_tsx') or {}
if not lobby.get('v107D_modified',False): print('FAIL lobby_modified'); sys.exit(1)
if combat.get('v107D_modified',True): print('FAIL combat_modified'); sys.exit(1)
if len(combat.get('validators_to_supersede_v108_pre') or [])<10: print('FAIL supersede list<10'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('silent_validator_deletion','validator_weakening','fake_PASS'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS \u2014 v107D tsx MD5 supersede review'); sys.exit(0)
