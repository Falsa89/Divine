#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v108_pre_story_launch_path_binding_result_v1.json')
d=json.load(open(p,encoding='utf-8'))
if d.get('status')!='STORY_LAUNCH_PATH_BINDING_APPLIED_LOBBY_ROUTE_LIVE_LEGACY_AUTO_RESOLVE_LABELED_QA': print('FAIL status'); sys.exit(1)
tsx=os.path.join(R,'frontend/app/story.tsx')
c=open(tsx,encoding='utf-8').read()
for t in ('/pre-battle-lobby','Avvia battaglia','QA Auto Resolve','launchBattleViaLobby','enemy_source_type','encounter_id','v108_pre'):
    if t not in c: print(f'FAIL token {t}'); sys.exit(1)
if d.get('legacy_auto_resolve_is_only_player_facing_path',True): print('FAIL only_path'); sys.exit(1)
if d.get('legacy_auto_resolve_backend_deleted',True): print('FAIL backend_deleted'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion','reward_grant','progress_live_write','backend_route_deleted','broad_story_rewrite'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS — v108_pre story launch path binding (Avvia battaglia + QA Auto Resolve)'); sys.exit(0)
