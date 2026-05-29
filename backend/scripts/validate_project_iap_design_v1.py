#!/usr/bin/env python3
"""
PROJECT_IAP_DESIGN validator (static, design-only).

Asserts:
  - 6 design JSON tracks present + 1 proof marker present
  - all JSONs syntactically valid + carry expected verdict per track
  - no runtime IAP SDK integration (no StoreKit/GoogleBilling/RevenueCat refs in product code)
  - no live receipt endpoint route created
  - no DB writes triggered by this pack (validator does not open mongo client)
  - gacha rate-relevant locks still in place (premium/targeted locked, artifact/constellation hidden)
  - no battle_engine.py / backend/.env drift (MD5 invariants)
  - no purchase buttons live (SHOP/ITEM-SHOP/BP/VIP locks still asserted in frontend code)
  - validator does NOT weaken REQUIRED validators

Exits 0 on PASS, 1 on FAIL. Designed for OPTIONAL registration in suite runner.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path('/app')
IAP_DIR = ROOT / 'data/design/iap'

REQUIRED_TRACKS = {
    'iap_monetization_surface_audit_v1.json':                        'TRACK_A_IAP_MONETIZATION_SURFACE_AUDIT_READY',
    'iap_taxonomy_product_families_v1.json':                         'TRACK_B_IAP_TAXONOMY_PRODUCT_FAMILIES_READY',
    'iap_currency_wallet_contract_v1.json':                          'TRACK_C_IAP_CURRENCY_WALLET_CONTRACT_READY',
    'iap_compliance_security_receipt_architecture_v1.json':          'TRACK_D_IAP_COMPLIANCE_SECURITY_RECEIPT_ARCHITECTURE_READY',
    'iap_anti_p2w_economy_boundary_v1.json':                         'TRACK_E_IAP_ANTI_P2W_ECONOMY_BOUNDARY_READY',
    'iap_future_implementation_gate_roadmap_v1.json':                'TRACK_F_IAP_FUTURE_IMPLEMENTATION_GATE_ROADMAP_READY',
}
PROOF_MARKER = 'iap_suite_registration_proof_marker_v1.json'

EXPECTED_INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':             'ff60bbb79efa329b71aa8ed351ea89b3',
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

# Frontend lock asserts (locks must still be present)
FRONTEND_LOCK_ASSERTS = [
    ('frontend/app/shop.tsx',       'SHOP_LOCKED_V2 = true'),
    ('frontend/app/item-shop.tsx',  'ITEM_SHOP_LOCKED_V2 = true'),
    ('frontend/app/battlepass.tsx', 'BP_LOCKED_V2 = true'),
    ('frontend/app/battlepass.tsx', 'BP_PREMIUM_BUY_LOCKED_V2 = true'),
    ('frontend/app/vip.tsx',        'VIP_LOCKED_V2 = true'),
]


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def fail(msg):
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main():
    # 1) tracks A-F present + valid JSON + carry expected verdict
    for fname, expected_verdict in REQUIRED_TRACKS.items():
        p = IAP_DIR / fname
        if not p.exists():
            fail(f'missing track file: {fname}')
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            fail(f'invalid JSON {fname}: {e}')
        if d.get('verdict') != expected_verdict:
            fail(f'{fname} verdict mismatch: got {d.get("verdict")!r} expected {expected_verdict!r}')
        if d.get('task_id') != 'PROJECT_IAP_DESIGN':
            fail(f'{fname} task_id mismatch: {d.get("task_id")!r}')

    # 2) proof marker present and valid
    pm = IAP_DIR / PROOF_MARKER
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

    # 4) no runtime IAP SDK token in product code (frontend/app + backend product code, excluding tools/scripts)
    scan_roots = [ROOT / 'frontend/app', ROOT / 'backend/routes', ROOT / 'backend/server.py', ROOT / 'backend/game_data.py']
    for root_p in scan_roots:
        if root_p.is_file():
            files_iter = [root_p]
        else:
            if not root_p.exists():
                continue
            files_iter = list(root_p.rglob('*'))
        for token in FORBIDDEN_RUNTIME_TOKENS_IN_CODE:
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
                if token in content:
                    fail(f'forbidden runtime IAP token {token!r} found in {p}')

    # 5) no live receipt endpoint route file
    forbidden_routes = ['iap.py', 'iap_verify.py', 'receipt.py', 'purchase.py', 'billing.py']
    for fr in forbidden_routes:
        if (ROOT / 'backend/routes' / fr).exists():
            fail(f'forbidden live IAP/receipt route file present: backend/routes/{fr}')

    # 6) frontend locks still present
    for rel, token in FRONTEND_LOCK_ASSERTS:
        p = ROOT / rel
        if not p.exists():
            fail(f'frontend lock asserted file missing: {rel}')
        if token not in p.read_text(encoding='utf-8'):
            fail(f'frontend lock token missing in {rel}: {token!r}')

    # 7) sanity asserts on Track E anti-P2W
    e = json.loads((IAP_DIR / 'iap_anti_p2w_economy_boundary_v1.json').read_text())
    pp = e['paid_power_limits']
    for k, v in pp.items():
        if v is not False:
            fail(f'Track E paid_power_limits.{k} must be False; got {v}')
    pg = e['premium_gacha_limits']
    for k, v in pg.items():
        if v is not False:
            fail(f'Track E premium_gacha_limits.{k} must be False; got {v}')
    if e['artifact_iap_prohibition']['strict'] is not True:
        fail('Track E artifact_iap_prohibition.strict must be True')

    # 8) Track C contract: no IAP grants of forbidden categories
    c = json.loads((IAP_DIR / 'iap_currency_wallet_contract_v1.json').read_text())
    for k, v in c['iap_grants_in_this_pack'].items():
        if v is not False:
            fail(f'Track C iap_grants_in_this_pack.{k} must be False; got {v}')
    if c['db_writes_during_design'] != 0:
        fail('Track C db_writes_during_design must be 0')

    # 9) Track D: no runtime sdk + no live receipt endpoint flags
    d = json.loads((IAP_DIR / 'iap_compliance_security_receipt_architecture_v1.json').read_text())
    if d['no_runtime_sdk_integrated'] is not True:
        fail('Track D no_runtime_sdk_integrated must be True')
    if d['no_live_receipt_endpoint'] is not True:
        fail('Track D no_live_receipt_endpoint must be True')
    if d['db_writes_in_this_pack'] != 0:
        fail('Track D db_writes_in_this_pack must be 0')

    # 10) Track F roadmap structure
    f = json.loads((IAP_DIR / 'iap_future_implementation_gate_roadmap_v1.json').read_text())
    stages = f['future_stages']
    if len(stages) != 10:
        fail(f'Track F must declare exactly 10 future stages; got {len(stages)}')

    # 11) Track A: locks_verified must all be True
    a = json.loads((IAP_DIR / 'iap_monetization_surface_audit_v1.json').read_text())
    for k, v in a['locks_verified'].items():
        if v is not True:
            fail(f'Track A locks_verified.{k} must be True; got {v}')

    print('[PASS] PROJECT_IAP_DESIGN master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
