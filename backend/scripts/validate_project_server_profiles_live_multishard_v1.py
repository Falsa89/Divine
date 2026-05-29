#!/usr/bin/env python3
"""
PROJECT_SERVER_PROFILES_LIVE_MULTISHARD validator (statico, gate audit only).

Asserisce:
  - 7 JSON design tracks (A..G) + 1 proof marker presenti e validi
  - tutti i JSON con task_id == PROJECT_SERVER_PROFILES_LIVE_MULTISHARD + verdict atteso
  - MD5 invarianti baseline su 5 file protetti
  - frontend locks attivi (VIP/BP/Shop/ItemShop)
  - backend/routes/server_profiles.py: feature flag gating intatto
  - server_profiles routes restano dietro flag (SERVER_PROFILES_RUNTIME_ENABLED)
  - server_scope util presente con second_server_opening_enabled / resolve_server_id
  - runtime env: SERVER_PROFILES_RUNTIME_ENABLED != "true"
                 SERVER_PROFILES_CANARY_ALLOWLIST_ENABLED != "true"
                 SECOND_SERVER_OPENING_ENABLED != "true"
                 SERVER_PROFILES_SECOND_SERVER_PUBLIC_OPEN != "true"
  - auth invariants pack 188 preservati (bcrypt + JWT + password filter)
  - validator NON indebolisce alcun REQUIRED validator
  - nessun nuovo endpoint live di server-profiles list/archive/registry implementato
    in questo pack

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL nel suite runner.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path('/app')
DIR = ROOT / 'data/design/server_profiles_live_multishard'

REQUIRED_TRACKS = {
    'server_profile_surface_audit_v1.json':              'TRACK_A_SERVER_PROFILE_SURFACE_AUDIT_READY',
    'account_wide_vs_server_boundary_matrix_v1.json':    'TRACK_B_ACCOUNT_WIDE_VS_SERVER_BOUNDARY_MATRIX_READY',
    'multishard_schema_and_endpoint_contract_v1.json':   'TRACK_C_MULTISHARD_SCHEMA_AND_ENDPOINT_CONTRACT_READY',
    'gated_runner_and_canary_plan_v1.json':              'TRACK_D_GATED_RUNNER_AND_CANARY_PLAN_READY',
    'route_protection_and_auth_ownership_gate_v1.json':  'TRACK_E_ROUTE_PROTECTION_AND_AUTH_OWNERSHIP_GATE_READY',
    'validator_and_suite_registration_v1.json':          'TRACK_F_VALIDATOR_AND_SUITE_REGISTRATION_READY',
    'completion_and_public_sync_v1.json':                'TRACK_G_COMPLETION_AND_PUBLIC_SYNC_READY',
}
PROOF_MARKER = 'server_profiles_live_multishard_suite_registration_proof_marker_v1.json'

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

# server_profiles.py must keep feature flag gating tokens
SP_ROUTE_REQUIRED_TOKENS = [
    'SERVER_PROFILES_RUNTIME_ENABLED',
    '_runtime_enabled',
    '503',
    '_disabled_payload',
]

# server_scope util must keep helpers
SCOPE_UTIL_REQUIRED_TOKENS = [
    'server_profiles_runtime_enabled',
    'second_server_opening_enabled',
    'resolve_server_id',
    'ensure_server_scope',
]

# Endpoints that MUST NOT be implemented yet (design-only)
FORBIDDEN_LIVE_NEW_ENDPOINTS = [
    '"/list"',  # /api/server-profiles/list
    '"/archive"',  # /api/server-profiles/archive
    '"/registry"',  # /api/server-profiles/registry
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
        if d.get('task_id') != 'PROJECT_SERVER_PROFILES_LIVE_MULTISHARD':
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
    for boolkey in ('weakens_REQUIRED_validators', 'fakes_PASS', 'runtime_applied',
                    'second_server_opened', 'second_server_public_open',
                    'server_selection_enabled_for_all', 'all_users_migrated',
                    'data_duplicated', 'wallet_gacha_heroes_inventory_guild_broad_change',
                    'auth_ownership_weakened', 'env_secret_added',
                    'gacha_bp_vip_shop_iap_change', 'artifact_change',
                    'battle_engine_change', 'combat_change',
                    'character_bible_change', 'hero_kit_change',
                    'required_validator_weakening'):
        if pm_d.get(boolkey) is not False:
            fail(f'proof marker must declare {boolkey}=false')
    if pm_d.get('db_writes', -1) != 0:
        fail('proof marker db_writes must be 0')
    if pm_d.get('gate_decision') != 'REFUSE_APPLY_RETURN_GATE_READY_NOT_APPLIED':
        fail('proof marker gate_decision must be REFUSE_APPLY_RETURN_GATE_READY_NOT_APPLIED')

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

    # 5) server_profiles.py feature-flag gating tokens present
    sp = (ROOT / 'backend/routes/server_profiles.py').read_text(encoding='utf-8')
    for tok in SP_ROUTE_REQUIRED_TOKENS:
        if tok not in sp:
            fail(f'server_profiles.py missing required token: {tok!r}')

    # 6) server_profiles.py: no new live endpoints in this pack
    for tok in FORBIDDEN_LIVE_NEW_ENDPOINTS:
        if tok in sp:
            fail(f'server_profiles.py introduces forbidden new endpoint token {tok!r} in this pack')

    # 7) server_scope util helpers
    su = (ROOT / 'backend/utils/server_scope.py').read_text(encoding='utf-8')
    for tok in SCOPE_UTIL_REQUIRED_TOKENS:
        if tok not in su:
            fail(f'server_scope.py missing required helper: {tok!r}')

    # 8) Runtime env: required markers MUST NOT be set to "true"
    for var in ('SERVER_PROFILES_RUNTIME_ENABLED',
                'SERVER_PROFILES_CANARY_ALLOWLIST_ENABLED',
                'SECOND_SERVER_OPENING_ENABLED',
                'SERVER_PROFILES_SECOND_SERVER_PUBLIC_OPEN'):
        v = os.environ.get(var, '').strip().lower()
        if v == 'true':
            fail(f'{var} must NOT be "true" during gate-audit-only pack; got {v!r}')

    # 9) Auth invariants from pack 188 preserved
    srv = (ROOT / 'backend/server.py').read_text(encoding='utf-8')
    for tok in ('bcrypt.hashpw', 'bcrypt.checkpw', 'jwt.encode', 'jwt.decode',
                'get_current_user', 'JWT_SECRET = os.getenv'):
        if tok not in srv:
            fail(f'server.py auth invariant token missing: {tok!r}')

    # 10) Track A: audit_only + db_writes 0 + runtime_changes 0
    a = json.loads((DIR / 'server_profile_surface_audit_v1.json').read_text())
    if a.get('audit_only') is not True:
        fail('Track A audit_only must be True')
    if a.get('db_writes') != 0:
        fail('Track A db_writes must be 0')
    if a.get('runtime_changes') != 0:
        fail('Track A runtime_changes must be 0')

    # 11) Track B: migration_required_in_this_pack false + broad_user_schema_rewrite false
    b = json.loads((DIR / 'account_wide_vs_server_boundary_matrix_v1.json').read_text())
    if b.get('migration_required_in_this_pack') is not False:
        fail('Track B migration_required_in_this_pack must be False')
    if b.get('broad_user_schema_rewrite_in_this_pack') is not False:
        fail('Track B broad_user_schema_rewrite_in_this_pack must be False')
    if not b.get('scope_matrix'):
        fail('Track B scope_matrix must be non-empty')

    # 12) Track C: design_only + no_migration + no_second_server
    c = json.loads((DIR / 'multishard_schema_and_endpoint_contract_v1.json').read_text())
    if c.get('design_only') is not True:
        fail('Track C design_only must be True')
    if c.get('db_migration') is not False:
        fail('Track C db_migration must be False')
    if c.get('db_writes') != 0:
        fail('Track C db_writes must be 0')
    if c.get('second_server_opening_in_this_pack') is not False:
        fail('Track C second_server_opening_in_this_pack must be False')

    # 13) Track D: gated runner REFUSE_APPLY + zero writes
    dt = json.loads((DIR / 'gated_runner_and_canary_plan_v1.json').read_text())
    gr = dt.get('gated_runner_behavior', {})
    if gr.get('current_resolved_action') != 'REFUSE_APPLY':
        fail('Track D gated_runner.current_resolved_action must be REFUSE_APPLY')
    if gr.get('db_writes_executed') != 0:
        fail('Track D gated_runner.db_writes_executed must be 0')
    if gr.get('server_profile_docs_created') != 0:
        fail('Track D gated_runner.server_profile_docs_created must be 0')
    if gr.get('users_server_mutation_executed') is not False:
        fail('Track D gated_runner.users_server_mutation_executed must be False')
    if gr.get('second_server_opened') is not False:
        fail('Track D gated_runner.second_server_opened must be False')
    if gr.get('verdict_emitted') != 'PROJECT_SERVER_PROFILES_LIVE_MULTISHARD_GATE_READY_NOT_APPLIED':
        fail('Track D gated_runner.verdict_emitted mismatch')
    ss = dt.get('second_server_opening', {})
    if ss.get('executed') is not False:
        fail('Track D second_server_opening.executed must be False')
    if ss.get('public_open') is not False:
        fail('Track D second_server_opening.public_open must be False')

    # 14) Track E: protection_matrix not empty + auth_hardening_pack_188 invariants preserved
    e = json.loads((DIR / 'route_protection_and_auth_ownership_gate_v1.json').read_text())
    if not e.get('route_protection_matrix'):
        fail('Track E route_protection_matrix must be non-empty')
    inv188 = e.get('auth_hardening_pack_188_invariants_preserved', {})
    for k in ('bcrypt_hashing', 'jwt_exp_30d', 'password_filter_universal',
              'no_log_secrets', 'locks_VIP_BP_Shop_ItemShop',
              'artifacts_constellation_locked_423'):
        if inv188.get(k) is not True:
            fail(f'Track E auth_hardening_pack_188 invariant {k} must be True')

    # 15) Completion track: db_writes 0 + runtime_applied false + verdict gate_ready_not_applied
    g = json.loads((DIR / 'completion_and_public_sync_v1.json').read_text())
    if g.get('db_writes') != 0:
        fail('Track G db_writes must be 0')
    if g.get('runtime_applied') is not False:
        fail('Track G runtime_applied must be False')
    if 'GATE_READY_NOT_APPLIED' not in g.get('local_verdict', ''):
        fail('Track G local_verdict must contain GATE_READY_NOT_APPLIED')

    print('[PASS] PROJECT_SERVER_PROFILES_LIVE_MULTISHARD master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
