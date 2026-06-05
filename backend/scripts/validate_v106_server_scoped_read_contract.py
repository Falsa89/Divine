#!/usr/bin/env python3
"""v106 — Server-scoped read contract validator (for v107+)."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v106_server_scoped_read_contract_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
eps = d.get('endpoints') or []
if len(eps) < 8: print(f'FAIL \u2014 endpoints < 8 (got {len(eps)})'); sys.exit(1)
required_paths = {'/api/server-profiles/current','/api/user/heroes','/api/team/get-formation','/api/inventory','/api/currencies','/api/chat/messages','/api/arena/profile'}
present = {e.get('path') for e in eps}
missing = required_paths - present
if missing: print(f'FAIL \u2014 missing endpoint contracts {missing}'); sys.exit(1)
for e in eps:
    if not e.get('filter_required'): print(f'FAIL \u2014 endpoint {e.get("path")} filter_required missing'); sys.exit(1)
    if e.get('status') not in ('contract_only','implemented'): print(f'FAIL \u2014 endpoint {e.get("path")} status invalid'); sys.exit(1)
# Validation rules and fallback
if len(d.get('server_id_validation_rules') or []) < 3: print('FAIL \u2014 server_id_validation_rules < 3'); sys.exit(1)
fb = d.get('fallback_when_flag_disabled') or {}
if fb.get('banner_obligation') != 'SERVER_DATA_ISOLATION_BACKEND_PENDING (v104)': print('FAIL \u2014 fallback banner_obligation token missing'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('no_implementation_yet','no_db_writes'):
    if not saf.get(k, False): print(f'FAIL \u2014 safety.{k} must be true'); sys.exit(1)
for k in ('fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v106 server-scoped read contract ({len(eps)} endpoints defined)")
sys.exit(0)
