#!/usr/bin/env python3
"""
PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME validator (statico, OPTIONAL).

Asserisce:
  - 9 JSON design tracks (A..I) + 1 proof marker presenti e validi
  - tutti i JSON con task_id == PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME
  - MD5 invarianti baseline su 5 file protetti
  - backend route file presente con feature flag e endpoints corretti
  - frontend constants/test sandbox presenti
  - server.py include gear_forge_preview_router
  - 4 subsystem canonici (enhance/fusion/reforge/enchant)
  - 6 qualita canoniche (common..mythic)
  - fusion_min_fodder == 3
  - db_writes = 0, materials_spent = false, mutation_enabled = false
  - fusion_commit_enabled = false (PREVIEW-ONLY policy)
  - runtime_mode == PREVIEW_ONLY
  - legacy /forge/* (backend/routes/forge.py) NON modificato (basta che esista, no MD5 check)
  - separation da Hero Elevation/Gemme/Rune/Artifact/DW/BP Delta/Material Raid
  - validator NON indebolisce alcun REQUIRED validator

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path('/app')
DIR = ROOT / 'data/design/gear_forge_fusion_reforge_runtime'

REQUIRED_JSON = {
    'A_forge_surface_audit_v1.json':                  'TRACK_A_FORGE_SURFACE_AUDIT_READY',
    'B_forge_schema_and_config_v1.json':              'TRACK_B_FORGE_SCHEMA_AND_CONFIG_READY',
    'C_backend_forge_preview_or_runtime_v1.json':     'TRACK_C_BACKEND_FORGE_PREVIEW_OR_RUNTIME_READY',
    'D_frontend_forge_ui_mvp_v1.json':                'TRACK_D_FRONTEND_FORGE_UI_MVP_READY',
    'E_fusion_safety_and_economy_policy_v1.json':     'TRACK_E_FUSION_SAFETY_AND_ECONOMY_POLICY_READY',
    'F_guide_codex_and_tutorial_links_v1.json':       'TRACK_F_GUIDE_CODEX_AND_TUTORIAL_LINKS_READY',
    'G_validator_and_suite_registration_v1.json':     'TRACK_G_VALIDATOR_AND_SUITE_REGISTRATION_READY',
    'H_smoke_and_qa_v1.json':                         'TRACK_H_SMOKE_AND_QA_READY',
    'I_completion_and_public_sync_v1.json':           'TRACK_I_COMPLETION_AND_PUBLIC_SYNC_READY',
}
PROOF_MARKER = DIR / 'gear_forge_fusion_reforge_runtime_suite_registration_proof_marker_v1.json'

RUNTIME_FILES = [
    ROOT / 'backend/routes/gear_forge_preview.py',
    ROOT / 'frontend/constants/gearForge.ts',
    ROOT / 'frontend/app/gear-forge-test.tsx',
]
LEGACY_FORGE_FILE = ROOT / 'backend/routes/forge.py'

MD5_INVARIANTS = {
    'backend/battle_engine.py':    '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':                'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx':        '45fcc9890b6b128c37088bc33aa54caf',
}

CANONICAL_SUBSYSTEMS = ['enhance', 'fusion', 'reforge', 'enchant']
CANONICAL_QUALITIES = ['common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic']


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
    track_c = None
    track_e = None
    for fname, expected_verdict in REQUIRED_JSON.items():
        p = DIR / fname
        if not p.exists():
            fail(f'missing JSON track: {p}')
        try:
            data = json.loads(p.read_text())
        except Exception as e:
            fail(f'invalid JSON {p}: {e}')
        if data.get('task_id') != 'PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME':
            fail(f'wrong task_id in {p}: {data.get("task_id")!r}')
        if data.get('verdict') != expected_verdict:
            fail(f'expected verdict {expected_verdict} in {p}, got {data.get("verdict")!r}')
        if fname.startswith('B_'):
            track_b = data
        if fname.startswith('C_'):
            track_c = data
        if fname.startswith('E_'):
            track_e = data

    # 3) Track B canonical schema
    if track_b is None:
        fail('track B not loaded')
    subsystem_ids = [s.get('id') for s in (track_b.get('forge_subsystems') or [])]
    for needed in CANONICAL_SUBSYSTEMS:
        if needed not in subsystem_ids:
            fail(f'track B missing subsystem: {needed}')
    gca = track_b.get('gear_cap_alignment') or {}
    if gca.get('cap_canonical') != 50:
        fail(f'track B gear_cap_alignment.cap_canonical must be 50, got {gca.get("cap_canonical")}')
    if gca.get('cap_legacy_to_replace') != 20:
        fail(f'track B gear_cap_alignment.cap_legacy_to_replace must be 20')
    if (track_b.get('fusion_rules_preview') or {}).get('min_fodder_for_quality_up') != 3:
        fail('track B fusion_rules_preview.min_fodder_for_quality_up must be 3')

    # 4) Track C runtime mode + endpoints + fusion commit disabled
    if track_c is None:
        fail('track C not loaded')
    if track_c.get('chosen_runtime_mode') != 'PREVIEW_ONLY':
        fail(f'track C chosen_runtime_mode must be PREVIEW_ONLY, got {track_c.get("chosen_runtime_mode")}')
    if track_c.get('fusion_commit_endpoint_added') is not False:
        fail('track C fusion_commit_endpoint_added must be false in this pack')
    if track_c.get('legacy_forge_routes_modified') is not False:
        fail('track C legacy_forge_routes_modified must be false')
    needed_paths = [
        '/api/gear-forge/config', '/api/gear-forge/fusion/preview',
        '/api/gear-forge/enhance/preview', '/api/gear-forge/reforge/preview',
        '/api/gear-forge/enchant/preview',
    ]
    endpoint_paths = [e.get('path') for e in (track_c.get('endpoints') or [])]
    for needed in needed_paths:
        if needed not in endpoint_paths:
            fail(f'track C missing endpoint: {needed}')

    # 5) Track E fusion safety
    if track_e is None:
        fail('track E not loaded')
    if track_e.get('fusion_commit_enabled') is not False:
        fail('track E fusion_commit_enabled must be false in this pack')

    # 6) Proof marker
    if not PROOF_MARKER.exists():
        fail(f'missing proof marker: {PROOF_MARKER}')
    marker = json.loads(PROOF_MARKER.read_text())
    expected_marker_verdict = 'PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    if marker.get('verdict') != expected_marker_verdict:
        fail(f'proof marker verdict mismatch: expected {expected_marker_verdict}, got {marker.get("verdict")!r}')
    if marker.get('mutation_enabled') is not False:
        fail('marker mutation_enabled must be false (preview-only)')
    if marker.get('db_writes') != 0:
        fail(f'marker db_writes must be 0, got {marker.get("db_writes")}')
    if marker.get('materials_spent') is not False:
        fail('marker materials_spent must be false')
    if marker.get('fusion_commit_enabled') is not False:
        fail('marker fusion_commit_enabled must be false')
    if marker.get('runtime_mode') != 'PREVIEW_ONLY':
        fail(f'marker runtime_mode must be PREVIEW_ONLY, got {marker.get("runtime_mode")}')
    seps = marker.get('separation_from_other_layers') or []
    for needed in ['hero_elevation', 'gemme', 'rune_scroll_talisman', 'artifact',
                   'divine_weapon', 'bp_delta', 'combat_formulas', 'battle_engine',
                   'material_raid_runtime']:
        if needed not in seps:
            fail(f'marker separation_from_other_layers missing: {needed}')

    # 7) Constraints honored
    constraints = marker.get('constraints_honored') or {}
    must_be_true = [
        'no_gem_runtime', 'no_rune_runtime', 'no_artifact_runtime',
        'no_divine_weapon_runtime', 'no_bp_delta_runtime',
        'no_hero_elevation_changes', 'no_gear_cap_preview_route_behavior_changes',
        'no_combat_formula_changes', 'no_battle_engine_changes', 'no_combat_tsx_changes',
        'no_character_bible_mutation', 'no_hero_final_numbers_changes',
        'no_layout_tsx_changes', 'no_home_menu_changes',
        'no_tower_or_guide_runtime_changes', 'no_shop_bp_vip_iap_unlock',
        'no_server_profiles_live', 'no_db_writes', 'no_materials_spent',
        'no_paid_currency', 'no_stamina_or_tickets', 'no_broad_db_migration',
        'no_material_raid_runtime', 'no_economy_live_change',
        'no_legacy_forge_routes_modified',
        'no_required_or_optional_validator_weakening', 'no_tuple_duplicate', 'no_fake_pass',
    ]
    for k in must_be_true:
        if not constraints.get(k):
            fail(f'constraint not honored: {k}')

    # 8) Runtime files exist
    for p in RUNTIME_FILES:
        if not p.exists():
            fail(f'missing runtime file: {p}')
    if not LEGACY_FORGE_FILE.exists():
        fail(f'legacy forge file missing (must exist, must remain intoccato): {LEGACY_FORGE_FILE}')

    # 9) Backend file specifics
    backend_src = (ROOT / 'backend/routes/gear_forge_preview.py').read_text()
    for needed in [
        'GEAR_FORGE_RUNTIME_PREVIEW_ENABLED',
        '/api/gear-forge',
        'GEAR_CAP_CANONICAL = 50',
        'FUSION_MIN_FODDER = 3',
        'fusion_commit_enabled',
        'db_writes',
        '503',
        'preview_only',
    ]:
        if needed not in backend_src:
            fail(f'backend gear_forge_preview.py missing: {needed!r}')
    # Must NOT touch user_equipment or users collection in this pack
    for forbidden in ['db.user_equipment', 'db.users.find', 'db.users.update', 'await db.']:
        if forbidden in backend_src:
            fail(f'backend gear_forge_preview.py must NOT reference DB: {forbidden!r}')

    # 10) server.py includes router
    server_src = (ROOT / 'backend/server.py').read_text()
    if 'gear_forge_preview' not in server_src:
        fail('backend/server.py missing gear_forge_preview include')

    # 11) Frontend constants subsystems + qualities
    consts_src = (ROOT / 'frontend/constants/gearForge.ts').read_text()
    for needed in ['FORGE_SUBSYSTEMS', 'FUSION_QUALITIES', 'FUSION_MIN_FODDER', 'describeSubsystemState']:
        if needed not in consts_src:
            fail(f'frontend/constants/gearForge.ts missing export: {needed}')
    for sid in CANONICAL_SUBSYSTEMS:
        if f"id: '{sid}'" not in consts_src:
            fail(f'frontend/constants/gearForge.ts missing subsystem id {sid}')
    for q in CANONICAL_QUALITIES:
        if f"'{q}'" not in consts_src:
            fail(f'frontend/constants/gearForge.ts missing quality {q}')

    # 12) Frontend test screen sanity
    test_src = (ROOT / 'frontend/app/gear-forge-test.tsx').read_text()
    if 'FORGE_SUBSYSTEMS' not in test_src or 'FUSION_QUALITIES' not in test_src:
        fail('gear-forge-test.tsx must use FORGE_SUBSYSTEMS and FUSION_QUALITIES')

    print('[PASS] PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME master validator')


if __name__ == '__main__':
    main()
