#!/usr/bin/env python3
"""v106 — Dry-run migration result validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v106_dry_run_player_server_profiles_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
if d.get('db_writes_performed', -1) != 0: print('FAIL \u2014 db_writes_performed must be 0'); sys.exit(1)
if d.get('default_server_id') != 's1': print('FAIL \u2014 default_server_id must be s1'); sys.exit(1)
if d.get('estimated_profiles_to_create') is None: print('FAIL \u2014 estimated_profiles_to_create missing'); sys.exit(1)
coll_inspected = d.get('collections_inspected') or {}
if len(coll_inspected) < 10: print('FAIL \u2014 collections_inspected < 10'); sys.exit(1)
plan = d.get('migration_plan_summary') or {}
if not plan.get('users_remain_account_global', False): print('FAIL \u2014 plan.users_remain_account_global must be true'); sys.exit(1)
if not plan.get('hard_currencies_remain_account_global', False): print('FAIL \u2014 plan.hard_currencies_remain_account_global must be true'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('no_db_writes','no_destructive_migration','no_reward_grant','no_premium_currency_grant','no_original_collections_deleted'):
    if not saf.get(k, False): print(f'FAIL \u2014 safety.{k} must be true'); sys.exit(1)
for k in ('fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v106 dry-run result (db_inspected={d.get('db_inspected')}, estimated_profiles={d.get('estimated_profiles_to_create')})")
sys.exit(0)
