#!/usr/bin/env python3
"""v98 — Bot progression runtime/simulator."""
import os, sys, json
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(ROOT,'data','design','server_actors','v98_bot_progression_runtime_result_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d=json.load(f)
if d.get('runtime_mode')!='DRY_RUN_ONLY': print('FAIL — runtime_mode'); sys.exit(1)
if d.get('db_writes_during_simulation',1)!=0: print('FAIL — db_writes'); sys.exit(1)
sim=d.get('simulated_features') or {}
for k in ('daily_activity','account_exp','roster_growth','pull_history_simulation','reward_accumulation_controlled','team_upgrades','event_unlock_progression'):
    if not sim.get(k): print(f'FAIL — sim.{k}'); sys.exit(1)
caps=d.get('caps_enforced') or {}
for k in ('max_level_by_server_age','p95_cap','top3_domination_forbidden','day_one_high_level_forbidden'):
    if not caps.get(k): print(f'FAIL — cap {k}'); sys.exit(1)
for f in ('real_iap','economy_exploit','premium_currency_inflation','hidden_advantage_over_players','premium_reward_theft','random_opponent_generation'):
    if f not in (d.get('forbidden_runtime') or []): print(f'FAIL — forbidden missing: {f}'); sys.exit(1)
script=os.path.join(ROOT,'backend','scripts','simulate_v98_bot_progression_runtime.py')
if not os.path.isfile(script): print('FAIL — simulator script missing'); sys.exit(1)
print('PASS — v98 bot progression runtime (dry-run gated)')
sys.exit(0)
