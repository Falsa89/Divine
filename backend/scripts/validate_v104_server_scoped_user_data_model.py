#!/usr/bin/env python3
"""v104 — Server-scoped user data model validator (declared pending)."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v104_server_scoped_user_data_model_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
pm = d.get('preferred_model') or {}
if pm.get('collection') != 'player_server_profiles': print('FAIL \u2014 collection name wrong'); sys.exit(1)
if pm.get('primary_key') != ['account_id', 'server_id']: print('FAIL \u2014 primary_key must be (account_id, server_id)'); sys.exit(1)
for field in ('account_id', 'server_id', 'roster', 'inventory', 'currencies', 'team_formation', 'story_progress', 'arena_profile'):
    if field not in (pm.get('fields') or {}): print(f'FAIL \u2014 field {field} missing in preferred_model'); sys.exit(1)
if len(pm.get('indexes_required') or []) < 2: print('FAIL \u2014 indexes_required < 2'); sys.exit(1)
if d.get('status') != 'DECLARED_PENDING': print('FAIL \u2014 status must be DECLARED_PENDING'); sys.exit(1)
rc = d.get('runtime_contract_until_isolation_ready') or {}
if rc.get('banner_token') != 'SERVER_DATA_ISOLATION_BACKEND_PENDING': print('FAIL \u2014 banner_token missing'); sys.exit(1)
if not rc.get('no_fake_per_server_data', False): print('FAIL \u2014 no_fake_per_server_data must be true'); sys.exit(1)
if len(d.get('migration_plan_safe') or []) < 4: print('FAIL \u2014 migration_plan_safe must have >=4 steps'); sys.exit(1)
if len(d.get('per_server_data_implementations_required_v104_plus') or []) < 6: print('FAIL \u2014 per_server_data_implementations < 6'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('db_destructive_writes', 'blind_migration', 'premium_currency_grant', 'random_starter_heroes', 'fake_per_server_profile_data', 'fake_PASS', 'validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print('PASS \u2014 v104 server-scoped user data model (DECLARED_PENDING, migration plan safe)')
sys.exit(0)
