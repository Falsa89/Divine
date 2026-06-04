#!/usr/bin/env python3
"""v98 — Full load/locust."""
import os, sys, json
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(ROOT,'data','design','closed_alpha','v98_full_load_locust_result_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d=json.load(f)
eps=d.get('endpoints_covered') or []
if len(eps)<10: print(f'FAIL — endpoints < 10: {len(eps)}'); sys.exit(1)
for e in eps:
    if e.get('status')!=200: print(f'FAIL — endpoint {e}'); sys.exit(1)
res=d.get('results') or {}
for k in ('no_5xx_under_load','no_token_leak_in_logs','no_unauthorized_db_writes','no_reward_live_mutation','no_score_live_mutation'):
    if not res.get(k): print(f'FAIL — results.{k}'); sys.exit(1)
if res.get('critical_errors',1)!=0: print('FAIL — critical_errors'); sys.exit(1)
script=os.path.join(ROOT,'backend','scripts','locust_v98_closed_alpha_smoke.py')
if not os.path.isfile(script): print('FAIL — locust script missing'); sys.exit(1)
print(f'PASS — v98 full load/locust ({len(eps)} endpoints, 0 critical errors)')
sys.exit(0)
