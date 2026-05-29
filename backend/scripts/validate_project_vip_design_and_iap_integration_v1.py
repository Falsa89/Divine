#!/usr/bin/env python3
"""
PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION validator (statico, design-only).

Verifica che il pack VIP sia consistente, completamente locked, anti-P2W
e che NON introduca alcuna mutazione live (no DB writes, no IAP SDK runtime,
no real product IDs, no live receipt endpoint, no rate/pity changes, no
modifiche a battle_engine / artifacts / .env / battlepass / vip frontend).

Asserisce:
  - 7 track JSON (A-G) presenti + 1 proof marker presente
  - JSON sintatticamente validi + verdict atteso per ogni track
  - frontend/app/vip.tsx contiene ancora "VIP_LOCKED_V2 = true"
  - frontend lock invarianti BP/Shop/Item-Shop/VIP intatti
  - nessun token IAP SDK runtime nel product code
  - nessun route IAP/VIP/receipt live aggiunto in backend/routes
  - nessun ID prodotto Apple/Google reale leakato nel product code
  - MD5 invarianti baseline su battle_engine.py / .env / routes/artifacts.py /
    frontend/app/battlepass.tsx / frontend/app/vip.tsx
  - il validator NON indebolisce alcun REQUIRED validator
  - VIP_LOCKED_V2 e tutte le feature flag VIP_*_ENABLED restano false in design

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL nel suite runner.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
VIP_DIR = ROOT / 'data/design/vip'

REQUIRED_TRACKS = {
    'vip_surface_lock_audit_v1.json':              'TRACK_A_VIP_SURFACE_AND_LOCK_AUDIT_READY',
    'vip_canonical_tier_design_v1.json':           'TRACK_B_VIP_CANONICAL_TIER_DESIGN_READY',
    'vip_benefit_boundary_anti_p2w_v1.json':       'TRACK_C_VIP_BENEFIT_BOUNDARY_READY',
    'vip_iap_entitlement_wallet_mapping_v1.json':  'TRACK_D_VIP_IAP_ENTITLEMENT_AND_WALLET_MAPPING_READY',
    'vip_locked_ui_preview_policy_v1.json':        'TRACK_E_VIP_LOCKED_UI_PREVIEW_POLICY_READY',
    'vip_future_api_backend_contract_v1.json':     'TRACK_F_VIP_FUTURE_API_BACKEND_CONTRACT_READY',
    'vip_future_implementation_roadmap_v1.json':   'TRACK_G_VIP_FUTURE_IMPLEMENTATION_ROADMAP_READY',
}
PROOF_MARKER = 'vip_suite_registration_proof_marker_v1.json'

EXPECTED_INVARIANTS = {
    'backend/battle_engine.py':       '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':                   'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py':    '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx':    '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx':           '45fcc9890b6b128c37088bc33aa54caf',
}

FORBIDDEN_RUNTIME_TOKENS_IN_CODE = [
    'expo-in-app-purchases',
    'react-native-iap',
    'react-native-purchases',
    'revenuecat',
    'StoreKit2',
    'BillingClient',
]

# Real store product IDs leak pattern (mock IDs uses dw_mock_, dw_real_ is forbidden).
REAL_PRODUCT_ID_REGEX = re.compile(
    r'\b(com\.divinewaifus|dw_real_)\.[a-z0-9_.]+',
    re.IGNORECASE,
)

FRONTEND_LOCK_ASSERTS = [
    ('frontend/app/vip.tsx',        'VIP_LOCKED_V2 = true'),
    ('frontend/app/battlepass.tsx', 'BP_LOCKED_V2 = true'),
    ('frontend/app/battlepass.tsx', 'BP_PREMIUM_BUY_LOCKED_V2 = true'),
    ('frontend/app/shop.tsx',       'SHOP_LOCKED_V2 = true'),
    ('frontend/app/item-shop.tsx',  'ITEM_SHOP_LOCKED_V2 = true'),
]


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def fail(msg):
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main():
    # 1) Track JSON files A-G present + valid JSON + expected verdict
    for fname, expected_verdict in REQUIRED_TRACKS.items():
        p = VIP_DIR / fname
        if not p.exists():
            fail(f'missing track file: {fname}')
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            fail(f'invalid JSON {fname}: {e}')
        if d.get('verdict') != expected_verdict:
            fail(f'{fname} verdict mismatch: got {d.get("verdict")!r} expected {expected_verdict!r}')
        if d.get('task_id') != 'PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION':
            fail(f'{fname} task_id mismatch: {d.get("task_id")!r}')

    # 2) Proof marker presente e ruolo OPTIONAL, non indebolisce REQUIRED
    pm = VIP_DIR / PROOF_MARKER
    if not pm.exists():
        fail(f'missing proof marker: {PROOF_MARKER}')
    pm_d = json.loads(pm.read_text(encoding='utf-8'))
    if pm_d.get('purpose') != 'DEDICATED_SUITE_REGISTRATION_PROOF_MARKER':
        fail('proof marker purpose mismatch')
    if pm_d.get('validator_file_role') != 'OPTIONAL':
        fail('proof marker role must be OPTIONAL')
    if pm_d.get('weakens_REQUIRED_validators') is not False:
        fail('proof marker must declare weakens_REQUIRED_validators=false')

    # 3) MD5 invariants su file critici (devono restare identici al baseline)
    for rel, expected_hash in EXPECTED_INVARIANTS.items():
        actual = md5(ROOT / rel)
        if actual != expected_hash:
            fail(f'invariant drift on {rel}: expected {expected_hash} got {actual}')

    # 4) Nessun runtime IAP SDK token + nessun real store product ID nel product code
    scan_roots = [
        ROOT / 'frontend/app',
        ROOT / 'backend/routes',
        ROOT / 'backend/server.py',
        ROOT / 'backend/game_data.py',
    ]
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

    # 5) Nessun live IAP/VIP/BP receipt endpoint file aggiunto a backend/routes
    forbidden_routes = [
        'iap.py', 'iap_verify.py', 'receipt.py', 'purchase.py', 'billing.py',
        'shop_iap.py', 'battlepass_iap.py', 'battlepass_verify.py',
        'vip_iap.py', 'vip_verify.py', 'vip_grant.py', 'vip_revoke.py',
    ]
    for fr in forbidden_routes:
        if (ROOT / 'backend/routes' / fr).exists():
            fail(f'forbidden live IAP/VIP/BP route file present: backend/routes/{fr}')

    # 6) Frontend locks ancora presenti
    for rel, token in FRONTEND_LOCK_ASSERTS:
        p = ROOT / rel
        if not p.exists():
            fail(f'frontend lock asserted file missing: {rel}')
        if token not in p.read_text(encoding='utf-8'):
            fail(f'frontend lock token missing in {rel}: {token!r}')

    # 7) Track A: locks_verified tutti True + zero db writes + iap_sdk_imported False
    a = json.loads((VIP_DIR / 'vip_surface_lock_audit_v1.json').read_text())
    for k, v in a['locks_verified'].items():
        if v is not True:
            fail(f'Track A locks_verified.{k} must be True; got {v}')
    if a['db_writes_during_audit'] != 0:
        fail('Track A db_writes_during_audit must be 0')
    if a['runtime_changes_during_audit'] is not False:
        fail('Track A runtime_changes_during_audit must be False')
    fe = a['vip_frontend']
    if fe['iap_sdk_imported'] is not False:
        fail('Track A vip_frontend.iap_sdk_imported must be False')
    if fe['storekit_imported'] is not False:
        fail('Track A vip_frontend.storekit_imported must be False')
    if fe['play_billing_imported'] is not False:
        fail('Track A vip_frontend.play_billing_imported must be False')
    if fe['revenuecat_imported'] is not False:
        fail('Track A vip_frontend.revenuecat_imported must be False')
    if fe['classification'] != 'locked':
        fail('Track A vip_frontend.classification must be "locked"')
    if fe['buy_button_visible'] is not False:
        fail('Track A vip_frontend.buy_button_visible must be False')
    if a['vip_backend']['endpoints_reachable_from_frontend'] is not False:
        fail('Track A vip_backend.endpoints_reachable_from_frontend must be False (gated by VIP_LOCKED_V2)')

    # 8) Track B: design-only + no live amounts + 11 tier (0..10) + tier 1..10 locked
    b = json.loads((VIP_DIR / 'vip_canonical_tier_design_v1.json').read_text())
    if b['design_only'] is not True:
        fail('Track B design_only must be True')
    if b['db_writes'] != 0:
        fail('Track B db_writes must be 0')
    if b['no_live_amounts_in_this_pack'] is not True:
        fail('Track B no_live_amounts_in_this_pack must be True')
    if b['no_combat_power_unlock_via_tier'] is not True:
        fail('Track B no_combat_power_unlock_via_tier must be True')
    if b['no_artifact_constellation_via_tier'] is not True:
        fail('Track B no_artifact_constellation_via_tier must be True')
    if b['no_premium_targeted_sigilli_via_tier'] is not True:
        fail('Track B no_premium_targeted_sigilli_via_tier must be True')
    if b['no_pity_skip_via_tier'] is not True:
        fail('Track B no_pity_skip_via_tier must be True')
    if len(b['vip_tiers']) != 11:
        fail(f'Track B must declare exactly 11 vip_tiers (0..10); got {len(b["vip_tiers"])}')
    for t in b['vip_tiers']:
        if t['tier'] == 0:
            if t.get('locked') is not False:
                fail('Track B tier 0 (Visitatore) must be locked=false (baseline state)')
        else:
            if t.get('locked') is not True:
                fail(f"Track B tier {t['tier']} must be locked=true")
            if t.get('live') is not False:
                fail(f"Track B tier {t['tier']} must be live=false")

    # 9) Track C: forbidden_benefits non vuoto + boundary summary anti-P2W + not runtime
    c = json.loads((VIP_DIR / 'vip_benefit_boundary_anti_p2w_v1.json').read_text())
    if not c['forbidden_benefits']:
        fail('Track C forbidden_benefits must list at least one entry')
    if c['applies_to_vip_endpoints_runtime'] is not False:
        fail('Track C applies_to_vip_endpoints_runtime must be False')
    if c['endpoints_remain_gated_by_VIP_LOCKED_V2'] is not True:
        fail('Track C endpoints_remain_gated_by_VIP_LOCKED_V2 must be True')
    bs = c['benefit_boundary_summary']
    if bs['vip_forbids_combat_power_grant'] is not True:
        fail('Track C vip_forbids_combat_power_grant must be True')
    if bs['vip_forbids_artifact_grant'] is not True:
        fail('Track C vip_forbids_artifact_grant must be True')
    if bs['vip_forbids_pity_change'] is not True:
        fail('Track C vip_forbids_pity_change must be True')
    if bs['vip_forbids_targeted_unlock'] is not True:
        fail('Track C vip_forbids_targeted_unlock must be True')
    if bs['vip_forbids_bp_premium_auto_unlock'] is not True:
        fail('Track C vip_forbids_bp_premium_auto_unlock must be True')
    if bs['vip_can_bypass_progression'] is not False:
        fail('Track C vip_can_bypass_progression must be False')
    if bs['vip_can_break_balance'] is not False:
        fail('Track C vip_can_break_balance must be False')

    # 10) Track D: server-authoritative + no DB writes + idempotency + refund handling
    d = json.loads((VIP_DIR / 'vip_iap_entitlement_wallet_mapping_v1.json').read_text())
    if d['design_only'] is not True:
        fail('Track D design_only must be True')
    if d['db_writes_in_this_pack'] != 0:
        fail('Track D db_writes_in_this_pack must be 0')
    if d['applies_to_runtime'] is not False:
        fail('Track D applies_to_runtime must be False')
    sa = d['server_authority']
    if sa['client_never_grants_vip_points'] is not True:
        fail('Track D client_never_grants_vip_points must be True')
    if sa['client_never_recomputes_tier'] is not True:
        fail('Track D client_never_recomputes_tier must be True')
    if sa['server_validates_all_iap_receipts_before_grant'] is not True:
        fail('Track D server_validates_all_iap_receipts_before_grant must be True')
    if sa['server_writes_all_vip_ledger_entries'] is not True:
        fail('Track D server_writes_all_vip_ledger_entries must be True')
    ws = d['wallet_separation_policy']
    if ws['vip_points_are_not_a_spendable_currency'] is not True:
        fail('Track D vip_points_are_not_a_spendable_currency must be True')
    if ws['vip_points_are_progression_marker_only'] is not True:
        fail('Track D vip_points_are_progression_marker_only must be True')

    # 11) Track E: frontend vip NON modificato in questo pack + lock invariants
    e = json.loads((VIP_DIR / 'vip_locked_ui_preview_policy_v1.json').read_text())
    if e['frontend_vip_modified_in_this_pack'] is not False:
        fail('Track E frontend_vip_modified_in_this_pack must be False')
    inv = e['locked_state_invariants_required_after_any_future_change']
    if inv['VIP_LOCKED_V2_must_remain_true'] is not True:
        fail('Track E VIP_LOCKED_V2_must_remain_true must be True')
    if inv['claim_button_disabled'] is not True:
        fail('Track E claim_button_disabled must be True')
    if inv['no_buy_tier_button_visible'] is not True:
        fail('Track E no_buy_tier_button_visible must be True')
    if inv['no_live_api_call_on_press'] is not True:
        fail('Track E no_live_api_call_on_press must be True')

    # 12) Track F: no runtime impl + feature flags forced off
    f = json.loads((VIP_DIR / 'vip_future_api_backend_contract_v1.json').read_text())
    if f['no_runtime_implementation_added_in_this_pack'] is not True:
        fail('Track F no_runtime_implementation_added_in_this_pack must be True')
    if f['no_db_writes_in_this_pack'] is not True:
        fail('Track F no_db_writes_in_this_pack must be True')
    if f['vip_endpoints_remain_gated'] is not True:
        fail('Track F vip_endpoints_remain_gated must be True')
    ff = f['feature_flag_design']
    for flag_name in ['VIP_PROGRESSION_ENABLED', 'VIP_DAILY_CLAIM_ENABLED',
                      'VIP_BENEFITS_RUNTIME_ENABLED', 'VIP_GRANT_ENABLED']:
        if ff.get(flag_name) is not False:
            fail(f'Track F feature_flag_design.{flag_name} must be False (design-only)')
    if ff.get('VIP_GLOBAL_DISABLED') is not True:
        fail('Track F feature_flag_design.VIP_GLOBAL_DISABLED must be True')
    if ff.get('VIP_CANARY_ONLY') is not True:
        fail('Track F feature_flag_design.VIP_CANARY_ONLY must be True')
    # design must include grant + revoke + claim-daily endpoints
    expected_paths = {'/api/vip/status', '/api/vip/claim-daily', '/api/vip/grant', '/api/vip/revoke', '/api/vip/history'}
    actual_paths = {ep['path'] for ep in f['future_endpoints']}
    missing = expected_paths - actual_paths
    if missing:
        fail(f'Track F missing future endpoints: {sorted(missing)}')

    # 13) Track G: 9 stages with monotonic stage_index 1..9
    g = json.loads((VIP_DIR / 'vip_future_implementation_roadmap_v1.json').read_text())
    if len(g['stages']) != 9:
        fail(f'Track G must declare exactly 9 stages; got {len(g["stages"])}')
    for idx, stage in enumerate(g['stages'], start=1):
        if stage['stage_index'] != idx:
            fail(f'Track G stage at position {idx} has stage_index {stage["stage_index"]} (expected {idx})')
    align = g['alignment_with_other_roadmaps']
    if align['vip_release_gate_stage_9_blocks_on_178F_release_gate_stage_10'] is not True:
        fail('Track G vip_release_gate_stage_9_blocks_on_178F_release_gate_stage_10 must be True')

    print('[PASS] PROJECT_VIP_DESIGN_AND_IAP_INTEGRATION master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
