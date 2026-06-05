#!/usr/bin/env python3
"""v101 — Frontend legacy mock/route audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','legacy_cleanup','v101_frontend_legacy_mock_route_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
findings = d.get('findings') or {}
for k in ('old_mock_heroes_items_enemies','old_preview_data','old_menu_routes_legacy','old_screens_still_reachable','old_authcontext_usage','old_server_select_locked_route'):
    if k not in findings: print(f'FAIL \u2014 finding {k} missing'); sys.exit(1)
if len(d.get('actions_applied_in_v101', [])) < 3: print('FAIL \u2014 actions_applied_in_v101 < 3'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('random_opponent_in_frontend_mocks','legacy_heroes_in_frontend_mocks','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v101 frontend legacy mock/route audit ({len(d['actions_applied_in_v101'])} actions applied)")
sys.exit(0)
