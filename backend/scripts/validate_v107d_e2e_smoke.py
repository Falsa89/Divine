#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107d_e2e_smoke_result_v1.json')
d=json.load(open(p,encoding='utf-8'))
if not d.get('reuses_v107c_smoke',False): print('FAIL reuses'); sys.exit(1)
if not d.get('v107c_smoke_overall_pass',False): print('FAIL v107c overall'); sys.exit(1)
if d.get('v107c_smoke_cases_pass')!=d.get('v107c_smoke_cases_total'): print('FAIL counts'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('no_db_writes','no_reward_grant','no_progress_write','no_currency_mutation'):
    if not saf.get(k,False): print(f'FAIL safety.{k}'); sys.exit(1)
for k in ('fake_PASS','validator_weakening','hiding_preview_state'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS \u2014 v107D e2e smoke (reuses v107C 2/2 PASS)'); sys.exit(0)
