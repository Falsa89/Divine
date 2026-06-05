#!/usr/bin/env python3
"""v102 — Server list source contract validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','server_select','v102_server_list_source_contract_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
for k in ('preferred_source','fallback_source','payload_contract','fallback_payload_sample'):
    if k not in d: print(f'FAIL \u2014 {k} missing'); sys.exit(1)
payload = d['payload_contract']
required_fields = ('server_id','server_name','region','status','can_enter')
for f in required_fields:
    if f not in payload: print(f'FAIL \u2014 payload_contract.{f} missing'); sys.exit(1)
fb = d['fallback_source']
if fb.get('contains_real_user_data', True): print('FAIL \u2014 fallback contains_real_user_data must be false'); sys.exit(1)
if fb.get('fake_real_profile_data', True): print('FAIL \u2014 fake_real_profile_data must be false'); sys.exit(1)
if not fb.get('declared_in_ui', False): print('FAIL \u2014 declared_in_ui must be true'); sys.exit(1)
if len(d.get('fallback_payload_sample', [])) < 3: print('FAIL \u2014 fallback_payload_sample < 3'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_server_profile_real_data','hardcoding_as_production_if_fallback','token_raw_logs','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v102 server list source ({len(payload)} fields, {len(d['fallback_payload_sample'])} fallback servers)")
sys.exit(0)
