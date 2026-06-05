#!/usr/bin/env python3
"""v103 — Server selection persistence validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','server_profile','v103_server_selection_persistence_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
keys = d.get('persistence_keys') or {}
for k in ('v101_selected_server_id','v102_selected_server_name','v103_logout_in_progress'):
    if k not in keys: print(f'FAIL \u2014 persistence_keys.{k} missing'); sys.exit(1)
if keys['v103_logout_in_progress'].get('purpose','').find('logout race') < 0:
    print('FAIL \u2014 v103_logout_in_progress purpose not documented'); sys.exit(1)
if not d.get('persistence_robust', False): print('FAIL \u2014 persistence_robust must be true'); sys.exit(1)
for k in ('app_start_no_session_routes_to_login','app_start_session_no_selected_server_routes_to_servers','app_start_session_with_selected_server_routes_to_home','cambia_server_does_not_clear_session'):
    if not d.get(k, False): print(f'FAIL \u2014 {k} must be true'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('token_in_AsyncStorage','raw_oauth_log','provider_secrets','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v103 server selection persistence ({len(keys)} keys, behavior matrix complete)")
sys.exit(0)
