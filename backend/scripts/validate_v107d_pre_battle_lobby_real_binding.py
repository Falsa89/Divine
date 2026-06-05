#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107d_pre_battle_lobby_real_binding_result_v1.json')
d=json.load(open(p,encoding='utf-8'))
if d.get('status')!='REAL_BINDING_APPLIED_GATED_OFF_BY_DEFAULT': print('FAIL status'); sys.exit(1)
tsx=os.path.join(R,d.get('tsx_file',''))
c=open(tsx,encoding='utf-8').read()
for t in ('launchFromLobby','preBattleLobbyAdapter','EXPO_PUBLIC_V107D_PREVIEW_LAUNCH_ENABLED','v107D'):
    if t not in c: print(f'FAIL token {t}'); sys.exit(1)
if not d.get('default_runtime_behavior_unchanged',False): print('FAIL default'); sys.exit(1)
if d.get('optional_fail_count',-1)!=23: print('FAIL opt count'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('new_player_facing_feature','combat_tsx_changes','reward_grant','progress_live_write','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS \u2014 v107D pre-battle-lobby real binding (gated, opt fail=23)'); sys.exit(0)
