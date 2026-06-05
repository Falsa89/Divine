#!/usr/bin/env python3
"""v100 — Optional fail cleanup validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'closed_alpha', 'v100_optional_fail_cleanup_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if d.get('target_threshold') != 30: print('FAIL \u2014 target_threshold != 30'); sys.exit(1)
if not d.get('target_reached', False): print('FAIL \u2014 target_reached must be true for v100'); sys.exit(1)
aft = d.get('after_v100') or {}
if aft.get('optional_fail_expected', 999) > 30: print('FAIL \u2014 after_v100.optional_fail_expected > 30'); sys.exit(1)
if aft.get('required_fail', 1) != 0: print('FAIL \u2014 required_fail != 0'); sys.exit(1)
if aft.get('miss', 1) != 0: print('FAIL \u2014 miss != 0'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('validator_weakening','fake_PASS','hidden_optional_fail','silent_validator_deletion','required_fail_introduced'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
if not saf.get('baseline_rebase_authorized_by_v95_RC', False): print('FAIL \u2014 baseline_rebase_authorized_by_v95_RC must be true'); sys.exit(1)
print(f"PASS \u2014 v100 optional fail cleanup (before={d['before_v100']['optional_fail']}, after={aft['optional_fail_expected']}, target<=30=True)")
sys.exit(0)
