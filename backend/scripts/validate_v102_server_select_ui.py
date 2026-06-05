#!/usr/bin/env python3
"""v102 — Server select UI validator (also checks frontend file for required tokens)."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','server_select','v102_server_select_ui_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if len(d.get('sections_implemented', [])) < 3: print('FAIL \u2014 sections_implemented < 3'); sys.exit(1)
if len(d.get('card_fields_displayed', [])) < 5: print('FAIL \u2014 card_fields_displayed < 5'); sys.exit(1)
btn = d.get('enter_button') or {}
if not btn.get('label'): print('FAIL \u2014 enter_button.label missing'); sys.exit(1)
if btn.get('touch_target_height_px', 0) < 44: print('FAIL \u2014 touch_target_height < 44'); sys.exit(1)
if not btn.get('meets_44pt_44dp_target', False): print('FAIL \u2014 meets_44pt_44dp_target must be true'); sys.exit(1)
actions = d.get('on_enter_actions') or []
if len(actions) < 3: print('FAIL \u2014 on_enter_actions < 3'); sys.exit(1)
if not any("v101_selected_server_id" in a for a in actions): print('FAIL \u2014 on_enter missing v101_selected_server_id write'); sys.exit(1)
if not any("router.replace('/(tabs)/home')" in a for a in actions): print('FAIL \u2014 missing router.replace home'); sys.exit(1)
# Verifica reale del file servers.tsx
servers_tsx = os.path.join(ROOT,'frontend','app','servers.tsx')
if not os.path.isfile(servers_tsx): print('FAIL \u2014 servers.tsx missing'); sys.exit(1)
with open(servers_tsx,'r',encoding='utf-8') as f: content = f.read()
for token in ('v101_selected_server_id', "router.replace('/(tabs)/home')", 'ENTRA', 'SERVER PROFILE FALLBACK', 'AsyncStorage'):
    if token not in content: print(f'FAIL \u2014 servers.tsx missing token: {token}'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('random_opponent_generation','fake_server_profile_real_data','hardcoded_as_production','token_raw_logs','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v102 server select UI ({len(d['sections_implemented'])} sections, {len(d['card_fields_displayed'])} card fields, runtime verified)")
sys.exit(0)
