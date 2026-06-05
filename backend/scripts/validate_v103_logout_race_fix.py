#!/usr/bin/env python3
"""v103 — Logout race fix validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','auth','v103_logout_race_fix_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
fix = d.get('fix_applied') or {}
if fix.get('flag_key') != 'v103_logout_in_progress': print('FAIL \u2014 flag_key wrong'); sys.exit(1)
if not fix.get('v96_securestore_explicit_clear', False): print('FAIL \u2014 v96_securestore_explicit_clear must be true'); sys.exit(1)
if len(fix.get('v96_keys_cleared', [])) < 2: print('FAIL \u2014 v96_keys_cleared < 2'); sys.exit(1)
if len(fix.get('legacy_keys_cleared', [])) < 3: print('FAIL \u2014 legacy_keys_cleared < 3'); sys.exit(1)
if fix.get('final_route') != "router.replace('/')": print('FAIL \u2014 final_route not /'); sys.exit(1)
if len(d.get('sequence_diagram', [])) < 6: print('FAIL \u2014 sequence_diagram < 6 steps'); sys.exit(1)
exp = d.get('expected_behavior_post_v103') or {}
for k in ('logout_routes_to_login_immediately','no_bounce_back_to_servers','no_bounce_back_to_home','kill_restart_stays_on_login'):
    if not exp.get(k, False): print(f'FAIL \u2014 expected_behavior.{k} must be true'); sys.exit(1)
# Runtime check on index.tsx + menu.tsx
index_tsx = os.path.join(ROOT,'frontend','app','index.tsx')
menu_tsx = os.path.join(ROOT,'frontend','app','(tabs)','menu.tsx')
with open(index_tsx,'r',encoding='utf-8') as f: idx = f.read()
with open(menu_tsx,'r',encoding='utf-8') as f: mn = f.read()
if 'v103_logout_in_progress' not in idx: print('FAIL \u2014 index.tsx missing v103_logout_in_progress check'); sys.exit(1)
if 'v103_logout_in_progress' not in mn: print('FAIL \u2014 menu.tsx missing v103_logout_in_progress set'); sys.exit(1)
if 'v96_auth_token' not in mn: print('FAIL \u2014 menu.tsx missing v96_auth_token SecureStore clear'); sys.exit(1)
if 'v96_auth_account' not in mn: print('FAIL \u2014 menu.tsx missing v96_auth_account SecureStore clear'); sys.exit(1)
if 'expo-secure-store' not in mn: print('FAIL \u2014 menu.tsx missing expo-secure-store import'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('auth_session_deletion_outside_logout','token_raw_logs','unexpected_token_loss','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v103 logout race fix (flag + SecureStore explicit clear, runtime verified)")
sys.exit(0)
