#!/usr/bin/env python3
"""v104 — Canonical / QA server naming validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v104_server_naming_canonicalization_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
if d.get('prefix') != '[QA] ': print('FAIL \u2014 prefix must be [QA] '); sys.exit(1)
if not d.get('all_fallback_names_prefixed_qa', False): print('FAIL \u2014 all_fallback_names_prefixed_qa must be true'); sys.exit(1)
if d.get('misleading_names_present', True): print('FAIL \u2014 misleading_names_present must be false'); sys.exit(1)
if d.get('fake_full_or_recommended_to_attract_clicks', True): print('FAIL \u2014 fake_full_or_recommended must be false'); sys.exit(1)
if d.get('fake_production_server_status', True): print('FAIL \u2014 fake_production_server_status must be false'); sys.exit(1)
servers = d.get('servers') or []
if len(servers) < 3: print(f'FAIL \u2014 servers < 3 (got {len(servers)})'); sys.exit(1)
for s in servers:
    if not s.get('server_name', '').startswith('[QA] '): print(f'FAIL \u2014 {s.get("server_id")} not [QA] prefixed'); sys.exit(1)
    if not s.get('is_qa', False): print(f'FAIL \u2014 {s.get("server_id")} is_qa must be true'); sys.exit(1)
if not d.get('ui_banner_visible', False): print('FAIL \u2014 ui_banner_visible must be true'); sys.exit(1)
if d.get('ui_banner_line2_contains_token') != 'SERVER_DATA_ISOLATION_BACKEND_PENDING': print('FAIL \u2014 banner line2 must contain isolation pending token'); sys.exit(1)
# Runtime check
srv_tsx = os.path.join(ROOT, 'frontend', 'app', 'servers.tsx')
with open(srv_tsx, 'r', encoding='utf-8') as f: content = f.read()
for token in ('[QA] Aurora', 'LISTA SERVER QA/FALLBACK', 'SERVER_DATA_ISOLATION_BACKEND_PENDING'):
    if token not in content: print(f'FAIL \u2014 servers.tsx missing token: {token}'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_production_server_data', 'fake_PASS', 'validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v104 server naming canonicalization ({len(servers)} [QA] servers, banner token present)")
sys.exit(0)
