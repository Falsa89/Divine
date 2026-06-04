#!/usr/bin/env python3
"""v97 — Validator: Account deletion/GDPR hardening."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'auth', 'v97_account_deletion_gdpr_hardening_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
eps = d.get('endpoints_implemented') or []
endpoints_paths = [e.get('endpoint') for e in eps]
for required in ('POST /api/auth/delete-account-request', 'POST /api/auth/logout-all', 'GET /api/auth/privacy-status'):
    if required not in endpoints_paths: print(f'FAIL — missing endpoint {required}'); sys.exit(1)
if d.get('soft_delete_runtime') != 'INTERNAL_ALPHA_READY': print('FAIL — soft_delete_runtime'); sys.exit(1)
pm = d.get('pii_minimization') or {}
for k in ('raw_provider_user_id_stored','raw_oauth_token_logged','real_name_collected','phone_collected','physical_address_collected'):
    if pm.get(k, True): print(f'FAIL — pii_minimization.{k} not false'); sys.exit(1)
safety = d.get('safety') or {}
for k in ('reward_live','raw_oauth_token_logged','provider_secret_in_repo','real_pii_in_logs'):
    if safety.get(k, True): print(f'FAIL — safety.{k} not false'); sys.exit(1)
print('PASS — v97 account deletion/GDPR hardening')
sys.exit(0)
