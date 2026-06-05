#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107b_pre_battle_lobby_adoption_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 missing'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
if d.get('status')!='ADAPTER_HELPER_INTRODUCED_TSX_INTEGRATION_DEFERRED': print('FAIL \u2014 status wrong'); sys.exit(1)
mod=os.path.join(R,d.get('adapter_module',''))
if not os.path.isfile(mod): print(f'FAIL \u2014 adapter missing: {mod}'); sys.exit(1)
c=open(mod,encoding='utf-8').read()
for t in ('launchFromLobby','buildLaunchContext','validateLaunchContext','POST','/api/battle/launch','preview'):
    if t not in c: print(f'FAIL \u2014 adapter missing {t}'); sys.exit(1)
for k in ('reward_policy_default','progress_policy_default','battle_engine_mode_default'):
    if d.get(k)!='preview': print(f'FAIL \u2014 {k} must be preview'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('new_player_facing_feature','combat_tsx_changes','reward_grant','progress_live_write','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL \u2014 safety.{k} false'); sys.exit(1)
print('PASS \u2014 v107B pre-battle-lobby adoption (adapter introduced, preview defaults)'); sys.exit(0)
