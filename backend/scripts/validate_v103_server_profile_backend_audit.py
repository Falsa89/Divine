#!/usr/bin/env python3
"""v103 — Server profile backend audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','server_profile','v103_server_profile_backend_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if len(d.get('files_audited', {})) < 6: print('FAIL \u2014 files_audited < 6'); sys.exit(1)
if len(d.get('blockers_identified_pre_v103', [])) < 3: print('FAIL \u2014 blockers < 3'); sys.exit(1)
if len(d.get('actions_applied_in_v103', [])) < 4: print('FAIL \u2014 actions < 4'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('db_destructive_writes','legacy_data_cleanup_apply','reward_economy_inventory_mutation','fake_production_server_data','fake_different_per_server_profiles','token_raw_logs','provider_secrets','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v103 server profile backend audit ({len(d['files_audited'])} files, {len(d['actions_applied_in_v103'])} actions)")
sys.exit(0)
