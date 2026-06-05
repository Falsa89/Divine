#!/usr/bin/env python3
"""v100 — MD5 forensic audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'closed_alpha', 'v100_md5_forensic_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if d.get('count_total_stale_md5_battle_engine', 0) < 100: print('FAIL \u2014 expected >=100 stale_md5'); sys.exit(1)
if not d.get('entries'): print('FAIL \u2014 no entries'); sys.exit(1)
required_action_terms = ('supersede_validator',)
for e in d['entries']:
    if e.get('validator_action') not in ('update_baseline','supersede_validator','keep_fail','convert_to_historical_reference'):
        print(f'FAIL \u2014 invalid action for {e.get("task")}'); sys.exit(1)
    if not e.get('justification'):
        print(f'FAIL \u2014 missing justification for {e.get("task")}'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion','hidden_optional_fail','mass_baseline_overwrite'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v100 md5 forensic audit ({d['count_total_stale_md5_battle_engine']} stale_md5 + {d.get('count_non_md5_remaining',0)} non-md5)")
sys.exit(0)
