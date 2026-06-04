#!/usr/bin/env python3
"""v98 — Multi-provider linking."""
import os, sys, json
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(ROOT,'data','design','auth','v98_multi_provider_linking_result_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d=json.load(f)
rules=d.get('rules') or {}
for k in ('same_user_can_link_google_apple_guest','guest_upgrade_to_real_provider','prevent_duplicate_for_same_provider_subject_hash','no_account_takeover'):
    if not rules.get(k): print(f'FAIL — rule {k}'); sys.exit(1)
if rules.get('raw_tokens_logged',True): print('FAIL — raw_tokens_logged'); sys.exit(1)
if rules.get('unlink_last_provider') not in ('forbidden_unless_alternative_set',): print('FAIL — unlink_last_provider policy'); sys.exit(1)
schema=d.get('schema_extension') or {}
if 'users.linked_providers' not in schema: print('FAIL — schema linked_providers'); sys.exit(1)
print('PASS — v98 multi-provider linking design contract')
sys.exit(0)
