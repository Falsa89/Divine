#!/usr/bin/env python3
"""v101 — Backup manifest validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','legacy_cleanup','v101_backup_manifest_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if len(d.get('collections_to_backup', [])) < 8: print('FAIL \u2014 collections_to_backup < 8'); sys.exit(1)
if d.get('backup_includes_secrets', True): print('FAIL \u2014 backup_includes_secrets must be false'); sys.exit(1)
if d.get('backup_includes_raw_oauth_tokens', True): print('FAIL \u2014 backup_includes_raw_oauth_tokens must be false'); sys.exit(1)
if d.get('backup_includes_provider_secrets', True): print('FAIL \u2014 backup_includes_provider_secrets must be false'); sys.exit(1)
if len(d.get('rollback_plan', [])) < 3: print('FAIL \u2014 rollback_plan < 3 steps'); sys.exit(1)
backup_script = os.path.join(ROOT, d.get('backup_script',''))
if not os.path.isfile(backup_script): print(f'FAIL \u2014 backup_script missing: {backup_script}'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('raw_oauth_dumps','provider_secrets_in_backup','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v101 backup manifest ({len(d['collections_to_backup'])} collections, script ready)")
sys.exit(0)
