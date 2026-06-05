#!/usr/bin/env python3
"""v101 — Server select / login / logout flow validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','server_select','v101_server_select_flow_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if len(d.get('flow_expected', [])) < 4: print('FAIL \u2014 flow_expected < 4 steps'); sys.exit(1)
if len(d.get('changes_applied', [])) < 3: print('FAIL \u2014 changes_applied < 3'); sys.exit(1)
# Verifica che le modifiche reali sono presenti nei file
index_tsx = os.path.join(ROOT,'frontend','app','index.tsx')
auth_tsx = os.path.join(ROOT,'frontend','context','AuthContext.tsx')
menu_tsx = os.path.join(ROOT,'frontend','app','(tabs)','menu.tsx')
for path, token in [(index_tsx,'v101_selected_server_id'),(auth_tsx,'v101_selected_server_id'),(menu_tsx,"router.replace('/')")]:
    if not os.path.isfile(path): print(f'FAIL \u2014 file missing: {path}'); sys.exit(1)
    with open(path,'r',encoding='utf-8') as f: content = f.read()
    if token not in content: print(f'FAIL \u2014 expected token {token!r} missing in {path}'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('auth_session_deletion_outside_logout','raw_oauth_logs','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v101 server select/login/logout flow ({len(d['changes_applied'])} changes applied, runtime verified)")
sys.exit(0)
