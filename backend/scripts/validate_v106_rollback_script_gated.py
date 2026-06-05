#!/usr/bin/env python3
"""v106 — Gated rollback script validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
script = os.path.join(ROOT, 'backend', 'scripts', 'rollback_v106_player_server_profiles_migration.py')
if not os.path.isfile(script): print('FAIL \u2014 rollback script missing'); sys.exit(1)
c = open(script, 'r', encoding='utf-8').read()
for flag in ('V106_PLAYER_SERVER_PROFILES_ROLLBACK','V106_ROLLBACK_BACKUP_MANIFEST_CONFIRMED'):
    if flag not in c: print(f'FAIL \u2014 rollback script missing flag {flag}'); sys.exit(1)
if 'ROLLBACK REFUSED' not in c: print('FAIL \u2014 rollback must refuse without flags'); sys.exit(1)
for f in ('delete_unrecognized_records','truncate_users','grant_premium_currency','reward_grant'):
    if f not in c: print(f'FAIL \u2014 rollback script missing forbidden marker {f}'); sys.exit(1)
plan = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v106_rollback_plan_v1.json')
if not os.path.isfile(plan): print('FAIL \u2014 rollback plan missing'); sys.exit(1)
p = json.load(open(plan, 'r', encoding='utf-8'))
if p.get('status') != 'ROLLBACK_NOT_EXECUTED_PLAN_DOCUMENTED': print('FAIL \u2014 rollback default status wrong'); sys.exit(1)
if len(p.get('strategies') or []) < 2: print('FAIL \u2014 rollback strategies < 2'); sys.exit(1)
forb = set(p.get('forbidden_during_rollback') or [])
for k in ('truncate users','truncate user_heroes','grant premium currency','reward grant'):
    if k not in forb: print(f'FAIL \u2014 forbidden_during_rollback missing "{k}"'); sys.exit(1)
saf = p.get('safety') or {}
if not saf.get('non_destructive_default', False): print('FAIL \u2014 safety.non_destructive_default must be true'); sys.exit(1)
for k in ('fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print('PASS \u2014 v106 rollback script gated (ROLLBACK_NOT_EXECUTED, non-destructive default)')
sys.exit(0)
