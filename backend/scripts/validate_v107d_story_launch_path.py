#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107d_story_launch_path_result_v1.json')
d=json.load(open(p,encoding='utf-8'))
if d.get('status')!='STORY_TSX_UNCHANGED_LOBBY_BINDING_IS_LIVE_PROOF': print('FAIL status'); sys.exit(1)
if d.get('story_tsx_modified_v107d',True): print('FAIL story_modified'); sys.exit(1)
if d.get('story_battle_endpoint_modified_v107d',True): print('FAIL endpoint_modified'); sys.exit(1)
if not d.get('proof_of_launch_path'): print('FAIL proof'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('story_tsx_modified_v107d','story_battle_endpoint_modified_v107d','reward_grant','progress_live_write','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS \u2014 v107D story launch path (story.tsx untouched, lobby binding is proof)'); sys.exit(0)
