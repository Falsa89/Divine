#!/usr/bin/env python3
"""v96 — Validator: Real formation account bridge."""
import os, sys, json
import urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'playability_completion', 'v96_real_formation_account_bridge_result_v1.json')
if not os.path.isfile(p):
    print('FAIL — file missing:', p); sys.exit(1)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
if d.get('verdict') != 'READY':
    print('FAIL — verdict not READY'); sys.exit(1)
if d.get('endpoint_present', False) is not True:
    print('FAIL — endpoint_present not true'); sys.exit(1)
if d.get('chain_implemented') != ['saved_formation', 'local_cached_formation', 'safe_fallback_formation']:
    print('FAIL — chain mismatch'); sys.exit(1)
if not d.get('v95_blocker_closed', False):
    print('FAIL — v95_blocker_closed not true'); sys.exit(1)
safety = d.get('safety') or {}
if safety.get('db_writes') != 0 or safety.get('team_mutation', True) or safety.get('reward_live', True):
    print('FAIL — safety violation'); sys.exit(1)
# Verify endpoint responds (unauthenticated should 401/403 or safe response)
BASE = os.environ.get('V96_BASE_URL', 'http://localhost:8001')
try:
    with urllib.request.urlopen(BASE + '/api/team/get-formation', timeout=5) as r:
        pass
except urllib.error.HTTPError as e:
    if e.code not in (401, 403, 422):
        print(f'FAIL — /api/team/get-formation unexpected status {e.code}'); sys.exit(1)
except Exception as e:
    print(f'FAIL — /api/team/get-formation error: {e}'); sys.exit(1)
print('PASS — v96 real formation account bridge')
sys.exit(0)
