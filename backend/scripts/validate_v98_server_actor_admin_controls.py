#!/usr/bin/env python3
"""v98 — Admin runtime controls."""
import os, sys, json, urllib.request
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(ROOT,'data','design','server_actors','v98_server_actor_admin_runtime_controls_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d=json.load(f)
if d.get('endpoint_implemented')!='GET /api/admin/server-actors/status': print('FAIL — endpoint'); sys.exit(1)
ks=d.get('kill_switches') or {}
for k in ('DISABLE_ALL_BOTS','DISABLE_BOT_CHAT','DISABLE_BOT_LIVE_EVENT_FILL','DISABLE_BOT_RANKING_VISIBILITY','BOT_POWER_PERCENTILE_CAP','BOT_LOW_POP_FILL_ENABLED'):
    if k not in ks: print(f'FAIL — kill switch missing: {k}'); sys.exit(1)
# live runtime check
try:
    with urllib.request.urlopen(os.environ.get('V98_BASE_URL','http://localhost:8001')+'/api/admin/server-actors/status',timeout=5) as r:
        ad=json.loads(r.read().decode('utf-8'))
        if not ad.get('mass_creation_protection'): print('FAIL — mass_creation_protection runtime'); sys.exit(1)
        if ad.get('mutation_allowed',True): print('FAIL — mutation_allowed must be false'); sys.exit(1)
except Exception as e: print(f'FAIL — admin endpoint: {e}'); sys.exit(1)
print(f'PASS — v98 admin controls ({len(ks)} kill switches)')
sys.exit(0)
