#!/usr/bin/env python3
"""v102 — Logout / Change server validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','server_select','v102_logout_change_server_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
act = d.get('actions_implemented') or {}
for k in ('cambia_server','logout_account'):
    if k not in act: print(f'FAIL \u2014 actions_implemented.{k} missing'); sys.exit(1)
cs = act['cambia_server']
if cs.get('clears_account_session', True): print('FAIL \u2014 cambia_server.clears_account_session must be false'); sys.exit(1)
if "router.replace('/servers')" not in str(cs.get('on_press','')): print('FAIL \u2014 cambia_server route must be /servers'); sys.exit(1)
la = act['logout_account']
seq = la.get('on_press_sequence') or []
if len(seq) < 5: print('FAIL \u2014 logout_account.on_press_sequence < 5'); sys.exit(1)
if not la.get('clears_account_session', False): print('FAIL \u2014 logout_account.clears_account_session must be true'); sys.exit(1)
if not la.get('clears_selected_server', False): print('FAIL \u2014 logout_account.clears_selected_server must be true'); sys.exit(1)
if not la.get('returns_to_login', False): print('FAIL \u2014 logout_account.returns_to_login must be true'); sys.exit(1)
# Verifica reale menu.tsx
menu_tsx = os.path.join(ROOT,'frontend','app','(tabs)','menu.tsx')
if not os.path.isfile(menu_tsx): print('FAIL \u2014 menu.tsx missing'); sys.exit(1)
with open(menu_tsx,'r',encoding='utf-8') as f: content = f.read()
for token in ('CAMBIA SERVER','LOGOUT ACCOUNT', "router.replace('/servers')", "router.replace('/')", 'v101_selected_server_id'):
    if token not in content: print(f'FAIL \u2014 menu.tsx missing token: {token}'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('auth_session_deletion_outside_logout','token_raw_logs','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v102 logout/change server (CAMBIA SERVER + LOGOUT ACCOUNT separati, menu.tsx verified)")
sys.exit(0)
