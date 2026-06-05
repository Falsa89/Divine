#!/usr/bin/env python3
"""v101 — Global legacy reference audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','legacy_cleanup','v101_global_legacy_reference_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if 'classification_taxonomy' not in d: print('FAIL \u2014 taxonomy missing'); sys.exit(1)
tax = d['classification_taxonomy']
for k in ('canonical_current','legacy_noncanonical','needs_quarantine','needs_migration','needs_delete_after_backup'):
    if k not in tax: print(f'FAIL \u2014 taxonomy.{k} missing'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('blind_destructive_reset','delete_without_backup','fake_PASS','validator_weakening','commercial_release_claim'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v101 global legacy reference audit (taxonomy={len(tax)}, status={d['findings_summary']['audit_status']})")
sys.exit(0)
