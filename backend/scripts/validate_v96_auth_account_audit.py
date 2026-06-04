#!/usr/bin/env python3
"""v96 — Validator: Auth/Account audit."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'auth', 'v96_auth_account_audit_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
class_ = d.get('classifications') or {}
for k in ('implemented', 'missing', 'blocked_by_env_provider_credentials', 'safe_fallback'):
    if k not in class_:
        print(f'FAIL — classifications missing key: {k}'); sys.exit(1)
safety = d.get('safety') or {}
for k in ('raw_oauth_token_logged', 'provider_secret_in_repo', 'plain_token_storage', 'real_pii_in_logs'):
    if safety.get(k, True):
        print(f'FAIL — safety.{k} not false'); sys.exit(1)
if not safety.get('alias_only_in_logs', False):
    print('FAIL — alias_only_in_logs not true'); sys.exit(1)
# verify v96 backend files
for rel in ('backend/routes/v96_auth.py', 'backend/routes/v96_team_formation.py',
            'frontend/src/auth/AuthContext.tsx', 'frontend/app/login.tsx'):
    if not os.path.isfile(os.path.join(ROOT, rel)):
        print(f'FAIL — missing file: {rel}'); sys.exit(1)
print('PASS — v96 auth account audit')
sys.exit(0)
