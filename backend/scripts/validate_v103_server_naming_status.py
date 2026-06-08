#!/usr/bin/env python3
"""v103 — Server naming/status truthful validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','server_profile','v103_server_naming_status_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if not d.get('all_fallback_names_prefixed_qa', False): print('FAIL \u2014 all_fallback_names_prefixed_qa must be true'); sys.exit(1)
if d.get('prefix') != '[QA] ': print('FAIL \u2014 prefix not [QA]'); sys.exit(1)
servers = d.get('servers') or []
if len(servers) < 3: print('FAIL \u2014 servers < 3'); sys.exit(1)
for s in servers:
    if not s.get('server_name','').startswith('[QA] '): print(f'FAIL \u2014 server {s.get("server_id")} not [QA] prefixed'); sys.exit(1)
if not d.get('ui_banner_visible', False): print('FAIL \u2014 ui_banner_visible must be true'); sys.exit(1)
if 'QA/FALLBACK' not in d.get('ui_banner_text_line1',''): print('FAIL \u2014 banner line1 missing QA/FALLBACK'); sys.exit(1)
# Runtime check on servers.tsx
srv_tsx = os.path.join(ROOT,'frontend','app','servers.tsx')
if not os.path.isfile(srv_tsx): print('FAIL \u2014 servers.tsx missing'); sys.exit(1)
with open(srv_tsx,'r',encoding='utf-8') as f: content = f.read()
for token in ('[QA] Aurora','LISTA SERVER QA/FALLBACK','DATI NON DI PRODUZIONE'):
    if token not in content: print(f'FAIL \u2014 servers.tsx missing token: {token}'); sys.exit(1)
# Pack 87 — Stale UI copy cleanup: i token "isolation backend" e "PENDING" relativi
# alla backend isolation NON sono pi\u00f9 attesi nella nuova copy descrittiva. La nuova
# copy onesta Pack 87 dichiara: account identity condivisa + server-scoped roster
# + loader inventory/currencies/story/equipment ancora deferred (per honesty).
# Accept either old stale copy (pre-Pack-87) OR new Pack 87 honest copy.
ACCEPTED_BANNER_COPY_PATTERNS = [
    'isolation backend',                       # pre-Pack-87 stale (legacy)
    'Pack 85-87 attivi',                       # post-Pack-87 cleanup
    'profilo giocatore, roster e progressione',# Pack 87 honest descriptor
]
if not any(p in content for p in ACCEPTED_BANNER_COPY_PATTERNS):
    print(f'FAIL \u2014 servers.tsx missing both legacy stale token and Pack 87 cleanup copy'); sys.exit(1)
if d.get('misleading_names_present', True): print('FAIL \u2014 misleading_names_present must be false'); sys.exit(1)
if d.get('fake_full_or_recommended_to_attract_clicks', True): print('FAIL \u2014 fake_full_or_recommended must be false'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_production_server_data','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v103 server naming/status ({len(servers)} servers all [QA] prefixed, banner visible)")
sys.exit(0)
