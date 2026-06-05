#!/usr/bin/env python3
"""v106 — Backup manifest validator (default: BACKUP_NOT_EXECUTED)."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v106_backup_manifest_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
if d.get('status') not in ('BACKUP_NOT_EXECUTED_DRY_RUN_DEFAULT','BACKUP_EXECUTED_STAGING'): print(f'FAIL \u2014 invalid status {d.get("status")}'); sys.exit(1)
if not d.get('backup_script'): print('FAIL \u2014 backup_script missing'); sys.exit(1)
script = os.path.join(ROOT, d.get('backup_script'))
if not os.path.isfile(script): print(f'FAIL \u2014 backup script file missing: {script}'); sys.exit(1)
plan = d.get('planned_collections_to_backup') or []
if len(plan) < 10: print('FAIL \u2014 planned_collections_to_backup < 10'); sys.exit(1)
mask = d.get('masking_rules') or {}
for k in ('password_hash','oauth_access_token','oauth_refresh_token','any_provider_secret'):
    if k not in mask: print(f'FAIL \u2014 masking_rules.{k} missing'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('no_raw_secrets','no_password_plaintext','no_oauth_raw','no_premium_provider_data','manifest_sha256_required'):
    if not saf.get(k, False): print(f'FAIL \u2014 safety.{k} must be true'); sys.exit(1)
print(f"PASS \u2014 v106 backup manifest ({d.get('status')}, {len(plan)} planned collections)")
sys.exit(0)
