#!/usr/bin/env python3
"""v105 — Auth/account/server profile audit validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'master_audit', 'v105_auth_account_server_profile_audit_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
ctx = d.get('contexts') or {}
if not ctx.get('legacy_auth', {}).get('active', False): print('FAIL \u2014 legacy_auth.active must be true'); sys.exit(1)
if not ctx.get('v96_auth', {}).get('active', False): print('FAIL \u2014 v96_auth.active must be true'); sys.exit(1)
if not ctx.get('bridged', False): print('FAIL \u2014 contexts.bridged must be true'); sys.exit(1)
if not ctx.get('unification_pending', False): print('FAIL \u2014 unification_pending must be true'); sys.exit(1)
if len(d.get('login_paths') or []) < 4: print('FAIL \u2014 login_paths < 4'); sys.exit(1)
logout = d.get('logout') or {}
if not logout.get('v103_race_fix', False): print('FAIL \u2014 logout.v103_race_fix must be true'); sys.exit(1)
if d.get('verdict') != 'AUTH_BRIDGED_DUAL_CONTEXT_FUNCTIONAL_UNIFICATION_PENDING': print('FAIL \u2014 verdict wrong'); sys.exit(1)
saf = d.get('forbidden_scope_compliance') or {}
for k in ('auth_rewrite_done_in_audit','db_writes','raw_token_logs','provider_secrets_in_repo','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 forbidden_scope.{k} must be false'); sys.exit(1)
print('PASS \u2014 v105 auth/account/server profile audit (bridged dual context documented)')
sys.exit(0)
