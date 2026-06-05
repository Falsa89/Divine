#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107b_story_autoresolve_guard_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 missing'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
cs=d.get('current_state') or {}
if not cs.get('story_battle_endpoint_active',False): print('FAIL \u2014 current_state.story_battle_endpoint_active must be true (honest)'); sys.exit(1)
if not cs.get('story_tsx_uses_auto_resolve',False): print('FAIL \u2014 current_state.story_tsx_uses_auto_resolve must be true (honest)'); sys.exit(1)
guard=d.get('guard_in_place') or {}
if not guard.get('v107a_contract_only',False): print('FAIL \u2014 guard.v107a_contract_only must be true'); sys.exit(1)
if not guard.get('v107b_adapter_helpers_introduced',False): print('FAIL \u2014 guard.v107b_adapter_helpers_introduced must be true'); sys.exit(1)
if not guard.get('v107b_no_runtime_change_to_story_battle',False): print('FAIL \u2014 guard.v107b_no_runtime_change must be true'); sys.exit(1)
phases=d.get('deprecation_phases_progress') or {}
if phases.get('v107A_contract_only')!='DONE': print('FAIL \u2014 v107A phase must be DONE'); sys.exit(1)
if phases.get('v107B_adapter_helpers')!='DONE': print('FAIL \u2014 v107B phase must be DONE'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('reward_granted','progress_written','story_battle_endpoint_modified_v107b','story_tsx_modified_v107b','fake_PASS','validator_weakening'):
    if saf.get(k,True): print(f'FAIL \u2014 safety.{k} false'); sys.exit(1)
print('PASS \u2014 v107B story auto-resolve guard (helpers DONE, runtime unchanged)'); sys.exit(0)
