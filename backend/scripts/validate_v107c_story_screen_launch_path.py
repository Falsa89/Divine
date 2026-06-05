#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107c_story_screen_launch_path_result_v1.json')
if not os.path.isfile(p): print('FAIL'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
if d.get('status')!='STORY_TSX_UNCHANGED_LOBBY_GATED_LAUNCH_IS_PROOF': print('FAIL status'); sys.exit(1)
if d.get('story_tsx_modified_v107c',True): print('FAIL story_tsx_modified'); sys.exit(1)
if d.get('story_autoresolve_runtime_changed',True): print('FAIL story_autoresolve_runtime_changed'); sys.exit(1)
if not d.get('proof_of_launch_path'): print('FAIL proof_of_launch_path missing'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('story_tsx_modified_v107c','reward_grant','progress_live_write','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL safety.{k}'); sys.exit(1)
print('PASS \u2014 v107C story screen launch path (story.tsx unchanged, lobby gated launch is proof)'); sys.exit(0)
