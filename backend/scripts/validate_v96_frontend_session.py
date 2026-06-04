#!/usr/bin/env python3
"""v96 — Validator: Frontend session implementation."""
import os, sys, json, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'auth', 'v96_frontend_session_result_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
feat = d.get('features') or {}
for k in ('session_restore', 'login_google', 'login_apple_ios_only', 'login_guest_gated_qa', 'logout'):
    if not feat.get(k):
        print(f'FAIL — frontend feature missing: {k}'); sys.exit(1)
if feat.get('plain_async_storage_for_tokens', True):
    print('FAIL — plain_async_storage_for_tokens not false'); sys.exit(1)
if feat.get('raw_oauth_token_logged', True):
    print('FAIL — raw_oauth_token_logged not false'); sys.exit(1)
# verify SecureStore use
ctx = os.path.join(ROOT, 'frontend', 'src', 'auth', 'AuthContext.tsx')
if not os.path.isfile(ctx):
    print('FAIL — AuthContext.tsx missing'); sys.exit(1)
with open(ctx, 'r', encoding='utf-8') as f:
    src = f.read()
if 'expo-secure-store' not in src:
    print('FAIL — AuthContext.tsx does not use expo-secure-store'); sys.exit(1)
if re.search(r'console\.log\(.*token', src, re.IGNORECASE):
    print('FAIL — AuthContext.tsx logs raw token'); sys.exit(1)
login = os.path.join(ROOT, 'frontend', 'app', 'login.tsx')
if not os.path.isfile(login):
    print('FAIL — login.tsx missing'); sys.exit(1)
with open(login, 'r', encoding='utf-8') as f:
    lsrc = f.read()
for needle in ('Continua con Google', 'Accedi con Apple', 'Platform.OS', 'useAuth'):
    if needle not in lsrc:
        print(f'FAIL — login.tsx missing: {needle}'); sys.exit(1)
print('PASS — v96 frontend session')
sys.exit(0)
