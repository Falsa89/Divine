#!/usr/bin/env python3
"""v96 — Validator: Account privacy / store compliance matrix."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'auth', 'v96_account_privacy_and_store_compliance_matrix_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
for section in ('privacy_policy', 'account_deletion', 'logging_policy', 'gdpr_checklist', 'ccpa_checklist', 'app_store_checklist', 'play_console_checklist', 'qa_announcements_pii_check'):
    if section not in d:
        print(f'FAIL — missing section: {section}'); sys.exit(1)
lp = d['logging_policy']
if not lp.get('no_PII_in_logs') or not lp.get('no_raw_oauth_token_in_logs') or not lp.get('alias_only'):
    print('FAIL — logging_policy unsafe'); sys.exit(1)
qa = d['qa_announcements_pii_check']
if qa.get('real_pii_in_qa_broadcasts', True) or not qa.get('alias_only', False):
    print('FAIL — qa announcements PII leak'); sys.exit(1)
print('PASS — v96 account privacy/store compliance')
sys.exit(0)
