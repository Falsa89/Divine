#!/usr/bin/env python3
"""v104 — Frontend server_id propagation validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v104_frontend_server_id_propagation_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
if d.get('selected_server_id_storage_key') != 'v101_selected_server_id': print('FAIL \u2014 storage key wrong'); sys.exit(1)
if d.get('hook_introduced') != 'frontend/src/hooks/useServerScope.ts': print('FAIL \u2014 hook path wrong'); sys.exit(1)
loaders = d.get('loaders_targeted') or []
if len(loaders) < 7: print(f'FAIL \u2014 loaders_targeted < 7 (got {len(loaders)})'); sys.exit(1)
for lo in loaders:
    if not lo.get('banner_obligation', False): print(f'FAIL \u2014 loader {lo.get("surface")} banner_obligation must be true'); sys.exit(1)
rg = d.get('routing_guard') or {}
if rg.get('missing_selected_server_id_redirects_to') != '/servers': print('FAIL \u2014 routing guard target wrong'); sys.exit(1)
if d.get('isolation_pending_token') != 'SERVER_DATA_ISOLATION_BACKEND_PENDING': print('FAIL \u2014 isolation_pending_token missing'); sys.exit(1)
if not d.get('no_fake_same_data_across_servers', False): print('FAIL \u2014 no_fake_same_data_across_servers must be true'); sys.exit(1)
# Verifica hook esiste e contiene il token
hook = os.path.join(ROOT, 'frontend', 'src', 'hooks', 'useServerScope.ts')
if not os.path.isfile(hook): print('FAIL \u2014 useServerScope.ts missing'); sys.exit(1)
with open(hook, 'r', encoding='utf-8') as f: hc = f.read()
for token in ('useServerScope', 'SERVER_DATA_ISOLATION_BACKEND_PENDING', 'v101_selected_server_id', 'is_isolation_pending'):
    if token not in hc: print(f'FAIL \u2014 useServerScope.ts missing token: {token}'); sys.exit(1)
# Verifica index.tsx routing guard
idx = os.path.join(ROOT, 'frontend', 'app', 'index.tsx')
with open(idx, 'r', encoding='utf-8') as f: ic = f.read()
if "router.replace('/servers')" not in ic: print('FAIL \u2014 index.tsx missing routing guard to /servers'); sys.exit(1)
if 'v101_selected_server_id' not in ic: print('FAIL \u2014 index.tsx missing v101_selected_server_id read'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_different_server_data', 'fake_PASS', 'validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v104 frontend server_id propagation ({len(loaders)} loaders documented, hook + routing guard live)")
sys.exit(0)
