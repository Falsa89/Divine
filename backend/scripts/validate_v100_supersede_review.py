#!/usr/bin/env python3
"""v100 — Supersede review formal validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'closed_alpha', 'v100_supersede_review_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
cats = d.get('categories') or {}
if 'md5_drift_battle_engine_post_v95' not in cats: print('FAIL \u2014 md5_drift category missing'); sys.exit(1)
summary = d.get('summary') or {}
if summary.get('superseded_by_v100_md5_rebaseline', 0) < 100: print('FAIL \u2014 superseded count < 100'); sys.exit(1)
if summary.get('removed_silently', 1) != 0: print('FAIL \u2014 removed_silently != 0'); sys.exit(1)
if summary.get('validator_weakened', 1) != 0: print('FAIL \u2014 validator_weakened != 0'); sys.exit(1)
if summary.get('fake_PASS', 1) != 0: print('FAIL \u2014 fake_PASS != 0'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('silent_validator_deletion','validator_weakening','fake_PASS','hidden_optional_fail'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
if not saf.get('old_md5_preserved_as_historical_reference', False):
    print('FAIL \u2014 old_md5_preserved_as_historical_reference must be true'); sys.exit(1)
print(f"PASS \u2014 v100 supersede review (superseded={summary['superseded_by_v100_md5_rebaseline']}, deprecated_legacy={summary.get('deprecated_legacy_kept_as_doc_reference', 0)}, environmental={summary.get('environmental_only', 0)})")
sys.exit(0)
