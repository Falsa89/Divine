#!/usr/bin/env python3
"""v102 — Selected server persistence validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','server_select','v102_selected_server_persistence_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
keys = d.get('storage_keys') or {}
if 'v101_selected_server_id' not in keys: print('FAIL \u2014 storage_keys.v101_selected_server_id missing'); sys.exit(1)
if keys['v101_selected_server_id'].get('storage') != 'AsyncStorage': print('FAIL \u2014 v101_selected_server_id must be AsyncStorage'); sys.exit(1)
stoken = d.get('session_token_storage') or {}
if not stoken.get('NOT_in_AsyncStorage', False): print('FAIL \u2014 session_token must NOT be in plain AsyncStorage (v96 SecureStore)'); sys.exit(1)
rb = d.get('required_behavior') or {}
for k in ('app_start_no_session','app_start_session_no_selected_server','app_start_session_with_selected_server','cambia_server_in_menu','logout_account_in_menu'):
    if k not in rb: print(f'FAIL \u2014 required_behavior.{k} missing'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('token_in_AsyncStorage','raw_oauth_log','provider_secrets','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v102 selected server persistence ({len(keys)} keys, behavior matrix complete)")
sys.exit(0)
