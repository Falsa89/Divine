#!/usr/bin/env python3
"""v100 — Closed alpha candidate gate validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'closed_alpha', 'v100_closed_alpha_candidate_gate_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
gates = d.get('gates') or {}
required_gates = ('optional_fail_<=30','no_required_fail','no_miss','v95_v96_v97_v98_v99_invariants_intact','v100_md5_rebaseline_formal_audit_present','external_blockers_documented','provider_credentials','privacy_terms_urls','physical_mobile_qa','full_load_>=1000','store_internal_testing_readiness')
for g in required_gates:
    if g not in gates: print(f'FAIL \u2014 gate missing: {g}'); sys.exit(1)
for g in ('optional_fail_<=30','no_required_fail','no_miss'):
    if not gates[g].get('reached', False): print(f'FAIL \u2014 gate {g} not reached'); sys.exit(1)
ov = d.get('overall_verdict') or {}
if not ov.get('BLOCKED_FOR_COMMERCIAL_RELEASE', False): print('FAIL \u2014 commercial must remain blocked'); sys.exit(1)
iss = d.get('internal_suite_state') or {}
if iss.get('REQUIRED_FAIL', 1) != 0: print('FAIL \u2014 REQUIRED_FAIL != 0'); sys.exit(1)
if iss.get('MISS', 1) != 0: print('FAIL \u2014 MISS != 0'); sys.exit(1)
if iss.get('OPTIONAL_FAIL', 999) > 30: print('FAIL \u2014 OPTIONAL_FAIL > 30'); sys.exit(1)
if not iss.get('OPTIONAL_FAIL_TARGET_REACHED', False): print('FAIL \u2014 OPTIONAL_FAIL_TARGET_REACHED must be true'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('reward_live','iap_active','production_push','production_broadcast','validator_weakening','fake_PASS','hidden_optional_fail','silent_validator_deletion','commercial_release_claim','raw_oauth_logs','provider_secrets_in_repo','bot_ranking_domination','bot_premium_reward_theft','random_opponents','bot_economy_exploit'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
if not saf.get('baseline_rebase_authorized_by_v95_RC', False): print('FAIL \u2014 baseline_rebase_authorized_by_v95_RC must be true'); sys.exit(1)
print(f"PASS \u2014 v100 closed alpha candidate gate (optional_fail={iss['OPTIONAL_FAIL']}/{iss['OPTIONAL_FAIL_TARGET']}, CONDITIONAL external blockers)")
sys.exit(0)
