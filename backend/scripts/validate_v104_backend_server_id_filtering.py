#!/usr/bin/env python3
"""v104 — Backend API server_id filtering audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v104_backend_server_id_filtering_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
eps = d.get('endpoints_audited') or []
if len(eps) < 6: print(f'FAIL \u2014 endpoints_audited < 6 (got {len(eps)})'); sys.exit(1)
allowed_status = {'NOT_SERVER_SCOPED', 'BACKEND_PENDING', 'OK_READONLY_FALLBACK', 'IMPLEMENTED'}
for e in eps:
    if e.get('status') not in allowed_status: print(f'FAIL \u2014 endpoint {e.get("endpoint")} invalid status {e.get("status")}'); sys.exit(1)
if d.get('verdict') != 'BACKEND_FILTERING_NOT_IMPLEMENTED_DECLARED_PENDING': print('FAIL \u2014 verdict not BACKEND_FILTERING_NOT_IMPLEMENTED_DECLARED_PENDING'); sys.exit(1)
if not d.get('no_fake_isolation', False): print('FAIL \u2014 no_fake_isolation must be true'); sys.exit(1)
if len(d.get('path_forward') or []) < 2: print('FAIL \u2014 path_forward must have >=2 entries'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('db_destructive_writes', 'blind_migration', 'fake_different_server_data', 'fake_PASS', 'validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v104 backend server_id filtering audit ({len(eps)} endpoints, isolation declared pending)")
sys.exit(0)
