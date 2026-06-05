#!/usr/bin/env python3
"""v104 — Server profile creation policy validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v104_server_profile_creation_policy_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
if d.get('policy_id') != 'v104_server_profile_creation_policy': print('FAIL \u2014 policy_id wrong'); sys.exit(1)
if d.get('trigger') != 'player_enters_server_without_profile': print('FAIL \u2014 trigger wrong'); sys.exit(1)
paths = d.get('creation_paths') or []
if len(paths) < 2: print('FAIL \u2014 creation_paths < 2'); sys.exit(1)
auto = next((c for c in paths if c.get('path') == 'auto_safe_starter'), None)
if not auto: print('FAIL \u2014 auto_safe_starter path missing'); sys.exit(1)
if not auto.get('requires_feature_flag', False): print('FAIL \u2014 auto_safe_starter must require feature flag'); sys.exit(1)
if auto.get('feature_flag_default', True): print('FAIL \u2014 feature_flag_default must be false'); sys.exit(1)
st = d.get('starter_profile_template') or {}
if st.get('account_level') != 1: print('FAIL \u2014 starter account_level must be 1'); sys.exit(1)
if st.get('premium_currency_grant', True): print('FAIL \u2014 starter premium_currency_grant must be false'); sys.exit(1)
if st.get('random_heroes', True): print('FAIL \u2014 starter random_heroes must be false'); sys.exit(1)
if st.get('legacy_heroes_allowed', True): print('FAIL \u2014 starter legacy_heroes_allowed must be false'); sys.exit(1)
if d.get('isolation_status') != 'DECLARED_PENDING': print('FAIL \u2014 isolation_status must be DECLARED_PENDING'); sys.exit(1)
forb = set(d.get('forbidden') or [])
required_forbidden = {'random_starter_heroes', 'premium_currency_grant', 'destructive_db_writes', 'silent_blind_migration'}
missing = required_forbidden - forb
if missing: print(f'FAIL \u2014 forbidden list missing entries: {missing}'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('db_destructive_writes', 'blind_migration', 'random_starter_heroes', 'premium_currency_grant', 'reward_grant', 'fake_PASS', 'validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print('PASS \u2014 v104 server profile creation policy (gated, no premium/random/legacy)')
sys.exit(0)
