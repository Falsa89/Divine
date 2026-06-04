#!/usr/bin/env python3
"""v98 — Server actor runtime persistence."""
import os, sys, json, urllib.request
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(ROOT,'data','design','server_actors','v98_server_actor_runtime_persistence_result_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d=json.load(f)
if d.get('collection')!='server_actors': print('FAIL — collection'); sys.exit(1)
schema=d.get('schema') or {}
for k in ('actor_id','is_bot','synthetic_server_actor','bot_archetype','account_level','roster_snapshot','runtime_enabled','created_by_system'):
    if k not in schema: print(f'FAIL — schema missing: {k}'); sys.exit(1)
rules=d.get('rules_enforced') or {}
for k in ('start_level_1','respect_server_age_cap','cap_p95','no_top3_domination','no_premium_reward_theft','no_real_iap','no_day_one_high_level','event_access_requires_unlock'):
    if not rules.get(k): print(f'FAIL — rule {k} not enforced'); sys.exit(1)
if d.get('gating',{}).get('default',True)!=False: print('FAIL — gating default should be false'); sys.exit(1)
if d.get('safety',{}).get('db_writes',1)!=0: print('FAIL — db_writes!=0'); sys.exit(1)
# verify admin endpoint live
try:
    with urllib.request.urlopen(os.environ.get('V98_BASE_URL','http://localhost:8001')+'/api/admin/server-actors/status',timeout=5) as r:
        if r.status!=200: print(f'FAIL — admin endpoint status {r.status}'); sys.exit(1)
        ad=json.loads(r.read().decode('utf-8'))
        if not ad.get('v98_server_actors'): print('FAIL — admin endpoint missing v98 flag'); sys.exit(1)
except Exception as e: print(f'FAIL — admin endpoint error: {e}'); sys.exit(1)
print('PASS — v98 server actor runtime persistence (gated, default off)')
sys.exit(0)
