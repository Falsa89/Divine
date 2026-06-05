#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107b_story_to_lobby_routing_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 missing'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
if d.get('status')!='ROUTING_PLAN_DOCUMENTED_NO_CODE_CHANGE_v107B': print('FAIL \u2014 status wrong'); sys.exit(1)
cs=d.get('current_state') or {}
if cs.get('story_tsx_modified_v107b',True): print('FAIL \u2014 story_tsx_modified_v107b must be false'); sys.exit(1)
if cs.get('story_calls_battle_launch_endpoint',True): print('FAIL \u2014 story_calls_battle_launch_endpoint must be false'); sys.exit(1)
flow=d.get('target_flow') or []
if len(flow)<5: print('FAIL \u2014 target_flow < 5 steps'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('reward_granted','progress_written','story_tsx_modified_v107b','battle_engine_modified','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL \u2014 safety.{k} false'); sys.exit(1)
print('PASS \u2014 v107B story-to-lobby routing (plan documented, no code change)'); sys.exit(0)
