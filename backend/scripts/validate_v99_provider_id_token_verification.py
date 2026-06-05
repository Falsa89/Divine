#!/usr/bin/env python3
"""v99 — Provider id_token verification final validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'auth', 'v99_provider_id_token_verification_final_result_v1.json')
if not os.path.isfile(p):
    print('FAIL \u2014 file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
for section in ('google_id_token_verify', 'apple_id_token_verify'):
    s = d.get(section) or {}
    if s.get('production_ready', True):
        if not s.get('audience_check') or s.get('audience_check') == 'design_only':
            print(f'FAIL \u2014 {section} production_ready but audience_check design_only'); sys.exit(1)
    if s.get('raw_token_logging', True):
        print(f'FAIL \u2014 {section} raw_token_logging not false'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('provider_secrets_in_repo', 'raw_oauth_token_logs', 'fake_credentials', 'fake_PASS', 'validator_weakening', 'production_ready_claim'):
    if saf.get(k, True):
        print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v99 provider id_token verification (verdict={d.get('verdict')})")
sys.exit(0)
