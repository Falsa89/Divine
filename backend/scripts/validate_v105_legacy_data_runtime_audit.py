#!/usr/bin/env python3
"""v105 — Legacy data runtime audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'master_audit', 'v105_legacy_data_runtime_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
if len(d.get('legacy_artifacts') or []) < 5: print('FAIL \u2014 legacy_artifacts < 5'); sys.exit(1)
if d.get('apply_status') != 'NOT_APPLIED': print('FAIL \u2014 apply_status must be NOT_APPLIED'); sys.exit(1)
if not d.get('recommended_apply_pack'): print('FAIL \u2014 recommended_apply_pack missing'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('legacy_cleanup_applied','db_writes','destructive_migration','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v105 legacy data runtime audit ({len(d.get('legacy_artifacts'))} artifacts, apply NOT_APPLIED)")
sys.exit(0)
