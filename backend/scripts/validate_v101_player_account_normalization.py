#!/usr/bin/env python3
"""v101 — Player account normalization policy validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','legacy_cleanup','v101_player_account_normalization_policy_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if len(d.get('rules', [])) < 5: print('FAIL \u2014 rules < 5'); sys.exit(1)
if 'safe_starter_roster' not in d: print('FAIL \u2014 safe_starter_roster missing'); sys.exit(1)
ssr = d['safe_starter_roster']
if ssr.get('hero_count', 0) < 3: print('FAIL \u2014 safe_starter_roster.hero_count < 3'); sys.exit(1)
if not d.get('auth_session_preserved', False): print('FAIL \u2014 auth_session_preserved must be true'); sys.exit(1)
if not d.get('auth_session_deletion_only_via_logout_flow', False): print('FAIL \u2014 auth_session_deletion_only_via_logout_flow must be true'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('auth_session_deletion_outside_logout','premium_currency_grant','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v101 player account normalization ({len(d['rules'])} rules, safe_starter_roster ready)")
sys.exit(0)
