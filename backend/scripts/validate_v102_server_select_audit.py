#!/usr/bin/env python3
"""v102 — Server select audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','server_select','v102_server_select_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if 'files_audited' not in d or len(d['files_audited']) < 5: print('FAIL \u2014 files_audited < 5'); sys.exit(1)
if 'classification' not in d: print('FAIL \u2014 classification missing'); sys.exit(1)
if len(d.get('blockers_identified_pre_v102', [])) < 3: print('FAIL \u2014 blockers_identified_pre_v102 < 3'); sys.exit(1)
if len(d.get('actions_applied_in_v102', [])) < 3: print('FAIL \u2014 actions_applied < 3'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('db_destructive_writes','legacy_apply_cleanup','reward_economy_inventory_mutation','token_raw_logs','provider_secrets','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v102 server select audit ({len(d['files_audited'])} files audited, {len(d['actions_applied_in_v102'])} actions)")
sys.exit(0)
