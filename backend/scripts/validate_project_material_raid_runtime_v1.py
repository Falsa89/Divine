#!/usr/bin/env python3
"""
PROJECT_MATERIAL_RAID_RUNTIME validator (statico, OPTIONAL).

Asserisce:
  - 10 JSON design tracks (A..J) + 1 proof marker presenti e validi
  - tutti i JSON con task_id == PROJECT_MATERIAL_RAID_RUNTIME
  - MD5 invarianti baseline su 5 file protetti
  - backend route file presente con feature flag e endpoints corretti
  - frontend constants/test sandbox presenti
  - server.py include material_raid_preview_router
  - 5 tracks canonici (2 open preview + 3 locked deferred)
  - 5 stage canonici (I, II, III, IV, V)
  - 5 reward families (gear, hero_growth, gem_locked, rune_locked, artifact_divine_locked)
  - db_writes = 0, materials_granted = false, mutation_enabled = false
  - reward_claim_enabled = false (PREVIEW-ONLY policy)
  - stamina_used = false, tickets_used = false
  - runtime_mode == PREVIEW_ONLY
  - legacy /raids/*, /inventory NON referenziati dal backend gated route
  - separation da Hero Elevation/Gemme/Rune/Artifact/DW/BP Delta/Gear Forge commit
  - validator NON indebolisce alcun REQUIRED validator

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path('/app')
DIR = ROOT / 'data/design/material_raid_runtime'

REQUIRED_JSON = {
    'A_material_raid_surface_audit_v1.json':                  'TRACK_A_MATERIAL_RAID_SURFACE_AUDIT_READY',
    'B_material_raid_schema_config_v1.json':                  'TRACK_B_MATERIAL_RAID_SCHEMA_CONFIG_READY',
    'C_backend_material_raid_preview_or_runtime_v1.json':     'TRACK_C_BACKEND_MATERIAL_RAID_PREVIEW_OR_RUNTIME_READY',
    'D_frontend_material_raid_ui_mvp_v1.json':                'TRACK_D_FRONTEND_MATERIAL_RAID_UI_MVP_READY',
    'E_material_reward_economy_boundary_v1.json':             'TRACK_E_MATERIAL_REWARD_ECONOMY_BOUNDARY_READY',
    'F_guide_codex_and_tutorial_links_v1.json':               'TRACK_F_GUIDE_CODEX_AND_TUTORIAL_LINKS_READY',
    'G_test_asset_audio_registry_v1.json':                    'TRACK_G_TEST_ASSET_AUDIO_REGISTRY_READY',
    'H_validator_and_suite_registration_v1.json':             'TRACK_H_VALIDATOR_AND_SUITE_REGISTRATION_READY',
    'I_smoke_and_qa_v1.json':                                 'TRACK_I_SMOKE_AND_QA_READY',
    'J_completion_and_public_sync_v1.json':                   'TRACK_J_COMPLETION_AND_PUBLIC_SYNC_READY',
}
PROOF_MARKER = DIR / 'material_raid_runtime_suite_registration_proof_marker_v1.json'

RUNTIME_FILES = [
    ROOT / 'backend/routes/material_raid_preview.py',
    ROOT / 'frontend/constants/materialRaid.ts',
    ROOT / 'frontend/app/material-raid-test.tsx',
]

MD5_INVARIANTS = {
    'backend/battle_engine.py':    '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':                'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx':        '45fcc9890b6b128c37088bc33aa54caf',
}

CANONICAL_TRACK_IDS_OPEN = ['gear_material_raid', 'hero_growth_raid']
CANONICAL_TRACK_IDS_LOCKED = ['gem_material_raid', 'rune_material_raid', 'artifact_divine_material_raid']
CANONICAL_STAGE_IDS = ['I', 'II', 'III', 'IV', 'V']
CANONICAL_REWARD_FAMILIES = ['gear', 'hero_growth', 'gem_locked', 'rune_locked', 'artifact_divine_locked']


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
        if data.get('task_id') != 'PROJECT_MATERIAL_RAID_RUNTIME':
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
    track_ids = [t.get('track_id') for t in (track_b.get('tracks') or [])]
    for needed in CANONICAL_TRACK_IDS_OPEN + CANONICAL_TRACK_IDS_LOCKED:
        if needed not in track_ids:
            fail(f'track B missing track_id: {needed}')
    if (track_b.get('stage_model') or {}).get('stages_per_open_track') != 5:
        fail('track B stage_model.stages_per_open_track must be 5')
    if (track_b.get('stage_model') or {}).get('no_stamina') is not True:
        fail('track B stage_model.no_stamina must be true')
    for sid in CANONICAL_STAGE_IDS:
        if sid not in (track_b.get('stage_recommended_power') or {}):
            fail(f'track B stage_recommended_power missing {sid}')
    for fam in CANONICAL_REWARD_FAMILIES:
        if fam not in (track_b.get('reward_families_canonical') or {}):
            fail(f'track B reward_families_canonical missing family: {fam}')

    # 4) Track C runtime mode + endpoints + reward claim disabled
    if track_c is None:
        fail('track C not loaded')
    if track_c.get('chosen_runtime_mode') != 'PREVIEW_ONLY':
        fail(f'track C chosen_runtime_mode must be PREVIEW_ONLY, got {track_c.get("chosen_runtime_mode")}')
    if track_c.get('reward_claim_endpoint_added') is not False:
        fail('track C reward_claim_endpoint_added must be false in this pack')
    if track_c.get('legacy_raids_routes_modified') is not False:
        fail('track C legacy_raids_routes_modified must be false')
    needed_paths = [
        '/api/material-raid/config', '/api/material-raid/stages',
        '/api/material-raid/reward-preview', '/api/material-raid/clear-preview',
    ]
    endpoint_paths = [e.get('path') for e in (track_c.get('endpoints') or [])]
    for needed in needed_paths:
        if needed not in endpoint_paths:
            fail(f'track C missing endpoint: {needed}')

    # 5) Track E economy boundary
    if track_e is None:
        fail('track E not loaded')
    if track_e.get('reward_claim_enabled') is not False:
        fail('track E reward_claim_enabled must be false in this pack')
    if track_e.get('materials_granted_in_this_pack') is not False:
        fail('track E materials_granted_in_this_pack must be false')
    if track_e.get('stamina_consumed_in_this_pack') is not False:
        fail('track E stamina_consumed_in_this_pack must be false')

    # 6) Proof marker
    if not PROOF_MARKER.exists():
        fail(f'missing proof marker: {PROOF_MARKER}')
    marker = json.loads(PROOF_MARKER.read_text())
    expected_marker_verdict = 'PROJECT_MATERIAL_RAID_RUNTIME_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
    if marker.get('verdict') != expected_marker_verdict:
        fail(f'proof marker verdict mismatch: expected {expected_marker_verdict}, got {marker.get("verdict")!r}')
    if marker.get('mutation_enabled') is not False:
        fail('marker mutation_enabled must be false (preview-only)')
    if marker.get('db_writes') != 0:
        fail(f'marker db_writes must be 0, got {marker.get("db_writes")}')
    if marker.get('materials_granted') is not False:
        fail('marker materials_granted must be false')
    if marker.get('reward_claim_enabled') is not False:
        fail('marker reward_claim_enabled must be false')
    if marker.get('stamina_used') is not False:
        fail('marker stamina_used must be false')
    if marker.get('tickets_used') is not False:
        fail('marker tickets_used must be false')
    if marker.get('paid_attempts') is not False:
        fail('marker paid_attempts must be false')
    if marker.get('runtime_mode') != 'PREVIEW_ONLY':
        fail(f'marker runtime_mode must be PREVIEW_ONLY, got {marker.get("runtime_mode")}')
    seps = marker.get('separation_from_other_layers') or []
    for needed in ['hero_elevation', 'gemme', 'rune_scroll_talisman', 'artifact',
                   'divine_weapon', 'bp_delta', 'combat_formulas', 'battle_engine',
                   'gear_forge_commit']:
        if needed not in seps:
            fail(f'marker separation_from_other_layers missing: {needed}')

    # 7) Constraints honored
    constraints = marker.get('constraints_honored') or {}
    must_be_true = [
        'no_live_material_grant', 'no_db_writes', 'no_stamina', 'no_tickets',
        'no_paid_attempts', 'no_drop_tables_live_economy', 'no_gear_forge_commit_enabling',
        'no_gem_runtime', 'no_rune_runtime', 'no_artifact_runtime',
        'no_divine_weapon_runtime', 'no_bp_delta_runtime',
        'no_hero_elevation_changes', 'no_gear_cap_preview_route_behavior_changes',
        'no_combat_formula_changes', 'no_battle_engine_changes', 'no_combat_tsx_changes',
        'no_character_bible_mutation', 'no_hero_final_numbers_changes',
        'no_layout_tsx_changes', 'no_home_menu_changes',
        'no_tower_or_guide_runtime_changes', 'no_shop_bp_vip_iap_unlock',
        'no_server_profiles_live', 'no_broad_db_migration', 'no_economy_live_change',
        'no_legacy_raids_or_inventory_routes_modified',
        'no_required_or_optional_validator_weakening', 'no_tuple_duplicate', 'no_fake_pass',
    ]
    for k in must_be_true:
        if not constraints.get(k):
            fail(f'constraint not honored: {k}')

    # 8) Runtime files exist
    for p in RUNTIME_FILES:
        if not p.exists():
            fail(f'missing runtime file: {p}')

    # 9) Backend file specifics
    backend_src = (ROOT / 'backend/routes/material_raid_preview.py').read_text()
    for needed in [
        'MATERIAL_RAID_RUNTIME_PREVIEW_ENABLED',
        '/api/material-raid',
        'MATERIAL_RAID_TRACKS',
        'STAGE_RECOMMENDED_POWER',
        'REWARD_FAMILIES',
        'reward_claim_enabled',
        'db_writes',
        '503',
        'preview_only',
    ]:
        if needed not in backend_src:
            fail(f'backend material_raid_preview.py missing: {needed!r}')
    # Must NOT touch user_materials / users / inventory / active_raids in this pack
    for forbidden in ['db.user_materials', 'db.inventory', 'db.active_raids',
                      'db.users.find', 'db.users.update', 'await db.']:
        if forbidden in backend_src:
            fail(f'backend material_raid_preview.py must NOT reference DB: {forbidden!r}')

    # 10) server.py includes router
    server_src = (ROOT / 'backend/server.py').read_text()
    if 'material_raid_preview' not in server_src:
        fail('backend/server.py missing material_raid_preview include')

    # 11) Frontend constants tracks + stages + families
    consts_src = (ROOT / 'frontend/constants/materialRaid.ts').read_text()
    for needed in ['MATERIAL_RAID_TRACKS', 'MATERIAL_RAID_STAGE_IDS',
                   'MATERIAL_RAID_RECOMMENDED_POWER', 'MATERIAL_RAID_REWARD_FAMILIES',
                   'describeRuntimeState']:
        if needed not in consts_src:
            fail(f'frontend/constants/materialRaid.ts missing export: {needed}')
    for tid in CANONICAL_TRACK_IDS_OPEN + CANONICAL_TRACK_IDS_LOCKED:
        if f"'{tid}'" not in consts_src:
            fail(f'frontend/constants/materialRaid.ts missing track_id {tid}')
    for sid in CANONICAL_STAGE_IDS:
        if f"'{sid}'" not in consts_src:
            fail(f'frontend/constants/materialRaid.ts missing stage_id {sid}')

    # 12) Frontend test screen sanity
    test_src = (ROOT / 'frontend/app/material-raid-test.tsx').read_text()
    if 'MATERIAL_RAID_TRACKS' not in test_src or 'MATERIAL_RAID_STAGE_IDS' not in test_src:
        fail('material-raid-test.tsx must use MATERIAL_RAID_TRACKS and MATERIAL_RAID_STAGE_IDS')

    print('[PASS] PROJECT_MATERIAL_RAID_RUNTIME master validator')


if __name__ == '__main__':
    main()
