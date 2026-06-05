#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v108_pre_pre_battle_lobby_compatibility_result_v1.json')
d=json.load(open(p,encoding='utf-8'))
if d.get('status')!='PRE_BATTLE_LOBBY_STORY_PARAMS_COMPATIBLE_V107D_BINDING_PRESERVED': print('FAIL status'); sys.exit(1)
tsx=os.path.join(R,'frontend/app/pre-battle-lobby.tsx')
c=open(tsx,encoding='utf-8').read()
for t in ('launchFromLobby','preBattleLobbyAdapter','EXPO_PUBLIC_V107D_PREVIEW_LAUNCH_ENABLED','v107D','encounter_id','enemy_source_id','v108_pre'):
    if t not in c: print(f'FAIL token {t}'); sys.exit(1)
if not d.get('v107d_flag_default_off',False): print('FAIL flag'); sys.exit(1)
if not d.get('runtime_player_facing_behavior_unchanged_when_flag_off',False): print('FAIL unchanged'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion','reward_grant','progress_live_write'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS — v108_pre pre-battle-lobby compatibility (v107D binding preserved)'); sys.exit(0)
