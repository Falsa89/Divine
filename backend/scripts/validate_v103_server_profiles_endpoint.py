#!/usr/bin/env python3
"""v103 — /api/server-profiles/list endpoint validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','server_profile','v103_server_profiles_endpoint_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if d.get('endpoint') != 'GET /api/server-profiles/list': print('FAIL \u2014 wrong endpoint'); sys.exit(1)
if not d.get('is_qa_fallback', False): print('FAIL \u2014 is_qa_fallback must be true'); sys.exit(1)
if d.get('is_production_data', True): print('FAIL \u2014 is_production_data must be false'); sys.exit(1)
if d.get('backend_data_isolation_implemented', True): print('FAIL \u2014 backend_data_isolation_implemented must be false (declared pending)'); sys.exit(1)
if d.get('returns_servers_count', 0) < 3: print('FAIL \u2014 returns_servers_count < 3'); sys.exit(1)
if not d.get('all_server_names_qa_prefixed', False): print('FAIL \u2014 all_server_names_qa_prefixed must be true'); sys.exit(1)
# Verifica file backend route esiste
route_file = os.path.join(ROOT,'backend','routes','v103_server_profiles.py')
if not os.path.isfile(route_file): print('FAIL \u2014 route file missing'); sys.exit(1)
with open(route_file,'r',encoding='utf-8') as f: content = f.read()
for token in ('/api/server-profiles/list','is_qa_fallback','backend_data_isolation_implemented','[QA]'):
    if token not in content: print(f'FAIL \u2014 route file missing token: {token}'); sys.exit(1)
# Verifica include_router in server.py
server_py = os.path.join(ROOT,'backend','server.py')
with open(server_py,'r',encoding='utf-8') as f: srv_content = f.read()
if 'v103_server_profiles_router' not in srv_content: print('FAIL \u2014 server.py missing v103 router include'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('read_only','no_db_writes','no_raw_token_logs','no_provider_secrets','declared_qa_fallback'):
    if not saf.get(k, False): print(f'FAIL \u2014 safety.{k} must be true'); sys.exit(1)
for k in ('fake_production_data','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v103 server profiles endpoint (read-only, qa_fallback, isolation_pending, {d['returns_servers_count']} servers)")
sys.exit(0)
