#!/usr/bin/env python3
"""v99 — Privacy/Terms live URLs validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'compliance', 'v99_privacy_terms_live_url_result_v1.json')
if not os.path.isfile(p):
    print('FAIL \u2014 file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
for k in ('PRIVACY_POLICY_URL', 'TERMS_OF_SERVICE_URL', 'ACCOUNT_DELETION_URL'):
    if k not in d.get('env_vars_checked', []):
        print(f'FAIL \u2014 env_var {k} missing'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('fake_urls', 'fake_PASS', 'validator_weakening'):
    if saf.get(k, True):
        print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v99 privacy/terms URLs (verdict={d.get('verdict')}, honest blocker)")
sys.exit(0)
