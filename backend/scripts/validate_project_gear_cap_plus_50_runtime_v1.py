#!/usr/bin/env python3
"""
PROJECT_GEAR_CAP_PLUS_50_RUNTIME validator (statico, OPTIONAL).

Asserisce:
  - 9 JSON design tracks (A..I) + 1 proof marker presenti e validi
  - tutti i JSON con task_id == PROJECT_GEAR_CAP_PLUS_50_RUNTIME
  - MD5 invarianti baseline su 5 file protetti
  - backend route file presente con feature flag e endpoints corretti
  - frontend constants/badge/test sandbox presenti
  - server.py include gear_cap_preview_router
  - cap canonical = 50, cap legacy = 20
  - 4 stage canonici (early/mid/late/endgame) con ranges 0-10 / 11-20 / 21-35 / 36-50
  - 6 slot canonici (weapon/armor/helm/boots/gloves/accessory)
  - db_writes = 0, materials_spent = false, mutation_enabled = false
  - runtime_mode == PREVIEW_ONLY
  - separation da Hero Elevation, Gemme, Rune, Artifact, Divine Weapon, BP Delta
  - validator NON indebolisce alcun REQUIRED validator

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path('/app')
DIR = ROOT / 'data/design/gear_cap_plus_50'

REQUIRED_JSON = {
    'A_gear_cap_runtime_surface_audit_v1.json':       'TRACK_A_GEAR_CAP_RUNTIME_SURFACE_AUDIT_READY',
    'B_gear_cap_constants_and_schema_v1.json':        'TRACK_B_GEAR_CAP_CONSTANTS_AND_SCHEMA_READY',
    'C_backend_gear_cap_contract_preview_v1.json':    'TRACK_C_BACKEND_GEAR_CAP_CONTRACT_PREVIEW_READY',
    'D_frontend_gear_cap_ui_mvp_v1.json':             'TRACK_D_FRONTEND_GEAR_CAP_UI_MVP_READY',
    'E_material_cost_policy_v1.json':                 'TRACK_E_MATERIAL_COST_POLICY_READY',
    'F_legacy_plus_20_migration_debt_v1.json':        'TRACK_F_LEGACY_PLUS_20_MIGRATION_DEBT_READY',
    'G_separation_from_other_layers_v1.json':         'TRACK_G_SEPARATION_FROM_OTHER_LAYERS_READY',
    'H_guide_codex_and_tutorial_links_v1.json':       'TRACK_H_GUIDE_CODEX_AND_TUTORIAL_LINKS_READY',
    'I_release_gates_and_rollback_v1.json':           'TRACK_I_RELEASE_GATES_AND_ROLLBACK_READY',
}
PROOF_MARKER = DIR / 'gear_cap_plus_50_runtime_suite_registration_proof_marker_v1.json'

RUNTIME_FILES = [
    ROOT / 'backend/routes/gear_cap_preview.py',
    ROOT / 'frontend/constants/gearCap.ts',
    ROOT / 'frontend/components/GearCapBadge.tsx',
    ROOT / 'frontend/app/gear-cap-test.tsx',
]

MD5_INVARIANTS = {
    'backend/battle_engine.py':    '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':                'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx':        '45fcc9890b6b128c37088bc33aa54caf',
}

CANONICAL_STAGES = [
    ('early',   0,  10),
    ('mid',     11, 20),
    ('late',    21, 35),
    ('endgame', 36, 50),
]
CANONICAL_SLOTS = ['weapon', 'armor', 'helm', 'boots', 'gloves', 'accessory']


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    # 1) MD5 invariants
    for rel, exp in MD5_INVARIANTS.items():
        p = ROOT / rel
        if not p.exists():
            fail(f'missing MD5-protected file: {rel}')
        h = hashlib.md5(p.read_bytes()).hexdigest()
        if h != exp:
            fail(f'MD5 mismatch on {rel}: expected={exp} actual={h}')

    # 2) Design JSON tracks
    track_b = None
    for fname, expected_verdict in REQUIRED_JSON.items():
        p = DIR / fname
        if not p.exists():
            fail(f'missing JSON track: {p}')
        try:
            data = json.loads(p.read_text())
        except Exception as e:
            fail(f'invalid JSON {p}: {e}')
        if data.get('task_id') != 'PROJECT_GEAR_CAP_PLUS_50_RUNTIME':
            fail(f'wrong task_id in {p}: {data.get("task_id")!r}')
        if data.get('verdict') != expected_verdict:
            fail(f'expected verdict {expected_verdict} in {p}, got {data.get("verdict")!r}')
        if fname.startswith('B_'):
            track_b = data

    # 3) Track B canonical schema
    if track_b is None:
        fail('track B not loaded')
    if track_b.get('gear_level_cap_canonical') != 50:
        fail(f'track B gear_level_cap_canonical must be 50, got {track_b.get("gear_level_cap_canonical")}')
    if track_b.get('gear_level_cap_legacy_to_replace') != 20:
        fail(f'track B gear_level_cap_legacy_to_replace must be 20, got {track_b.get("gear_level_cap_legacy_to_replace")}')
    staged = track_b.get('staged_caps') or []
    if len(staged) != 4:
        fail(f'track B staged_caps must have 4 entries, got {len(staged)}')
    for (sid, smin, smax), entry in zip(CANONICAL_STAGES, staged):
        if entry.get('stage_id') != sid:
            fail(f'track B staged_caps order/id mismatch: expected {sid}, got {entry.get("stage_id")}')
        if entry.get('min') != smin or entry.get('max') != smax:
            fail(f'track B stage {sid} range mismatch: expected {smin}-{smax}, got {entry.get("min")}-{entry.get("max")}')
    slot_ids = [s.get('slot_id') for s in (track_b.get('gear_slots') or [])]
    for needed in CANONICAL_SLOTS:
        if needed not in slot_ids:
            fail(f'track B missing canonical slot: {needed}')

    # 4) Proof marker
    if not PROOF_MARKER.exists():
        fail(f'missing proof marker: {PROOF_MARKER}')
    marker = json.loads(PROOF_MARKER.read_text())
    expected_marker_verdict = 'PROJECT_GEAR_CAP_PLUS_50_RUNTIME_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    if marker.get('verdict') != expected_marker_verdict:
        fail(f'proof marker verdict mismatch: expected {expected_marker_verdict}, got {marker.get("verdict")!r}')
    if marker.get('mutation_enabled') is not False:
        fail('marker mutation_enabled must be false (preview-only)')
    if marker.get('db_writes') != 0:
        fail(f'marker db_writes must be 0, got {marker.get("db_writes")}')
    if marker.get('materials_spent') is not False:
        fail('marker materials_spent must be false')
    if marker.get('runtime_mode') != 'PREVIEW_ONLY':
        fail(f'marker runtime_mode must be PREVIEW_ONLY, got {marker.get("runtime_mode")}')
    seps = marker.get('separation_from_other_layers') or []
    for needed in ['hero_elevation', 'gemme', 'rune_scroll_talisman', 'artifact',
                   'divine_weapon', 'bp_delta', 'combat_formulas', 'battle_engine']:
        if needed not in seps:
            fail(f'marker separation_from_other_layers missing: {needed}')

    # 5) Constraints honored
    constraints = marker.get('constraints_honored') or {}
    must_be_true = [
        'no_gem_runtime', 'no_rune_runtime', 'no_artifact_runtime',
        'no_divine_weapon_runtime', 'no_bp_delta_runtime',
        'no_hero_elevation_changes', 'no_combat_formula_changes',
        'no_battle_engine_changes', 'no_character_bible_mutation',
        'no_hero_final_numbers_changes', 'no_layout_tsx_changes',
        'no_home_menu_changes', 'no_tower_or_guide_runtime_changes',
        'no_shop_bp_vip_iap_unlock', 'no_server_profiles_live',
        'no_db_writes', 'no_materials_spent',
        'no_required_or_optional_validator_weakening', 'no_fake_pass',
    ]
    for k in must_be_true:
        if not constraints.get(k):
            fail(f'constraint not honored: {k}')

    # 6) Runtime files exist
    for p in RUNTIME_FILES:
        if not p.exists():
            fail(f'missing runtime file: {p}')

    # 7) Backend file specifics
    backend_src = (ROOT / 'backend/routes/gear_cap_preview.py').read_text()
    for needed in [
        'GEAR_CAP_PLUS_50_PREVIEW_ENABLED',
        '/api/gear-cap',
        'GEAR_CAP_CANONICAL = 50',
        'GEAR_CAP_LEGACY_TO_REPLACE = 20',
        'GEAR_STAGED_CAPS',
        'db_writes',
        '503',
        'preview_only_no_db_read_in_this_pack',
    ]:
        if needed not in backend_src:
            fail(f'backend gear_cap_preview.py missing: {needed!r}')

    # 8) server.py includes router
    server_src = (ROOT / 'backend/server.py').read_text()
    if 'gear_cap_preview' not in server_src:
        fail('backend/server.py missing gear_cap_preview include')

    # 9) Frontend constants stages + slots
    consts_src = (ROOT / 'frontend/constants/gearCap.ts').read_text()
    for needed in [
        'GEAR_CAP_CANONICAL',
        'GEAR_CAP_LEGACY_TO_REPLACE',
        'GEAR_STAGED_CAPS',
        'GEAR_SLOTS',
        'resolveGearStage',
    ]:
        if needed not in consts_src:
            fail(f'frontend/constants/gearCap.ts missing export: {needed}')
    for sid in ('early', 'mid', 'late', 'endgame'):
        if f"stage_id: '{sid}'" not in consts_src:
            fail(f'frontend/constants/gearCap.ts missing stage_id {sid}')
    for slot in CANONICAL_SLOTS:
        if f"slot_id: '{slot}'" not in consts_src:
            fail(f'frontend/constants/gearCap.ts missing slot_id {slot}')

    # 10) Frontend badge + test screen sanity
    badge_src = (ROOT / 'frontend/components/GearCapBadge.tsx').read_text()
    if 'GEAR_CAP_CANONICAL' not in badge_src or 'resolveGearStage' not in badge_src:
        fail('GearCapBadge.tsx must reference GEAR_CAP_CANONICAL and resolveGearStage')
    test_src = (ROOT / 'frontend/app/gear-cap-test.tsx').read_text()
    if 'GearCapBadge' not in test_src or 'GEAR_STAGED_CAPS' not in test_src:
        fail('gear-cap-test.tsx must use GearCapBadge and GEAR_STAGED_CAPS')

    print('[PASS] PROJECT_GEAR_CAP_PLUS_50_RUNTIME master validator')


if __name__ == '__main__':
    main()
