#!/usr/bin/env python3
"""v104 — Server profile backend runtime contract validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v104_server_profile_backend_contract_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 contract json missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
eps = d.get('endpoints') or []
paths = {e.get('path') for e in eps}
required_paths = {'/api/server-profiles/list', '/api/server-profiles/select', '/api/server-profiles/current'}
missing = required_paths - paths
if missing: print(f'FAIL \u2014 missing endpoint contracts: {missing}'); sys.exit(1)
for e in eps:
    if e.get('mutates_db', True): print(f'FAIL \u2014 endpoint {e["path"]} mutates_db must be false'); sys.exit(1)
    if not e.get('declares_qa_fallback', False): print(f'FAIL \u2014 endpoint {e["path"]} declares_qa_fallback must be true'); sys.exit(1)
    if e.get('backend_data_isolation_implemented', True): print(f'FAIL \u2014 endpoint {e["path"]} backend_data_isolation_implemented must be false'); sys.exit(1)
if d.get('isolation_state') != 'DECLARED_PENDING': print('FAIL \u2014 isolation_state must be DECLARED_PENDING'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('read_only', 'no_db_writes', 'no_raw_token_logs', 'no_provider_secrets', 'declared_qa_fallback'):
    if not saf.get(k, False): print(f'FAIL \u2014 safety.{k} must be true'); sys.exit(1)
for k in ('fake_production_data', 'fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
# Verifica esiste la route v103 (riusata in v104)
route_file = os.path.join(ROOT, 'backend', 'routes', 'v103_server_profiles.py')
if not os.path.isfile(route_file): print('FAIL \u2014 backend route file missing'); sys.exit(1)
print('PASS \u2014 v104 server profile backend contract (read-only, isolation_state=DECLARED_PENDING)')
sys.exit(0)
