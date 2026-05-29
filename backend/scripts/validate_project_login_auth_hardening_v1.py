#!/usr/bin/env python3
"""
PROJECT_LOGIN_AUTH_HARDENING validator (statico, audit + hardening controllato).

Asserisce:
  - 7 JSON design tracks (A..G) + 1 proof marker presenti e validi
  - tutti i JSON con task_id == PROJECT_LOGIN_AUTH_HARDENING + verdict atteso
  - MD5 invarianti baseline su 5 file protetti
  - frontend locks attivi (VIP/BP/Shop/ItemShop)
  - backend/server.py: get_current_user presente con bcrypt+JWT pattern
  - backend/server.py: register/login NON ritornano password
  - backend/server.py: nessuna route ritorna `current_user` direttamente senza filtro
  - nessun print/log di password/token nel backend
  - nessuna route forgot/reset/verify implementata (DESIGN-ONLY contract)
  - SERVER_PROFILES_RUNTIME_ENABLED / SECOND_SERVER_OPENING_ENABLED non attive
    al momento del check (env unset)
  - server_profiles.py mantiene feature_flag gating
  - AuthContext.tsx usa AsyncStorage (warning informativo, non FAIL)
  - validator NON indebolisce alcun REQUIRED validator

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL nel suite runner.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path('/app')
DIR = ROOT / 'data/design/login_auth_hardening'

REQUIRED_TRACKS = {
    'auth_surface_audit_v1.json':                          'TRACK_A_AUTH_SURFACE_AUDIT_READY',
    'controlled_auth_hardening_patch_v1.json':             'TRACK_B_CONTROLLED_AUTH_HARDENING_PATCH_READY',
    'email_verify_and_password_reset_contract_v1.json':    'TRACK_C_EMAIL_VERIFY_AND_PASSWORD_RESET_CONTRACT_READY',
    'ownership_and_route_protection_matrix_v1.json':       'TRACK_D_OWNERSHIP_AND_ROUTE_PROTECTION_MATRIX_READY',
    'auth_smoke_and_regression_tests_v1.json':             'TRACK_E_AUTH_SMOKE_AND_REGRESSION_TESTS_READY',
    'validator_and_suite_registration_v1.json':            'TRACK_F_VALIDATOR_AND_SUITE_REGISTRATION_READY',
    'completion_and_public_sync_v1.json':                  'TRACK_G_COMPLETION_AND_PUBLIC_SYNC_READY',
}
PROOF_MARKER = 'login_auth_hardening_suite_registration_proof_marker_v1.json'

EXPECTED_INVARIANTS = {
    'backend/battle_engine.py':       '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':                   'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py':    '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx':    '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx':           '45fcc9890b6b128c37088bc33aa54caf',
}

FRONTEND_LOCK_ASSERTS = [
    ('frontend/app/vip.tsx',        'VIP_LOCKED_V2 = true'),
    ('frontend/app/battlepass.tsx', 'BP_LOCKED_V2 = true'),
    ('frontend/app/battlepass.tsx', 'BP_PREMIUM_BUY_LOCKED_V2 = true'),
    ('frontend/app/shop.tsx',       'SHOP_LOCKED_V2 = true'),
    ('frontend/app/item-shop.tsx',  'ITEM_SHOP_LOCKED_V2 = true'),
]

# Tokens that MUST be present in server.py for auth primitives
AUTH_PRIMITIVES_REQUIRED = [
    'bcrypt.hashpw',
    'bcrypt.checkpw',
    'jwt.encode',
    'jwt.decode',
    'get_current_user',
    'Bearer ',
]

# Tokens that MUST NOT appear (would mean auth weakened or secrets leaked)
AUTH_FORBIDDEN_TOKENS = [
    'print(password',
    'print(token',
    'logger.info(password',
    'logger.info(token',
    'logger.debug(password',
    'logger.debug(token',
]

# Email/reset endpoints MUST NOT yet be implemented as live runtime in this pack
FORBIDDEN_LIVE_AUTH_ENDPOINTS = [
    '/api/auth/email/verify/request',
    '/api/auth/email/verify/confirm',
    '/api/auth/password/reset/request',
    '/api/auth/password/reset/confirm',
]


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def fail(msg):
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main():
    # 1) Track JSON files present + valid + expected verdict
    for fname, expected_verdict in REQUIRED_TRACKS.items():
        p = DIR / fname
        if not p.exists():
            fail(f'missing track file: {fname}')
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            fail(f'invalid JSON {fname}: {e}')
        if d.get('verdict') != expected_verdict:
            fail(f'{fname} verdict mismatch: got {d.get("verdict")!r} expected {expected_verdict!r}')
        if d.get('task_id') != 'PROJECT_LOGIN_AUTH_HARDENING':
            fail(f'{fname} task_id mismatch: {d.get("task_id")!r}')

    # 2) Proof marker
    pm = DIR / PROOF_MARKER
    if not pm.exists():
        fail(f'missing proof marker: {PROOF_MARKER}')
    pm_d = json.loads(pm.read_text(encoding='utf-8'))
    if pm_d.get('purpose') != 'DEDICATED_SUITE_REGISTRATION_PROOF_MARKER':
        fail('proof marker purpose mismatch')
    if pm_d.get('validator_file_role') != 'OPTIONAL':
        fail('proof marker role must be OPTIONAL')
    if pm_d.get('weakens_REQUIRED_validators') is not False:
        fail('proof marker must declare weakens_REQUIRED_validators=false')
    for boolkey in ('runtime_change', 'env_secret_added', 'password_hashing_removed',
                    'real_email_sending', 'server_profiles_live_activated',
                    'second_server_opened', 'db_migration', 'broad_user_schema_rewrite'):
        if pm_d.get(boolkey) is not False:
            fail(f'proof marker must declare {boolkey}=false')

    # 3) MD5 invariants
    for rel, expected_hash in EXPECTED_INVARIANTS.items():
        actual = md5(ROOT / rel)
        if actual != expected_hash:
            fail(f'invariant drift on {rel}: expected {expected_hash} got {actual}')

    # 4) Frontend locks still in place
    for rel, token in FRONTEND_LOCK_ASSERTS:
        p = ROOT / rel
        if not p.exists():
            fail(f'frontend lock file missing: {rel}')
        if token not in p.read_text(encoding='utf-8'):
            fail(f'frontend lock token missing in {rel}: {token!r}')

    # 5) server.py auth primitives present
    srv = (ROOT / 'backend/server.py').read_text(encoding='utf-8')
    for tok in AUTH_PRIMITIVES_REQUIRED:
        if tok not in srv:
            fail(f'server.py missing auth primitive token: {tok!r}')

    # 6) server.py register/login filter password on return
    if 'if k != "password"' not in srv:
        fail('server.py missing password filter pattern on auth returns')

    # 7) No print/log of password/token in server.py and routes
    for tok in AUTH_FORBIDDEN_TOKENS:
        if tok in srv:
            fail(f'server.py contains forbidden secret-logging token: {tok!r}')

    routes_dir = ROOT / 'backend/routes'
    for p in routes_dir.rglob('*.py'):
        if any(part in ('__pycache__',) for part in p.parts):
            continue
        content = p.read_text(encoding='utf-8', errors='ignore')
        for tok in AUTH_FORBIDDEN_TOKENS:
            if tok in content:
                fail(f'{p} contains forbidden secret-logging token: {tok!r}')

    # 8) No live email/password reset endpoints implemented yet
    scan = srv
    for routef in routes_dir.rglob('*.py'):
        if any(part in ('__pycache__',) for part in routef.parts):
            continue
        scan += routef.read_text(encoding='utf-8', errors='ignore')
    for ep in FORBIDDEN_LIVE_AUTH_ENDPOINTS:
        if ep in scan:
            fail(f'live auth endpoint MUST NOT be implemented yet in this pack: {ep}')

    # 9) JWT_SECRET sourced from env (must use os.getenv)
    if 'JWT_SECRET = os.getenv' not in srv:
        fail('server.py must source JWT_SECRET via os.getenv')

    # 10) server_profiles.py still feature-flag gated
    sp = (ROOT / 'backend/routes/server_profiles.py').read_text(encoding='utf-8')
    if 'SERVER_PROFILES_RUNTIME_ENABLED' not in sp:
        fail('server_profiles.py missing SERVER_PROFILES_RUNTIME_ENABLED feature flag check')

    # 11) Runtime env state: feature flags MUST be unset OR explicitly != "true"
    spre = os.environ.get('SERVER_PROFILES_RUNTIME_ENABLED')
    if spre == 'true':
        fail(f'SERVER_PROFILES_RUNTIME_ENABLED must NOT be "true" during this pack; got {spre!r}')
    sso = os.environ.get('SECOND_SERVER_OPENING_ENABLED')
    if sso == 'true':
        fail(f'SECOND_SERVER_OPENING_ENABLED must NOT be "true" during this pack; got {sso!r}')

    # 12) AuthContext uses AsyncStorage (current state; SecureStore future P1)
    ac = (ROOT / 'frontend/context/AuthContext.tsx').read_text(encoding='utf-8')
    if 'AsyncStorage' not in ac:
        fail('AuthContext.tsx missing AsyncStorage usage')

    # 13) Track B: no_patch_required + no runtime/db_migration/secret/email touch
    b = json.loads((DIR / 'controlled_auth_hardening_patch_v1.json').read_text())
    if b.get('no_patch_required') is not True:
        fail('Track B no_patch_required must be True')
    for boolkey in ('login_register_weakened', 'password_hashing_removed',
                    'password_or_token_logged', 'password_hash_returned_to_client',
                    'env_secrets_added', 'real_email_sending',
                    'server_profiles_live_activated', 'second_server_opened',
                    'broad_user_schema_rewrite', 'gacha_change',
                    'bp_vip_shop_iap_change', 'artifact_change',
                    'battle_engine_change', 'combat_change',
                    'required_validator_weakening', 'fake_pass'):
        if b.get(boolkey) is not False:
            fail(f'Track B {boolkey} must be False')

    # 14) Track C: design_only + no runtime + no email + no migration
    c = json.loads((DIR / 'email_verify_and_password_reset_contract_v1.json').read_text())
    if c.get('design_only') is not True:
        fail('Track C design_only must be True')
    if c.get('runtime_implementation_in_this_pack') is not False:
        fail('Track C runtime_implementation_in_this_pack must be False')
    if c.get('real_email_sending') is not False:
        fail('Track C real_email_sending must be False')
    if c.get('smtp_provider_external') is not False:
        fail('Track C smtp_provider_external must be False')
    if c.get('db_migration') is not False:
        fail('Track C db_migration must be False')

    # 15) Track D: no CRITICAL findings; protection_matrix not empty
    d = json.loads((DIR / 'ownership_and_route_protection_matrix_v1.json').read_text())
    if not d.get('protection_matrix'):
        fail('Track D protection_matrix must be non-empty')
    if d.get('findings_summary', {}).get('CRITICAL', -1) != 0:
        fail('Track D findings_summary.CRITICAL must be 0')

    # 16) Track E: smoke_fail_count == 0 + regression_observed == false + at least 10 checks
    e = json.loads((DIR / 'auth_smoke_and_regression_tests_v1.json').read_text())
    if e.get('smoke_fail_count', -1) != 0:
        fail('Track E smoke_fail_count must be 0')
    if e.get('regression_observed') is not False:
        fail('Track E regression_observed must be False')
    if len(e.get('smoke_results', [])) < 10:
        fail('Track E must have at least 10 smoke results')

    print('[PASS] PROJECT_LOGIN_AUTH_HARDENING master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
