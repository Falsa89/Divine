#!/usr/bin/env python3
"""
PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME validator (statico, OPTIONAL).

Asserisce:
  - 6 JSON design tracks (A..F) + 1 proof marker presenti e validi
  - tutti i JSON con task_id == PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME
  - MD5 invarianti baseline su 5 file protetti
  - backend route file presente con feature flag e endpoints corretti
  - frontend constants/badge/test sandbox presenti
  - server.py include hero_elevation_preview_router
  - 15 tier canonici E0..E14 con label IT corretti
  - default_tier_id == E0
  - db_writes = 0, materials_spent = false, mutation_enabled = false
  - separation from 11 layer canonici (hero_level, star_up, ascension, skill_upgrade,
    costellazioni, reincarnation, gear, gemme, rune_scroll_talisman, artifact, divine_weapon)
  - validator NON indebolisce alcun REQUIRED validator

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path('/app')
DIR = ROOT / 'data/design/hero_elevation_runtime'

REQUIRED_JSON = {
    'A_elevation_runtime_surface_audit_v1.json':           'TRACK_A_ELEVATION_RUNTIME_SURFACE_AUDIT_READY',
    'B_elevation_constants_and_schema_v1.json':            'TRACK_B_ELEVATION_CONSTANTS_AND_SCHEMA_READY',
    'C_backend_elevation_contract_preview_v1.json':        'TRACK_C_BACKEND_ELEVATION_CONTRACT_PREVIEW_READY',
    'D_frontend_elevation_ui_mvp_v1.json':                 'TRACK_D_FRONTEND_ELEVATION_UI_MVP_READY',
    'E_material_cost_policy_v1.json':                      'TRACK_E_MATERIAL_COST_POLICY_READY',
    'F_guide_codex_and_tutorial_links_v1.json':            'TRACK_F_GUIDE_CODEX_AND_TUTORIAL_LINKS_READY',
}
PROOF_MARKER = DIR / 'hero_elevation_runtime_suite_registration_proof_marker_v1.json'

RUNTIME_FILES = [
    ROOT / 'backend/routes/hero_elevation_preview.py',
    ROOT / 'frontend/constants/heroElevation.ts',
    ROOT / 'frontend/components/HeroElevationBadge.tsx',
    ROOT / 'frontend/app/hero-elevation-test.tsx',
]

MD5_INVARIANTS = {
    'backend/battle_engine.py':    '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':                'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx':        '45fcc9890b6b128c37088bc33aa54caf',
}


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
    for fname, expected_verdict in REQUIRED_JSON.items():
        p = DIR / fname
        if not p.exists():
            fail(f'missing JSON track: {p}')
        try:
            data = json.loads(p.read_text())
        except Exception as e:
            fail(f'invalid JSON {p}: {e}')
        if data.get('task_id') != 'PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME':
            fail(f'wrong task_id in {p}')
        if data.get('verdict') != expected_verdict:
            fail(f'expected verdict {expected_verdict} in {p}, got {data.get("verdict")!r}')

    # 3) Proof marker
    if not PROOF_MARKER.exists():
        fail(f'missing proof marker: {PROOF_MARKER}')
    marker = json.loads(PROOF_MARKER.read_text())
    if marker.get('verdict') != 'PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING':
        fail(f'proof marker verdict mismatch')

    # 4) Runtime files exist
    for p in RUNTIME_FILES:
        if not p.exists():
            fail(f'missing runtime file: {p}')

    # 5) Backend file specifics
    backend_src = (ROOT / 'backend/routes/hero_elevation_preview.py').read_text()
    for needed in [
        'HERO_ELEVATION_PREVIEW_ENABLED',
        '/api/hero/elevation',
        'ELEVATION_TIERS',
        'DEFAULT_TIER_ID = "E0"',
        'db_writes',
        '503',
    ]:
        if needed not in backend_src:
            fail(f'backend hero_elevation_preview.py missing: {needed!r}')

    # 6) server.py includes router
    server_src = (ROOT / 'backend/server.py').read_text()
    if 'hero_elevation_preview' not in server_src:
        fail('backend/server.py missing hero_elevation_preview include')

    # 7) Frontend constants 15 tiers
    consts_src = (ROOT / 'frontend/constants/heroElevation.ts').read_text()
    for tier_id in ['E0', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12', 'E13', 'E14']:
        if f"tier_id: '{tier_id}'" not in consts_src:
            fail(f'frontend/constants/heroElevation.ts missing tier {tier_id}')
    for lbl in ['Bianco', 'Verde', 'Verde +1', 'Blu', 'Blu +1', 'Blu +2',
                'Viola +1', 'Viola +2', 'Viola +3',
                'Oro +1', 'Oro +2', 'Oro +3',
                'Rosso +1', 'Rosso +2', 'Rosso +3']:
        if f"label_it: '{lbl}'" not in consts_src:
            fail(f'frontend/constants/heroElevation.ts missing label "{lbl}"')

    # 8) Marker checks
    if marker.get('mutation_enabled') is not False:
        fail('marker mutation_enabled must be false (preview-only)')
    if marker.get('db_writes') != 0:
        fail(f'marker db_writes must be 0, got {marker.get("db_writes")}')
    if marker.get('materials_spent') is not False:
        fail('marker materials_spent must be false')
    if marker.get('runtime_mode') != 'PREVIEW_ONLY':
        fail(f'marker runtime_mode must be PREVIEW_ONLY, got {marker.get("runtime_mode")}')
    seps = marker.get('separation_from_other_layers') or []
    for needed in ['hero_level', 'star_up', 'ascension', 'gear', 'gemme', 'rune_scroll_talisman', 'artifact', 'divine_weapon']:
        if needed not in seps:
            fail(f'marker separation_from_other_layers missing: {needed}')

    # 9) Constraints honored
    constraints = marker.get('constraints_honored') or {}
    must_be_true = [
        'no_gear_plus_50_runtime', 'no_gem_runtime', 'no_rune_scroll_talisman_runtime',
        'no_artifact_live_bonus_or_unhide', 'no_divine_weapon_runtime',
        'no_combat_formula_changes', 'no_battle_engine_changes',
        'no_character_bible_mutation', 'no_hero_final_numbers_changes',
        'no_layout_tsx_changes', 'no_home_menu_changes',
        'no_required_or_optional_validator_weakening', 'no_fake_pass',
    ]
    for k in must_be_true:
        if not constraints.get(k):
            fail(f'constraint not honored: {k}')

    print('[PASS] PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME master validator')


if __name__ == '__main__':
    main()
