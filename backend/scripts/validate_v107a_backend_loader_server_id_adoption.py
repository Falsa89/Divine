#!/usr/bin/env python3
"""v107A — Backend loader server_id adoption validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v107a_backend_loader_server_id_adoption_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
if d.get('feature_flag') != 'SERVER_SCOPED_RUNTIME_ENABLED': print('FAIL \u2014 feature_flag name wrong'); sys.exit(1)
if d.get('feature_flag_default', True): print('FAIL \u2014 feature_flag_default must be false'); sys.exit(1)
if d.get('adoption_status') != 'CONTRACT_ONLY_LOADER_CHANGE_DEFERRED_TO_v107B': print('FAIL \u2014 adoption_status wrong'); sys.exit(1)
eps = d.get('endpoints_targeted') or []
if len(eps) < 7: print(f'FAIL \u2014 endpoints_targeted < 7 (got {len(eps)})'); sys.exit(1)
for e in eps:
    if e.get('current_accepts_server_id', True): print(f'FAIL \u2014 {e.get("endpoint")} current_accepts_server_id must be false'); sys.exit(1)
    if not e.get('target_behavior_when_flag_on'): print(f'FAIL \u2014 {e.get("endpoint")} target_behavior missing'); sys.exit(1)
    if not e.get('adoption_pack'): print(f'FAIL \u2014 {e.get("endpoint")} adoption_pack missing'); sys.exit(1)
if d.get('backend_isolation_live', True): print('FAIL \u2014 backend_isolation_live must be false'); sys.exit(1)
if d.get('backend_claims_isolation_live', True): print('FAIL \u2014 backend_claims_isolation_live must be false'); sys.exit(1)
if d.get('banner_token') != 'SERVER_DATA_ISOLATION_BACKEND_PENDING': print('FAIL \u2014 banner_token wrong'); sys.exit(1)
saf = d.get('safety') or {}
if saf.get('db_writes_performed', -1) != 0: print('FAIL \u2014 safety.db_writes_performed must be 0'); sys.exit(1)
if saf.get('loader_endpoints_modified_v107a', -1) != 0: print('FAIL \u2014 safety.loader_endpoints_modified_v107a must be 0'); sys.exit(1)
for k in ('fake_isolation_live','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v107A backend loader server_id adoption ({len(eps)} endpoints documented contract-only)")
sys.exit(0)
