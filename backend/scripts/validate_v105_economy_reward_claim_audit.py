#!/usr/bin/env python3
"""v105 — Economy/reward claim audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'master_audit', 'v105_economy_reward_claim_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
claims = d.get('claim_endpoints') or []
if len(claims) < 8: print('FAIL \u2014 claim_endpoints < 8'); sys.exit(1)
for c in claims:
    if c.get('server_scoped', True): print(f'FAIL \u2014 claim {c.get("endpoint")} server_scoped must be false (honest)'); sys.exit(1)
sp = d.get('safety_preview_claim_endpoints') or []
if len(sp) < 6: print('FAIL \u2014 safety_preview < 6'); sys.exit(1)
for c in sp:
    if not c.get('dry_run', False): print(f'FAIL \u2014 safety_preview {c.get("endpoint")} dry_run must be true'); sys.exit(1)
pp = d.get('premium_currency_protection') or {}
if pp.get('gems_grant_outside_purchase', True): print('FAIL \u2014 premium currency protection violated'); sys.exit(1)
if pp.get('premium_currency_in_starter_template', True): print('FAIL \u2014 premium currency in starter template violated'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('reward_mutation_added','new_claim_endpoints','premium_currency_grant','iap_changes','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v105 economy/reward claim audit ({len(claims)} live claims, {len(sp)} safety-preview)")
sys.exit(0)
