#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107b_battle_launch_smoke_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 missing (run smoke_v107b_battle_launch_integration.py)'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
if not d.get('overall_pass',False): print('FAIL \u2014 smoke overall_pass must be true'); sys.exit(1)
if (d.get('cases_total') or 0)<3: print('FAIL \u2014 smoke cases_total < 3'); sys.exit(1)
if d.get('cases_pass')!=d.get('cases_total'): print('FAIL \u2014 not all cases passed'); sys.exit(1)
results=d.get('results') or []
for r in results:
    if not r.get('pass',False): print(f'FAIL \u2014 case {r.get("case")} not passed'); sys.exit(1)
    if r.get('response_status_string')!='PREVIEW_ECHO_NON_AUTHORITATIVE': print(f'FAIL \u2014 case {r.get("case")} status not preview'); sys.exit(1)
    saf=r.get('safety') or {}
    if saf.get('db_writes_performed',-1)!=0: print(f'FAIL \u2014 case {r.get("case")} db_writes != 0'); sys.exit(1)
    if saf.get('reward_granted',True): print(f'FAIL \u2014 case {r.get("case")} reward_granted'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('no_db_writes','no_reward_grant','no_progress_write','no_currency_mutation'):
    if not saf.get(k,False): print(f'FAIL \u2014 safety.{k} must be true'); sys.exit(1)
print(f"PASS \u2014 v107B battle launch smoke ({d.get('cases_pass')}/{d.get('cases_total')} preview echo)"); sys.exit(0)
