#!/usr/bin/env python3
"""v98 — Closed alpha gate."""
import os, sys, json
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(ROOT,'data','design','closed_alpha','v98_closed_alpha_gate_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d=json.load(f)
gates=d.get('gates') or {}
for k in ('auth_providers','refresh_session','data_deletion_export','engine','rewards_canary','live_guild','bot_runtime','bot_chat','load','mobile_qa','optional_fail_baseline','privacy_terms','store_readiness','multi_provider_linking'):
    if k not in gates: print(f'FAIL — gate missing: {k}'); sys.exit(1)
ov=d.get('overall_verdict') or {}
if ov.get('BLOCKED_FOR_CLOSED_ALPHA',True): print('FAIL — BLOCKED_FOR_CLOSED_ALPHA'); sys.exit(1)
if not ov.get('CONDITIONAL_FOR_CLOSED_ALPHA'): print('FAIL — CONDITIONAL not set'); sys.exit(1)
safety=d.get('safety') or {}
for k in ('reward_live','iap_active','production_push','production_broadcast','real_pii_in_bot_chat','fake_users_presented_as_real','day_one_high_level_bots','bot_event_access_bypass','bot_ranking_domination','bot_premium_reward_theft','random_opponents','bot_economy_exploit','raw_oauth_logs','provider_secrets_in_repo','validator_weakening','fake_PASS'):
    if safety.get(k,True): print(f'FAIL — safety.{k} not false'); sys.exit(1)
bl=d.get('blockers_for_closed_alpha') or []
if len(bl)<3: print('FAIL — blockers_for_closed_alpha < 3'); sys.exit(1)
print(f'PASS — v98 closed alpha gate ({len(bl)} closed_alpha blockers, CONDITIONAL)')
sys.exit(0)
