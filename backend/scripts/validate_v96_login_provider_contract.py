#!/usr/bin/env python3
"""v96 — Validator: Login provider contract (Google/Apple/Guest)."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'auth', 'v96_login_provider_contract_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
for prov in ('google', 'apple'):
    e = d.get(prov) or {}
    if e.get('status') not in ('READY', 'STRUCTURE_READY_CREDENTIALS_REQUIRED_FOR_STORE_BUILD'):
        print(f'FAIL — {prov} status invalid: {e.get("status")}'); sys.exit(1)
    if not e.get('frontend_button_implemented') and not e.get('frontend_button_implemented_ios_only'):
        print(f'FAIL — {prov} frontend button missing'); sys.exit(1)
    if not e.get('backend_endpoint'):
        print(f'FAIL — {prov} backend_endpoint missing'); sys.exit(1)
if d.get('apple', {}).get('ios_only_client_side') is not True:
    print('FAIL — apple ios_only_client_side must be true'); sys.exit(1)
linking = d.get('account_linking') or {}
if not linking.get('idempotent') or linking.get('provider_user_id_raw_stored', True):
    print('FAIL — account_linking unsafe'); sys.exit(1)
safety = d.get('safety') or {}
for k in ('raw_oauth_token_logged', 'provider_secret_in_repo'):
    if safety.get(k, True):
        print(f'FAIL — safety.{k} not false'); sys.exit(1)
print('PASS — v96 login provider contract')
sys.exit(0)
