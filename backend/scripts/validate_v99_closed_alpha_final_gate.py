#!/usr/bin/env python3
"""v99 — Closed alpha final gate validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'closed_alpha', 'v99_closed_alpha_final_gate_v1.json')
if not os.path.isfile(p):
    print('FAIL \u2014 file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
required_gates = ('optional_fail_target_<=30', 'provider_id_token_verification', 'privacy_terms_live_urls', 'physical_mobile_qa', 'full_locust_>=1000', 'store_internal_testing_readiness', 'auth_account', 'engine', 'modes_15', 'bot_runtime', 'live_guild', 'announcements', 'known_issues_documented')
gates = d.get('gates') or {}
for g in required_gates:
    if g not in gates:
        print(f'FAIL \u2014 gate missing: {g}'); sys.exit(1)
ov = d.get('overall_verdict') or {}
if ov.get('READY_FOR_CLOSED_ALPHA_CANDIDATE', False) and ov.get('CONDITIONAL_FOR_CLOSED_ALPHA', False):
    print('FAIL \u2014 READY and CONDITIONAL both true'); sys.exit(1)
if not (ov.get('READY_FOR_CLOSED_ALPHA_CANDIDATE') or ov.get('CONDITIONAL_FOR_CLOSED_ALPHA') or ov.get('BLOCKED_FOR_CLOSED_ALPHA')):
    print('FAIL \u2014 no overall verdict set'); sys.exit(1)
if not ov.get('BLOCKED_FOR_COMMERCIAL_RELEASE', False):
    print('FAIL \u2014 commercial release must remain blocked unless explicitly cleared'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('reward_live', 'iap_active', 'production_push', 'production_broadcast', 'real_pii_in_bot_chat', 'fake_users_presented_as_real', 'day_one_high_level_bots', 'bot_event_access_bypass', 'bot_ranking_domination', 'bot_premium_reward_theft', 'random_opponents', 'bot_economy_exploit', 'raw_oauth_logs', 'provider_secrets_in_repo', 'validator_weakening', 'fake_PASS', 'hidden_optional_fail', 'commercial_release_claim'):
    if saf.get(k, True):
        print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
bl = d.get('blockers_for_closed_alpha') or []
if len(bl) < 3:
    print('FAIL \u2014 blockers_for_closed_alpha < 3'); sys.exit(1)
bc = d.get('blockers_for_commercial_release') or []
if len(bc) < 3:
    print('FAIL \u2014 blockers_for_commercial_release < 3'); sys.exit(1)
print(f"PASS \u2014 v99 closed alpha final gate ({len(bl)} closed_alpha blockers, {len(bc)} commercial blockers, CONDITIONAL)")
sys.exit(0)
