#!/usr/bin/env python3
"""v103 — Server-scoped data isolation validator (declared pending)."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','server_profile','v103_server_scoped_data_isolation_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if d.get('backend_isolation_implemented', True): print('FAIL \u2014 backend_isolation_implemented must be false (declared pending)'); sys.exit(1)
if d.get('status') != 'DECLARED_PENDING': print('FAIL \u2014 status not DECLARED_PENDING'); sys.exit(1)
if len(d.get('loaders_audited', [])) < 5: print('FAIL \u2014 loaders_audited < 5'); sys.exit(1)
if len(d.get('per_server_data_implementations_required_v104', [])) < 3: print('FAIL \u2014 per_server_data_implementations required < 3'); sys.exit(1)
if not d.get('ui_declares_isolation_pending', False): print('FAIL \u2014 ui_declares_isolation_pending must be true'); sys.exit(1)
if d.get('fake_per_server_profile_data', True): print('FAIL \u2014 fake_per_server_profile_data must be false'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_different_per_server_profiles','fake_PASS','validator_weakening','db_destructive_writes'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v103 server-scoped data isolation (DECLARED_PENDING honest, {len(d['loaders_audited'])} loaders audited)")
sys.exit(0)
