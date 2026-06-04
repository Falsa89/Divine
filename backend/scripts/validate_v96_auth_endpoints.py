#!/usr/bin/env python3
"""v96 — Validator: Backend auth endpoints runtime smoke."""
import os, sys, json
import urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.environ.get('V96_BASE_URL', 'http://localhost:8001')
failures = []

# 1) router file presence
for rel in ('backend/routes/v96_auth.py', 'backend/routes/v96_team_formation.py'):
    if not os.path.isfile(os.path.join(ROOT, rel)):
        failures.append(f'missing file: {rel}')

# 2) server.py registers v96_auth + v96_team_formation
with open(os.path.join(ROOT, 'backend', 'server.py'), 'r', encoding='utf-8') as f:
    src = f.read()
if 'v96_auth' not in src or 'v96_team_formation' not in src:
    failures.append('server.py does not register v96 routers')

# 3) smoke: provider-status
try:
    with urllib.request.urlopen(BASE + '/api/auth/provider-status', timeout=5) as r:
        if r.status != 200:
            failures.append(f'provider-status status={r.status}')
        else:
            d = json.loads(r.read().decode('utf-8'))
            if not d.get('v96_auth'):
                failures.append('provider-status missing v96_auth flag')
            for k in ('google', 'apple', 'guest', 'jwt'):
                if k not in d:
                    failures.append(f'provider-status missing {k}')
            if d.get('safety', {}).get('raw_oauth_token_logged', True):
                failures.append('safety.raw_oauth_token_logged not false')
except Exception as e:
    failures.append(f'provider-status error: {e}')

# 4) smoke: guest login
import json as _j
try:
    req = urllib.request.Request(BASE + '/api/auth/guest', data=_j.dumps({'alias_hint': 'qa_validator_v96'}).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=5) as r:
        if r.status != 200:
            failures.append(f'guest login status={r.status}')
        else:
            d = _j.loads(r.read().decode('utf-8'))
            if not d.get('token') or not d.get('account'):
                failures.append('guest login missing token/account')
except Exception as e:
    failures.append(f'guest login error: {e}')

if failures:
    print('FAIL — v96 auth endpoints:')
    for x in failures: print(' -', x)
    sys.exit(1)
print('PASS — v96 auth endpoints runtime smoke')
sys.exit(0)
