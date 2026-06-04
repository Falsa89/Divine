#!/usr/bin/env python3
"""v97 — Validator: Internal Alpha hardening gate."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'internal_alpha', 'v97_internal_alpha_hardening_gate_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
gates = d.get('gates') or {}
for k in ('account_auth','engine','playability','live_guild','bots_server_actors','chat','optional_fail_cleanup','mobile_qa','load_locust','compliance_privacy'):
    if k not in gates: print(f'FAIL — gate missing: {k}'); sys.exit(1)
ov = d.get('overall_verdict') or {}
if not ov.get('READY_FOR_INTERNAL_ALPHA_HARDENED'): print('FAIL — not READY_FOR_INTERNAL_ALPHA_HARDENED'); sys.exit(1)
safety = d.get('safety') or {}
for k in ('reward_live','iap_active','production_push','production_broadcast','real_pii_in_bot_chat','fake_users_presented_as_real','day_one_high_level_bots','bot_event_access_bypass','bot_ranking_domination','bot_premium_reward_theft','random_opponents','bot_economy_exploit','raw_oauth_logs','provider_secrets_in_repo','validator_weakening','fake_PASS'):
    if safety.get(k, True): print(f'FAIL — safety.{k} not false'); sys.exit(1)
bl = d.get('blockers_for_closed_alpha') or []
if len(bl) < 5: print('FAIL — blockers_for_closed_alpha < 5'); sys.exit(1)
print(f'PASS — v97 internal alpha hardening gate (READY_FOR_INTERNAL_ALPHA_HARDENED, {len(bl)} closed_alpha blockers)')
sys.exit(0)
