#!/usr/bin/env python3
"""v99 — Physical mobile QA execution matrix validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'closed_alpha', 'v99_physical_mobile_qa_result_v1.json')
if not os.path.isfile(p):
    print('FAIL \u2014 file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
if len(d.get('checklist_android', [])) < 10:
    print('FAIL \u2014 checklist_android < 10 items'); sys.exit(1)
if len(d.get('checklist_ios', [])) < 10:
    print('FAIL \u2014 checklist_ios < 10 items'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_mobile_qa', 'fake_PASS', 'validator_weakening'):
    if saf.get(k, True):
        print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v99 physical mobile QA (executed={d.get('executed')}, status={d.get('honest_status')})")
sys.exit(0)
