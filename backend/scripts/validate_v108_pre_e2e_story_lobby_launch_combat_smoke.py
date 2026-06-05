#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v108_pre_e2e_story_lobby_launch_combat_smoke_result_v1.json')
d=json.load(open(p,encoding='utf-8'))
chk=d.get('checks') or {}
required=['story_tsx_contains_pre_battle_lobby_route','story_tsx_auto_resolve_is_not_only_path','combat_tsx_imports_combat_launch_parser','combat_tsx_contains_preview_non_authoritative_label','pre_battle_lobby_v107d_binding_still_present','backend_battle_launch_endpoint_returns_preview_echo','backend_no_db_write','backend_no_reward_grant','backend_no_progress_write','combat_route_payload_serializable']
for k in required:
    if not chk.get(k,False): print(f'FAIL check {k}'); sys.exit(1)
ss=os.path.join(R,'backend','scripts','smoke_v108_pre_story_lobby_launch_combat_binding.py')
if not os.path.isfile(ss): print('FAIL missing smoke script'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('no_db_writes','no_reward_grant','no_progress_write','no_currency_mutation'):
    if not saf.get(k,False): print(f'FAIL safety.{k}'); sys.exit(1)
for k in ('fake_PASS','validator_weakening','hiding_preview_state'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS — v108_pre E2E story/lobby/launch/combat smoke'); sys.exit(0)
