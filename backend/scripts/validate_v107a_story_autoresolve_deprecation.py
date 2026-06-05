#!/usr/bin/env python3
"""v107A — Story auto-resolve deprecation validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'battle_launch', 'v107a_story_autoresolve_deprecation_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
cs = d.get('current_state') or {}
if cs.get('is_authoritative_combat', True): print('FAIL \u2014 current_state.is_authoritative_combat must be false (honest)'); sys.exit(1)
if not cs.get('reward_granted_directly', False): print('FAIL \u2014 current_state.reward_granted_directly must be true (honest)'); sys.exit(1)
plan = d.get('deprecation_plan') or {}
if not plan.get('target_replacement'): print('FAIL \u2014 target_replacement missing'); sys.exit(1)
if len(plan.get('replacement_flow') or []) < 4: print('FAIL \u2014 replacement_flow < 4'); sys.exit(1)
if len(plan.get('deprecation_phases') or []) < 3: print('FAIL \u2014 deprecation_phases < 3'); sys.exit(1)
if d.get('v107a_action_taken') != 'plan_documented_no_code_change_to_story_or_/story/battle': print('FAIL \u2014 v107a_action_taken wrong'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('reward_granted','progress_written','story_battle_endpoint_modified_v107a','story_tsx_modified_v107a','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print('PASS \u2014 v107A story auto-resolve deprecation (plan documented, no code change)')
sys.exit(0)
