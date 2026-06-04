#!/usr/bin/env python3
"""v97 — Validator: Refresh token rotation runtime."""
import os, sys, json, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'auth', 'v97_refresh_token_rotation_result_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f: d = json.load(f)
if d.get('implementation') != 'FULL_RUNTIME_ROTATION': print('FAIL — implementation'); sys.exit(1)
feat = d.get('features') or {}
for k in ('new_access_token_issued','new_refresh_token_issued','old_refresh_revoked','replay_detection','family_revocation_on_replay','expiration_check','hash_stored_not_raw'):
    if not feat.get(k): print(f'FAIL — feature {k} missing'); sys.exit(1)
rt = d.get('runtime_verified') or {}
for k in ('login_emits_access_and_refresh_token','refresh_endpoint_rotates_and_revokes_old','replay_attempt_returns_401_and_revokes_family','logout_all_revokes_all_refresh_tokens'):
    if not rt.get(k): print(f'FAIL — runtime_verified.{k}'); sys.exit(1)
# live smoke: guest then refresh
BASE = os.environ.get('V97_BASE_URL', 'http://localhost:8001')
req = urllib.request.Request(BASE + '/api/auth/guest', data=json.dumps({'alias_hint':'rt_valid'}).encode('utf-8'), headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=5) as r:
    data = json.loads(r.read().decode('utf-8'))
rt_tok = data.get('refresh_token')
if not rt_tok: print('FAIL — guest did not issue refresh_token'); sys.exit(1)
req2 = urllib.request.Request(BASE + '/api/auth/refresh', data=json.dumps({'refresh_token':rt_tok}).encode('utf-8'), headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req2, timeout=5) as r:
    refresh_data = json.loads(r.read().decode('utf-8'))
if not refresh_data.get('rotation_applied'): print('FAIL — rotation_applied false'); sys.exit(1)
print('PASS — v97 refresh token rotation runtime')
sys.exit(0)
