#!/usr/bin/env python3
"""v96 — Validator: Optional fail reconciliation."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'release_candidate', 'v96_optional_fail_baseline_reconciliation_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
class_ = d.get('classification') or {}
required_keys = ('environmental', 'stale_proof_missing', 'deprecated_legacy', 'real_blocker', 'should_remove_from_suite', 'should_fix_pre_rc', 'acceptable_for_closed_alpha')
for k in required_keys:
    if k not in class_:
        print(f'FAIL — classification missing: {k}'); sys.exit(1)
if class_.get('real_blocker', {}).get('count_estimate', 1) != 0:
    print('FAIL — real_blocker.count_estimate must be 0'); sys.exit(1)
if d.get('baseline_v95_state', {}).get('required_fail', 1) != 0:
    print('FAIL — baseline required_fail != 0'); sys.exit(1)
if d.get('verdict') != 'OPTIONAL_FAIL_BASELINE_RECONCILED_NO_REAL_BLOCKER':
    print('FAIL — verdict mismatch'); sys.exit(1)
print('PASS — v96 optional fail reconciliation')
sys.exit(0)
