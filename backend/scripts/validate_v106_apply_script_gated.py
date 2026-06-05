#!/usr/bin/env python3
"""v106 — Gated apply script validator (verifies script structure + result)."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
script = os.path.join(ROOT, 'backend', 'scripts', 'apply_v106_player_server_profiles_migration.py')
if not os.path.isfile(script): print('FAIL \u2014 apply script missing'); sys.exit(1)
content = open(script, 'r', encoding='utf-8').read()
required_flags = ['V106_PLAYER_SERVER_PROFILES_APPLY','V106_BACKUP_MANIFEST_CONFIRMED','V106_STAGING_DB_CONFIRMED','V106_USER_EXPLICIT_DB_WRITE_APPROVAL']
for flag in required_flags:
    if flag not in content: print(f'FAIL \u2014 apply script missing flag {flag}'); sys.exit(1)
forbidden = ['delete_users','delete_user_heroes','grant_premium_currency','apply_legacy_cleanup_v101']
for f in forbidden:
    if f not in content: print(f'FAIL \u2014 apply script missing forbidden marker {f}'); sys.exit(1)
if 'APPLY REFUSED' not in content: print('FAIL \u2014 apply script must refuse without flags'); sys.exit(1)
# Result file check
result = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v106_apply_result_v1.json')
if not os.path.isfile(result): print('FAIL \u2014 apply result missing'); sys.exit(1)
r = json.load(open(result, 'r', encoding='utf-8'))
if r.get('status') not in ('APPLY_SKIPPED_GATED','APPLY_EXECUTED_STAGING'): print(f'FAIL \u2014 invalid status {r.get("status")}'); sys.exit(1)
# In default Emergent run, status MUST be APPLY_SKIPPED_GATED
if r.get('status') != 'APPLY_SKIPPED_GATED': print(f'FAIL \u2014 default v106 must be APPLY_SKIPPED_GATED (got {r.get("status")})'); sys.exit(1)
if r.get('db_writes_performed', -1) != 0: print('FAIL \u2014 db_writes_performed must be 0 in default'); sys.exit(1)
if r.get('premium_currency_granted', True): print('FAIL \u2014 premium_currency_granted must be false'); sys.exit(1)
if r.get('reward_granted', True): print('FAIL \u2014 reward_granted must be false'); sys.exit(1)
if r.get('legacy_cleanup_applied', True): print('FAIL \u2014 legacy_cleanup_applied must be false'); sys.exit(1)
if (r.get('original_collections_deleted') or []) != []: print('FAIL \u2014 original_collections_deleted must be empty'); sys.exit(1)
saf = r.get('safety') or {}
for k in ('no_destructive_writes','no_original_data_deleted','no_reward_grant','no_premium_currency_grant','no_legacy_cleanup_apply'):
    if not saf.get(k, False): print(f'FAIL \u2014 safety.{k} must be true'); sys.exit(1)
for k in ('fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print('PASS \u2014 v106 apply script gated (APPLY_SKIPPED_GATED, 0 db writes)')
sys.exit(0)
