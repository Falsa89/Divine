#!/usr/bin/env python3
"""
PROJECT_BATTLE_PASS_SURFACE_MODERNIZATION validator (static, design-only).

Asserts:
  - 6 design JSON tracks present + 1 proof marker present
  - all JSONs syntactically valid + carry expected verdict per track
  - frontend battlepass.tsx still has BP_LOCKED_V2 = true + BP_PREMIUM_BUY_LOCKED_V2 = true
  - no runtime IAP SDK token in product code
  - no live receipt endpoint route file added
  - no real Apple/Google store product IDs leaked in product code
  - MD5 invariants unchanged for battle_engine.py / .env / routes/artifacts.py
  - related locks still in place (shop/item-shop/vip/gacha banner state)
  - validator does NOT weaken REQUIRED validators

Exits 0 on PASS, 1 on FAIL. OPTIONAL registration in suite runner.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
BP_DIR = ROOT / 'data/design/battle_pass'

REQUIRED_TRACKS = {
    'bp_surface_audit_v1.json':                       'TRACK_A_BATTLE_PASS_SURFACE_AUDIT_READY',
    'bp_canonical_structure_v1.json':                 'TRACK_B_BATTLE_PASS_CANONICAL_STRUCTURE_READY',
    'bp_reward_boundary_anti_p2w_v1.json':            'TRACK_C_BATTLE_PASS_REWARD_BOUNDARY_READY',
    'bp_locked_ui_modernization_policy_v1.json':      'TRACK_D_BATTLE_PASS_LOCKED_UI_MODERNIZATION_POLICY_READY',
    'bp_future_api_backend_contract_v1.json':         'TRACK_E_BATTLE_PASS_FUTURE_API_BACKEND_CONTRACT_READY',
    'bp_future_implementation_roadmap_v1.json':       'TRACK_F_BATTLE_PASS_FUTURE_IMPLEMENTATION_ROADMAP_READY',
}
PROOF_MARKER = 'bp_suite_registration_proof_marker_v1.json'

EXPECTED_INVARIANTS = {
    'backend/battle_engine.py':    '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':                'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
}

FORBIDDEN_RUNTIME_TOKENS_IN_CODE = [
    'expo-in-app-purchases',
    'react-native-iap',
    'react-native-purchases',
    'revenuecat',
    'StoreKit2',
    'BillingClient',
]

REAL_PRODUCT_ID_REGEX = re.compile(
    r'\b(com\.divinewaifus|dw_real_)\.[a-z0-9_.]+',
    re.IGNORECASE,
)

FRONTEND_LOCK_ASSERTS = [
    ('frontend/app/battlepass.tsx', 'BP_LOCKED_V2 = true'),
    ('frontend/app/battlepass.tsx', 'BP_PREMIUM_BUY_LOCKED_V2 = true'),
    ('frontend/app/shop.tsx',       'SHOP_LOCKED_V2 = true'),
    ('frontend/app/item-shop.tsx',  'ITEM_SHOP_LOCKED_V2 = true'),
    ('frontend/app/vip.tsx',        'VIP_LOCKED_V2 = true'),
]


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def fail(msg):
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main():
    # 1) tracks A-F present + valid JSON + expected verdict
    for fname, expected_verdict in REQUIRED_TRACKS.items():
        p = BP_DIR / fname
        if not p.exists():
            fail(f'missing track file: {fname}')
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            fail(f'invalid JSON {fname}: {e}')
        if d.get('verdict') != expected_verdict:
            fail(f'{fname} verdict mismatch: got {d.get("verdict")!r} expected {expected_verdict!r}')
        if d.get('task_id') != 'PROJECT_BATTLE_PASS_SURFACE_MODERNIZATION':
            fail(f'{fname} task_id mismatch: {d.get("task_id")!r}')

    # 2) proof marker
    pm = BP_DIR / PROOF_MARKER
    if not pm.exists():
        fail(f'missing proof marker: {PROOF_MARKER}')
    pm_d = json.loads(pm.read_text(encoding='utf-8'))
    if pm_d.get('purpose') != 'DEDICATED_SUITE_REGISTRATION_PROOF_MARKER':
        fail('proof marker purpose mismatch')
    if pm_d.get('validator_file_role') != 'OPTIONAL':
        fail('proof marker role must be OPTIONAL')
    if pm_d.get('weakens_REQUIRED_validators') is not False:
        fail('proof marker must declare weakens_REQUIRED_validators=false')

    # 3) MD5 invariants unchanged
    for rel, expected_hash in EXPECTED_INVARIANTS.items():
        actual = md5(ROOT / rel)
        if actual != expected_hash:
            fail(f'invariant drift on {rel}: expected {expected_hash} got {actual}')

    # 4) no runtime IAP SDK token + no real store IDs in product code
    scan_roots = [ROOT / 'frontend/app', ROOT / 'backend/routes', ROOT / 'backend/server.py', ROOT / 'backend/game_data.py']
    for root_p in scan_roots:
        if root_p.is_file():
            files_iter = [root_p]
        else:
            if not root_p.exists():
                continue
            files_iter = list(root_p.rglob('*'))
        for p in files_iter:
            if not p.is_file():
                continue
            if any(part in ('node_modules', '__pycache__', '.git') for part in p.parts):
                continue
            if p.suffix not in ('.py', '.ts', '.tsx', '.js', '.jsx', '.json'):
                continue
            try:
                content = p.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            for token in FORBIDDEN_RUNTIME_TOKENS_IN_CODE:
                if token in content:
                    fail(f'forbidden runtime IAP token {token!r} found in {p}')
            m = REAL_PRODUCT_ID_REGEX.search(content)
            if m:
                fail(f'forbidden real product ID pattern leaked in product code: {m.group(0)!r} in {p}')

    # 5) no live IAP/BP receipt endpoint route file added
    forbidden_routes = ['iap.py', 'iap_verify.py', 'receipt.py', 'purchase.py', 'billing.py', 'shop_iap.py', 'battlepass_iap.py', 'battlepass_verify.py']
    for fr in forbidden_routes:
        if (ROOT / 'backend/routes' / fr).exists():
            fail(f'forbidden live IAP/BP route file present: backend/routes/{fr}')

    # 6) frontend locks still present
    for rel, token in FRONTEND_LOCK_ASSERTS:
        p = ROOT / rel
        if not p.exists():
            fail(f'frontend lock asserted file missing: {rel}')
        if token not in p.read_text(encoding='utf-8'):
            fail(f'frontend lock token missing in {rel}: {token!r}')

    # 7) Track A locks_verified all True + audit fields
    a = json.loads((BP_DIR / 'bp_surface_audit_v1.json').read_text())
    for k, v in a['locks_verified'].items():
        if v is not True:
            fail(f'Track A locks_verified.{k} must be True; got {v}')
    if a['db_writes_during_audit'] != 0:
        fail('Track A db_writes_during_audit must be 0')
    if a['battlepass_frontend']['iap_sdk_imported'] is not False:
        fail('Track A iap_sdk_imported must be False')
    if a['battlepass_backend']['endpoints_reachable_from_frontend'] is not False:
        fail('Track A backend endpoints_reachable_from_frontend must be False (gated by frontend lock)')

    # 8) Track B: no live + season length sanity
    b = json.loads((BP_DIR / 'bp_canonical_structure_v1.json').read_text())
    if b['no_live_reward_amounts_in_this_pack'] is not True:
        fail('Track B no_live_reward_amounts_in_this_pack must be True')
    if b['no_stamina_dependency'] is not True:
        fail('Track B no_stamina_dependency must be True')
    if b['db_writes'] != 0:
        fail('Track B db_writes must be 0')
    # All non-FREE tracks must be locked
    for t in b['tracks']:
        if t['track_id'] != 'FREE':
            if t.get('locked') is not True:
                fail(f"Track B track {t['track_id']} must be locked=true")
            if t.get('live') is not False:
                fail(f"Track B track {t['track_id']} must be live=false")

    # 9) Track C: forbidden_rewards non vuoto + applies_to_bp_endpoints_runtime False
    c = json.loads((BP_DIR / 'bp_reward_boundary_anti_p2w_v1.json').read_text())
    if not c['forbidden_rewards']:
        fail('Track C forbidden_rewards must list at least one entry')
    if c['applies_to_bp_endpoints_runtime'] is not False:
        fail('Track C applies_to_bp_endpoints_runtime must be False')
    if c['endpoints_remain_gated_by_BP_LOCKED_V2'] is not True:
        fail('Track C endpoints_remain_gated_by_BP_LOCKED_V2 must be True')

    # 10) Track D: frontend NOT modified in this pack + lock invariants required
    d = json.loads((BP_DIR / 'bp_locked_ui_modernization_policy_v1.json').read_text())
    if d['frontend_battlepass_modified_in_this_pack'] is not False:
        fail('Track D frontend_battlepass_modified_in_this_pack must be False')
    inv = d['locked_state_invariants_required_after_any_future_change']
    if inv['BP_LOCKED_V2_must_remain_true'] is not True:
        fail('Track D BP_LOCKED_V2_must_remain_true must be True')
    if inv['BP_PREMIUM_BUY_LOCKED_V2_must_remain_true'] is not True:
        fail('Track D BP_PREMIUM_BUY_LOCKED_V2_must_remain_true must be True')

    # 11) Track E: no runtime + feature flags
    e = json.loads((BP_DIR / 'bp_future_api_backend_contract_v1.json').read_text())
    if e['no_runtime_implementation_added_in_this_pack'] is not True:
        fail('Track E no_runtime_implementation_added_in_this_pack must be True')
    if e['no_db_writes_in_this_pack'] is not True:
        fail('Track E no_db_writes_in_this_pack must be True')
    if e['feature_flag_design']['BP_GLOBAL_DISABLED'] is not True:
        fail('Track E BP_GLOBAL_DISABLED must be True')
    if e['feature_flag_design']['BP_CANARY_ONLY'] is not True:
        fail('Track E BP_CANARY_ONLY must be True')

    # 12) Track F: 10 stages
    f = json.loads((BP_DIR / 'bp_future_implementation_roadmap_v1.json').read_text())
    if len(f['stages']) != 10:
        fail(f'Track F must declare exactly 10 stages; got {len(f["stages"])}')

    print('[PASS] PROJECT_BATTLE_PASS_SURFACE_MODERNIZATION master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
