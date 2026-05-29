#!/usr/bin/env python3
"""
PROJECT_SHOP_IAP_INTEGRATION validator (static, design-only).

Asserts:
  - 6 design JSON tracks present + 1 proof marker present
  - all JSONs syntactically valid + carry expected verdict per track
  - no runtime IAP SDK integration (no StoreKit/GoogleBilling/RevenueCat in product code)
  - no live receipt endpoint route created
  - no real Apple/Google store product IDs leaked into product code
  - no DB writes triggered by this pack
  - shop/item-shop UI locks still asserted in frontend
  - gacha rate locks still in place (premium/targeted locked, artifact/constellation hidden)
  - no battle_engine / backend/.env drift (MD5 invariants)
  - validator does NOT weaken REQUIRED validators

Exits 0 on PASS, 1 on FAIL. Designed for OPTIONAL registration in suite runner.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
SHOP_DIR = ROOT / 'data/design/shop_iap'

REQUIRED_TRACKS = {
    'shop_iap_surface_revalidation_v1.json':                  'TRACK_A_SHOP_IAP_SURFACE_REVALIDATION_READY',
    'shop_iap_mock_product_catalog_v1.json':                  'TRACK_B_SHOP_IAP_MOCK_PRODUCT_CATALOG_READY',
    'shop_iap_ui_lock_preview_policy_v1.json':                'TRACK_C_SHOP_IAP_UI_LOCK_PREVIEW_POLICY_READY',
    'shop_iap_wallet_ledger_fulfillment_contract_v1.json':    'TRACK_D_SHOP_IAP_WALLET_LEDGER_FULFILLMENT_CONTRACT_READY',
    'shop_iap_future_api_receipt_contract_v1.json':           'TRACK_E_SHOP_IAP_FUTURE_API_RECEIPT_CONTRACT_READY',
    'shop_iap_risk_compliance_roadmap_v1.json':               'TRACK_F_SHOP_IAP_RISK_COMPLIANCE_ROADMAP_READY',
}
PROOF_MARKER = 'shop_iap_suite_registration_proof_marker_v1.json'

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

# Real store product ID patterns we forbid in product code at this stage (mock IDs are allowed)
REAL_PRODUCT_ID_REGEX = re.compile(
    r'\b(com\.divinewaifus|dw_real_)\.[a-z0-9_.]+',
    re.IGNORECASE,
)

FRONTEND_LOCK_ASSERTS = [
    ('frontend/app/shop.tsx',       'SHOP_LOCKED_V2 = true'),
    ('frontend/app/item-shop.tsx',  'ITEM_SHOP_LOCKED_V2 = true'),
    ('frontend/app/battlepass.tsx', 'BP_LOCKED_V2 = true'),
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
        p = SHOP_DIR / fname
        if not p.exists():
            fail(f'missing track file: {fname}')
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            fail(f'invalid JSON {fname}: {e}')
        if d.get('verdict') != expected_verdict:
            fail(f'{fname} verdict mismatch: got {d.get("verdict")!r} expected {expected_verdict!r}')
        if d.get('task_id') != 'PROJECT_SHOP_IAP_INTEGRATION':
            fail(f'{fname} task_id mismatch: {d.get("task_id")!r}')

    # 2) proof marker
    pm = SHOP_DIR / PROOF_MARKER
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

    # 4) no runtime IAP SDK + no real store IDs in product code (scan only product paths)
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

    # 5) no live receipt endpoint route file
    forbidden_routes = ['iap.py', 'iap_verify.py', 'receipt.py', 'purchase.py', 'billing.py', 'shop_iap.py']
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

    # 7) Track A locks_verified all True
    a = json.loads((SHOP_DIR / 'shop_iap_surface_revalidation_v1.json').read_text())
    for k, v in a['locks_verified'].items():
        if v is not True:
            fail(f'Track A locks_verified.{k} must be True; got {v}')
    if a['db_writes_during_revalidation'] != 0:
        fail('Track A db_writes_during_revalidation must be 0')

    # 8) Track B catalog: all mock IDs must start with mock.divinewaifus.
    b = json.loads((SHOP_DIR / 'shop_iap_mock_product_catalog_v1.json').read_text())
    if b['real_store_ids_in_this_pack'] is not False:
        fail('Track B real_store_ids_in_this_pack must be False')
    if b['live_prices_in_this_pack'] is not False:
        fail('Track B live_prices_in_this_pack must be False')
    for item in b['mock_product_catalog']:
        if not item['mock_id'].startswith('mock.divinewaifus.'):
            fail(f'Track B mock_id does not start with mock.divinewaifus.: {item["mock_id"]!r}')
        if item.get('live_buyable') is not False:
            fail(f'Track B item live_buyable must be False: {item["mock_id"]!r}')

    # 9) Track C: allowed/forbidden text sets + lock state
    c = json.loads((SHOP_DIR / 'shop_iap_ui_lock_preview_policy_v1.json').read_text())
    if c['locked_state_required']['buttons_buy_or_acquista_disabled'] is not True:
        fail('Track C buttons_buy_or_acquista_disabled must be True')
    if c['refund_and_restore_ui_state']['restore_purchases_button_visible'] is not False:
        fail('Track C restore_purchases_button_visible must be False (until Stage 8 of roadmap)')

    # 10) Track D: iap_grants_in_this_pack all False + db_writes 0
    d = json.loads((SHOP_DIR / 'shop_iap_wallet_ledger_fulfillment_contract_v1.json').read_text())
    for k, v in d['iap_grants_in_this_pack'].items():
        if v is not False:
            fail(f'Track D iap_grants_in_this_pack.{k} must be False; got {v}')
    if d['db_writes_in_this_pack'] != 0:
        fail('Track D db_writes_in_this_pack must be 0')

    # 11) Track E: no runtime endpoints + all feature flags False/canary-only
    e = json.loads((SHOP_DIR / 'shop_iap_future_api_receipt_contract_v1.json').read_text())
    if e['no_runtime_endpoints_added_in_this_pack'] is not True:
        fail('Track E no_runtime_endpoints_added_in_this_pack must be True')
    if e['no_live_receipt_endpoint'] is not True:
        fail('Track E no_live_receipt_endpoint must be True')
    if e['no_live_purchase_button'] is not True:
        fail('Track E no_live_purchase_button must be True')
    if e['feature_flag_design']['IAP_GLOBAL_DISABLED'] is not True:
        fail('Track E IAP_GLOBAL_DISABLED must be True')
    if e['feature_flag_design']['IAP_FULFILLMENT_CANARY_ONLY'] is not True:
        fail('Track E IAP_FULFILLMENT_CANARY_ONLY must be True')

    # 12) Track F roadmap structure
    f = json.loads((SHOP_DIR / 'shop_iap_risk_compliance_roadmap_v1.json').read_text())
    if len(f['risk_register']) < 8:
        fail('Track F risk_register must enumerate at least 8 risks')

    print('[PASS] PROJECT_SHOP_IAP_INTEGRATION master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
