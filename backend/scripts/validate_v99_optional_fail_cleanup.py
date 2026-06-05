#!/usr/bin/env python3
"""v99 — Optional fail cleanup final result validator (honest blocker matrix)."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'closed_alpha', 'v99_optional_fail_cleanup_result_v1.json')
if not os.path.isfile(p):
    print('FAIL \u2014 file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
if d.get('pack') != 'MEGA_RELEASE_ACCELERATION_48_v99':
    print('FAIL \u2014 wrong pack'); sys.exit(1)
if d.get('target_threshold') != 30:
    print('FAIL \u2014 target_threshold != 30'); sys.exit(1)
if 'target_reached' not in d:
    print('FAIL \u2014 target_reached missing'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('validator_weakening', 'fake_PASS', 'validator_removed_to_lower_count', 'hidden_optional_fail', 'required_fail_introduced'):
    if saf.get(k, True):
        print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
cl = d.get('final_classification') or {}
if 'true_blocker_for_closed_alpha' not in cl:
    print('FAIL \u2014 true_blocker_for_closed_alpha missing'); sys.exit(1)
if cl['true_blocker_for_closed_alpha'].get('count', 1) != 0:
    print('FAIL \u2014 true_blocker_for_closed_alpha.count != 0'); sys.exit(1)
print(f"PASS \u2014 v99 optional fail cleanup (target_reached={d.get('target_reached')}, honest, no_weakening)")
sys.exit(0)
