#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107c_story_autoresolve_deprecation_guard_result_v1.json')
if not os.path.isfile(p): print('FAIL'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
cs=d.get('current_state') or {}
if not cs.get('story_battle_endpoint_active',False): print('FAIL story_battle_endpoint_active (honest)'); sys.exit(1)
if not cs.get('story_tsx_uses_auto_resolve',False): print('FAIL story_tsx_uses_auto_resolve (honest)'); sys.exit(1)
if cs.get('story_tsx_modified_v107c',True): print('FAIL story_tsx_modified_v107c'); sys.exit(1)
ph=d.get('deprecation_phases_progress') or {}
if ph.get('v107A_contract_only')!='DONE' or ph.get('v107B_adapter_helpers')!='DONE' or ph.get('v107C_tsx_binding_lobby_combat')!='DONE': print('FAIL phases'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('reward_granted','progress_written','story_battle_endpoint_modified_v107c','story_tsx_modified_v107c','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL safety.{k}'); sys.exit(1)
print('PASS \u2014 v107C story auto-resolve deprecation guard (phases DONE through v107C)'); sys.exit(0)
