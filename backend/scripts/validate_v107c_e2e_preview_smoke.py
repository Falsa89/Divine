#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107c_e2e_preview_smoke_result_v1.json')
if not os.path.isfile(p): print('FAIL missing (run smoke_v107c_story_lobby_launch_combat_preview.py)'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
if not d.get('overall_pass',False): print('FAIL overall_pass'); sys.exit(1)
if d.get('steps_pass')!=d.get('steps_total'): print('FAIL steps_pass != total'); sys.exit(1)
results=d.get('results') or []
if len(results)<2: print('FAIL results<2'); sys.exit(1)
for r in results:
    if not r.get('pass',False): print(f'FAIL step {r.get("step")} not pass'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('no_db_writes','no_reward_grant','no_progress_write','no_currency_mutation'):
    if not saf.get(k,False): print(f'FAIL safety.{k}'); sys.exit(1)
for k in ('fake_PASS','validator_weakening','hiding_preview_state'):
    if saf.get(k,True): print(f'FAIL safety.{k}'); sys.exit(1)
print(f"PASS \u2014 v107C e2e preview smoke ({d.get('steps_pass')}/{d.get('steps_total')} steps)"); sys.exit(0)
