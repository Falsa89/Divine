#!/usr/bin/env python3
"""
PROJECT_FULL_RUNTIME_FEATURE_REALITY_AUDIT_WITH_TEST_ASSET_REGISTRY validator
(statico, audit-only, design-only).

Verifica che il pack audit/registry sia consistente e che NON introduca alcuna
mutazione live (no DB writes, no runtime feature implementation, no IAP/BP/VIP/Shop
attivazioni, no gacha/pity changes, no battle_engine/combat changes, no artifact
public unhide, no Soul Forge changes, no final art/audio aggiunti).

Asserisce:
  - 7 JSON design/audit (A, B, C, D, E-schema, E-inventory, F) + 1 proof marker
  - tutti i JSON syntactically validi + carry expected verdict per track
  - registry schema contiene le 7 metadata keys richieste
  - registry inventory entries hanno tutte le required keys
  - frontend lock invariants intatti (VIP/BP/SHOP/ITEM_SHOP)
  - MD5 invarianti baseline su battle_engine.py / battle_core.py / .env /
    routes/artifacts.py / frontend/app/combat.tsx / soul-forge.tsx / vip.tsx /
    battlepass.tsx
  - nessun route IAP/BP/VIP live receipt verifier in backend/routes
  - artifact mutation lock HTTP 423 preservato
  - validator NON indebolisce alcun REQUIRED validator

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL nel suite runner.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path('/app')
AUDIT_DIR = ROOT / 'data/design/runtime_audit'

REQUIRED_TRACKS = {
    'project_context_revalidation_v1.json':              'TRACK_A_PROJECT_CONTEXT_REVALIDATION_READY',
    'route_backend_inventory_audit_v1.json':             'TRACK_B_ROUTE_AND_BACKEND_INVENTORY_AUDIT_READY',
    'feature_reality_matrix_v1.json':                    'TRACK_C_FEATURE_REALITY_MATRIX_READY',
    'canonical_mismatch_tech_debt_v1.json':              'TRACK_D_CANONICAL_MISMATCH_TECH_DEBT_READY',
    'test_asset_audio_registry_schema_v1.json':          'TRACK_E_TEST_ASSET_AUDIO_REGISTRY_READY',
    'test_asset_audio_registry_initial_inventory_v1.json': 'TRACK_E_TEST_ASSET_AUDIO_REGISTRY_READY',
    'mode_implementation_priority_roadmap_v1.json':      'TRACK_F_MODE_IMPLEMENTATION_PRIORITY_ROADMAP_READY',
}
PROOF_MARKER = 'runtime_audit_suite_registration_proof_marker_v1.json'

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

REGISTRY_REQUIRED_METADATA_KEYS = {
    'mode_id', 'screen_id', 'asset_key', 'asset_status',
    'audio_key', 'audio_status', 'replace_before_release',
}

ALLOWED_STATUSES = {
    'test_placeholder', 'placeholder_dev', 'missing_final_asset',
    'missing_final_audio', 'final_ready', 'not_required',
}

TAXONOMY = {
    'NOT_FOUND', 'DESIGN_ONLY', 'LOCKED_PREVIEW', 'SCAFFOLD_EXISTS',
    'PROTOTYPE_PLAYABLE', 'PARTIAL_RUNTIME', 'CANONICAL_RUNTIME_READY',
    'MOBILE_QA_VERIFIED', 'RELEASE_READY', 'DEPRECATED_OR_UNSAFE',
}


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def fail(msg):
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main():
    # 1) Track JSON files present + valid + expected verdict
    for fname, expected_verdict in REQUIRED_TRACKS.items():
        p = AUDIT_DIR / fname
        if not p.exists():
            fail(f'missing track file: {fname}')
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            fail(f'invalid JSON {fname}: {e}')
        if d.get('verdict') != expected_verdict:
            fail(f'{fname} verdict mismatch: got {d.get("verdict")!r} expected {expected_verdict!r}')
        if d.get('task_id') != 'PROJECT_FULL_RUNTIME_FEATURE_REALITY_AUDIT_WITH_TEST_ASSET_REGISTRY':
            fail(f'{fname} task_id mismatch: {d.get("task_id")!r}')

    # 2) Proof marker
    pm = AUDIT_DIR / PROOF_MARKER
    if not pm.exists():
        fail(f'missing proof marker: {PROOF_MARKER}')
    pm_d = json.loads(pm.read_text(encoding='utf-8'))
    if pm_d.get('purpose') != 'DEDICATED_SUITE_REGISTRATION_PROOF_MARKER':
        fail('proof marker purpose mismatch')
    if pm_d.get('validator_file_role') != 'OPTIONAL':
        fail('proof marker role must be OPTIONAL')
    if pm_d.get('weakens_REQUIRED_validators') is not False:
        fail('proof marker must declare weakens_REQUIRED_validators=false')

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

    # 5) Artifact mutation HTTP 423 lock preserved
    art = (ROOT / 'backend/routes/artifacts.py').read_text(encoding='utf-8')
    if 'ARTIFACT_MUTATION_LOCK_STATUS = 423' not in art:
        fail('artifact mutation lock HTTP 423 marker missing in backend/routes/artifacts.py')

    # 6) No live IAP/BP/VIP receipt verifier route file present
    forbidden_routes = [
        'iap.py', 'iap_verify.py', 'receipt.py', 'purchase.py', 'billing.py',
        'shop_iap.py', 'battlepass_iap.py', 'battlepass_verify.py',
        'vip_iap.py', 'vip_verify.py', 'vip_grant.py', 'vip_revoke.py',
    ]
    for fr in forbidden_routes:
        if (ROOT / 'backend/routes' / fr).exists():
            fail(f'forbidden live IAP/BP/VIP route file present: backend/routes/{fr}')

    # 7) Registry schema contains required metadata keys
    schema = json.loads((AUDIT_DIR / 'test_asset_audio_registry_schema_v1.json').read_text())
    schema_keys = set(schema.get('registry_schema', {}).get('entry_required_keys', []))
    missing = REGISTRY_REQUIRED_METADATA_KEYS - schema_keys
    if missing:
        fail(f'registry schema missing required metadata keys: {sorted(missing)}')
    schema_statuses = set(schema.get('registry_schema', {}).get('allowed_statuses', []))
    if not ALLOWED_STATUSES.issubset(schema_statuses):
        fail(f'registry schema allowed_statuses missing entries: {sorted(ALLOWED_STATUSES - schema_statuses)}')
    if schema.get('db_writes') != 0:
        fail('Track E schema db_writes must be 0')

    # 8) Registry inventory entries all have required keys
    inv = json.loads((AUDIT_DIR / 'test_asset_audio_registry_initial_inventory_v1.json').read_text())
    entries = inv.get('entries', [])
    if not entries:
        fail('Track E initial inventory must contain at least 1 entry')
    for i, e in enumerate(entries):
        missing_e = REGISTRY_REQUIRED_METADATA_KEYS - set(e.keys())
        if missing_e:
            fail(f'inventory entry #{i} missing required keys: {sorted(missing_e)}')
        if e['asset_status'] not in ALLOWED_STATUSES:
            fail(f'inventory entry #{i} asset_status {e["asset_status"]!r} not in allowed_statuses')
        if e['audio_status'] not in ALLOWED_STATUSES:
            fail(f'inventory entry #{i} audio_status {e["audio_status"]!r} not in allowed_statuses')
        if not isinstance(e['replace_before_release'], bool):
            fail(f'inventory entry #{i} replace_before_release must be boolean')
    if inv.get('db_writes') != 0:
        fail('Track E inventory db_writes must be 0')

    # 9) Track A: forbidden_in_pack_compliance all True
    a = json.loads((AUDIT_DIR / 'project_context_revalidation_v1.json').read_text())
    fic = a.get('forbidden_in_pack_compliance', {})
    expected_compliance = [
        'no_runtime_implementation', 'no_db_writes', 'no_player_data_mutation',
        'no_unlock_locked_systems', 'no_gacha_or_pity_changes',
        'no_iap_bp_vip_shop_live_activation', 'no_artifact_public_activation',
        'no_battle_engine_or_combat_changes', 'no_character_bible_mutation',
        'no_hero_kit_final_numbers_change', 'no_final_assets_or_audio_added',
        'no_paid_product_ids_added', 'no_env_secrets_added',
        'no_required_validator_weakening',
    ]
    for k in expected_compliance:
        if fic.get(k) is not True:
            fail(f'Track A forbidden_in_pack_compliance.{k} must be True; got {fic.get(k)}')
    if a.get('audit_only') is not True:
        fail('Track A audit_only must be True')
    if a.get('db_writes') != 0:
        fail('Track A db_writes must be 0')

    # 10) Track B: counts match expected schema and stamina_violation flag present
    b = json.loads((AUDIT_DIR / 'route_backend_inventory_audit_v1.json').read_text())
    if b.get('audit_only') is not True:
        fail('Track B audit_only must be True')
    counts = b.get('counts', {})
    if counts.get('total_backend_route_files', 0) < 30:
        fail('Track B total_backend_route_files unexpectedly low')
    if counts.get('locked_frontend_routes', 0) != 4:
        fail('Track B locked_frontend_routes must be 4 (shop/item-shop/battlepass/vip)')
    stamina_routes = [r for r in b.get('backend_routes', []) if r.get('stamina_violation')]
    if len(stamina_routes) < 5:
        fail(f'Track B should flag at least 5 stamina_violation backend routes; got {len(stamina_routes)}')

    # 11) Track C: every feature uses valid taxonomy
    c = json.loads((AUDIT_DIR / 'feature_reality_matrix_v1.json').read_text())
    if c.get('audit_only') is not True:
        fail('Track C audit_only must be True')
    features = c.get('features', [])
    if len(features) < 30:
        fail(f'Track C must audit at least 30 features; got {len(features)}')
    for f in features:
        if f.get('status') not in TAXONOMY:
            fail(f'Track C feature {f.get("feature")!r} has invalid status {f.get("status")!r}')

    # 12) Track D: mismatches list non-empty + stamina violation flagged HIGH
    d = json.loads((AUDIT_DIR / 'canonical_mismatch_tech_debt_v1.json').read_text())
    if d.get('audit_only') is not True:
        fail('Track D audit_only must be True')
    if d.get('db_writes') != 0:
        fail('Track D db_writes must be 0')
    mismatches = d.get('mismatches', [])
    if not mismatches:
        fail('Track D mismatches must be non-empty')
    stamina_mm = [m for m in mismatches if m.get('id') == 'MISMATCH_NO_STAMINA_VIOLATION']
    if not stamina_mm:
        fail('Track D must include MISMATCH_NO_STAMINA_VIOLATION')
    if stamina_mm[0].get('severity') != 'HIGH':
        fail('Track D stamina violation must be severity HIGH')

    # 13) Track F: roadmap buckets present
    f_track = json.loads((AUDIT_DIR / 'mode_implementation_priority_roadmap_v1.json').read_text())
    if f_track.get('audit_only') is not True:
        fail('Track F audit_only must be True')
    buckets = f_track.get('priority_buckets', {})
    for b_name in ('P0_release_blockers', 'P1_core_playable_mode_completion',
                   'P2_live_modes', 'P3_polish_asset_audio'):
        if not buckets.get(b_name):
            fail(f'Track F priority_buckets.{b_name} must be non-empty')
    est = f_track.get('honest_project_completion_estimate', {})
    for k in ('design_architecture_pct', 'runtime_playable_pct',
              'release_ready_excluding_graphics_audio_pct',
              'release_ready_including_graphics_audio_pct'):
        v = est.get(k)
        if not isinstance(v, (int, float)) or not (0 <= v <= 100):
            fail(f'Track F honest_project_completion_estimate.{k} must be 0..100; got {v}')

    print('[PASS] PROJECT_FULL_RUNTIME_FEATURE_REALITY_AUDIT_WITH_TEST_ASSET_REGISTRY master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
