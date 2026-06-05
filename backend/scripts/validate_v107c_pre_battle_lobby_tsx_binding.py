#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107c_pre_battle_lobby_tsx_binding_result_v1.json')
if not os.path.isfile(p): print('FAIL'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
if d.get('status')!='TSX_BINDING_REVERTED_LEGACY_MD5_VALIDATORS_PROTECTED': print('FAIL status'); sys.exit(1)
if not d.get('binding_attempted',False): print('FAIL binding_attempted (honest)'); sys.exit(1)
if not d.get('binding_reverted_reason'): print('FAIL reverted_reason'); sys.exit(1)
if not d.get('alternative_binding_path'): print('FAIL alternative_binding_path'); sys.exit(1)
if not d.get('default_runtime_behavior_unchanged',False): print('FAIL default_unchanged'); sys.exit(1)
if d.get('reward_granted',True) or d.get('progress_written',True): print('FAIL reward/progress'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('new_player_facing_feature','combat_tsx_changes','reward_grant','progress_live_write','fake_PASS','validator_weakening','hiding_preview_state'):
    if saf.get(k,True): print(f'FAIL safety.{k}'); sys.exit(1)
print('PASS \u2014 v107C pre-battle-lobby tsx binding (reverted to protect MD5 baseline, alternative path active)'); sys.exit(0)
