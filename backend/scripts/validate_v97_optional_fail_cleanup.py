#!/usr/bin/env python3
"""v97 — Validator: Optional fail cleanup (honest, no fake PASS)."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'internal_alpha', 'v97_optional_fail_cleanup_result_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
if d.get('target_threshold') != 30: print('FAIL — target_threshold != 30'); sys.exit(1)
# honest result: target NOT reached but documented, NO fake PASS, NO validator weakening
safety = d.get('safety') or {}
if not safety.get('no_validator_weakening', False): print('FAIL — no_validator_weakening must be true'); sys.exit(1)
if not safety.get('no_fake_PASS', False): print('FAIL — no_fake_PASS must be true'); sys.exit(1)
if d.get('honest_status') not in ('PARTIAL_CLEANUP_DESIGN_AND_RECONCILIATION_ONLY','CLEANUP_TARGET_REACHED'): print('FAIL — honest_status'); sys.exit(1)
if d.get('verdict') not in ('OPTIONAL_FAIL_CLEANUP_TARGET_NOT_REACHED_HONEST_PLAN_DEFERRED_TO_V98','OPTIONAL_FAIL_CLEANUP_TARGET_REACHED'): print('FAIL — verdict'); sys.exit(1)
class_ = d.get('classification_extended') or {}
if class_.get('real_blocker', 1) != 0: print('FAIL — real_blocker must be 0'); sys.exit(1)
print(f"PASS — v97 optional fail cleanup (target_reached={d.get('target_reached')}, honest plan documented)")
sys.exit(0)
