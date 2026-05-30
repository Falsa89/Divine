#!/usr/bin/env python3
"""
PROJECT_HERO_GEAR_PROGRESSION_BIBLE validator (statico, OPTIONAL).

Asserisce:
  - 10 JSON design tracks (A..J) + 1 proof marker presenti e validi
  - tutti i JSON con task_id == PROJECT_HERO_GEAR_PROGRESSION_BIBLE
  - decisioni canoniche lockate nel proof marker:
      gear_level_cap == 50
      gemme_definition contiene "socket_in_gear"
      rune_definition contiene "hero_equipped"
      rune_NOT_separate_from_scroll_etc == true
      artifact_scope contiene "global_account"
      divine_weapon_scope contiene "per_hero_6star"
  - MD5 invarianti baseline su 5 file protetti
  - design_only == true (no runtime change)
  - validator NON indebolisce alcun REQUIRED validator

Exit 0 su PASS, 1 su FAIL. Registrazione OPTIONAL.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path('/app')
DIR = ROOT / 'data/design/hero_gear_progression_bible'

REQUIRED_JSON = {
    'A_current_progression_audit_v1.json':                       'TRACK_A_CURRENT_PROGRESSION_AUDIT_READY',
    'B_hero_progression_layer_bible_v1.json':                    'TRACK_B_HERO_PROGRESSION_LAYER_BIBLE_READY',
    'C_hero_elevation_quality_frame_bible_v1.json':              'TRACK_C_HERO_ELEVATION_QUALITY_FRAME_BIBLE_READY',
    'D_gear_progression_bible_v1.json':                          'TRACK_D_GEAR_PROGRESSION_BIBLE_READY',
    'E_gem_socket_system_bible_v1.json':                         'TRACK_E_GEM_SOCKET_SYSTEM_BIBLE_READY',
    'F_rune_scroll_talisman_system_bible_v1.json':               'TRACK_F_RUNE_SCROLL_TALISMAN_SYSTEM_BIBLE_READY',
    'G_artifact_divine_weapon_separation_rules_v1.json':         'TRACK_G_ARTIFACT_DIVINE_WEAPON_SEPARATION_RULES_READY',
    'H_material_sources_and_mode_mapping_v1.json':               'TRACK_H_MATERIAL_SOURCES_AND_MODE_MAPPING_READY',
    'I_bp_delta_and_guide_tutorial_integration_v1.json':         'TRACK_I_BP_DELTA_AND_GUIDE_TUTORIAL_INTEGRATION_READY',
    'J_implementation_roadmap_and_release_gates_v1.json':        'TRACK_J_IMPLEMENTATION_ROADMAP_AND_RELEASE_GATES_READY',
}
PROOF_MARKER = DIR / 'hero_gear_progression_bible_suite_registration_proof_marker_v1.json'

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
        if data.get('task_id') != 'PROJECT_HERO_GEAR_PROGRESSION_BIBLE':
            fail(f'wrong task_id in {p}: {data.get("task_id")!r}')
        if data.get('verdict') != expected_verdict:
            fail(f'expected verdict {expected_verdict} in {p}, got {data.get("verdict")!r}')

    # 3) Proof marker
    if not PROOF_MARKER.exists():
        fail(f'missing proof marker: {PROOF_MARKER}')
    marker = json.loads(PROOF_MARKER.read_text())
    if marker.get('task_id') != 'PROJECT_HERO_GEAR_PROGRESSION_BIBLE':
        fail('proof marker task_id mismatch')
    if marker.get('verdict') != 'PROJECT_HERO_GEAR_PROGRESSION_BIBLE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING':
        fail(f'proof marker verdict mismatch: {marker.get("verdict")!r}')

    # 4) Canonical decisions locked
    decisions = marker.get('canonical_decisions_locked') or {}
    if decisions.get('gear_level_cap') != 50:
        fail(f'gear_level_cap must be 50, got {decisions.get("gear_level_cap")}')
    if 'socket_in_gear' not in (decisions.get('gemme_definition') or ''):
        fail('gemme_definition must contain "socket_in_gear"')
    if 'hero_equipped' not in (decisions.get('rune_definition') or ''):
        fail('rune_definition must contain "hero_equipped"')
    if decisions.get('rune_NOT_separate_from_scroll_etc') is not True:
        fail('rune_NOT_separate_from_scroll_etc must be true')
    if 'global_account' not in (decisions.get('artifact_scope') or ''):
        fail('artifact_scope must contain "global_account"')
    if 'per_hero_6star' not in (decisions.get('divine_weapon_scope') or ''):
        fail('divine_weapon_scope must contain "per_hero_6star"')
    if decisions.get('hero_elevation_separated_from_star_up_and_ascension') is not True:
        fail('hero_elevation_separated_from_star_up_and_ascension must be true')

    # 5) Track D specifics: gear cap 50, stages 4
    d = json.loads((DIR / 'D_gear_progression_bible_v1.json').read_text())
    if d.get('gear_level_cap_canonical') != 50:
        fail('D gear_level_cap_canonical != 50')
    stages = d.get('gear_level_stages') or []
    if len(stages) != 4:
        fail(f'D gear_level_stages must have 4 entries, got {len(stages)}')
    if not (stages[0]['min'] == 0 and stages[0]['max'] == 10):
        fail('D early stage must be 0..10')
    if not (stages[3]['min'] == 36 and stages[3]['max'] == 50):
        fail('D endgame stage must be 36..50')

    # 6) Track E gem placement
    e = json.loads((DIR / 'E_gem_socket_system_bible_v1.json').read_text())
    if e.get('placement') != 'socketed_in_gear':
        fail('E gem placement must be "socketed_in_gear"')
    if e.get('NOT_socketed_on_hero') is not True:
        fail('E NOT_socketed_on_hero must be true')

    # 7) Track F rune placement
    f = json.loads((DIR / 'F_rune_scroll_talisman_system_bible_v1.json').read_text())
    if f.get('placement') != 'equipped_on_hero_dedicated_slots':
        fail('F rune placement must be "equipped_on_hero_dedicated_slots"')
    if f.get('NOT_socketed_in_gear') is not True:
        fail('F NOT_socketed_in_gear must be true')
    aliases = f.get('aliases_unified_under_rune') or []
    for needed in ['scroll', 'talisman', 'pergamena', 'sigillo']:
        if needed not in aliases:
            fail(f'F aliases_unified_under_rune missing "{needed}"')

    # 8) Track G artifact/dw separation
    g = json.loads((DIR / 'G_artifact_divine_weapon_separation_rules_v1.json').read_text())
    if g['artifact_canonical_rules']['scope'] != 'global_account_roster':
        fail('G artifact scope must be global_account_roster')
    if g['divine_weapon_canonical_rules']['scope'] != 'per_hero_6star_only':
        fail('G divine_weapon scope must be per_hero_6star_only')

    # 9) design-only & constraints
    if marker.get('design_only') is not True:
        fail('marker design_only must be true')
    if marker.get('runtime_changes') is not False:
        fail('marker runtime_changes must be false')

    constraints = marker.get('constraints_honored') or {}
    must_be_true = [
        'no_runtime_hero_upgrade', 'no_runtime_gear_upgrade',
        'no_runtime_gem_rune', 'no_combat_or_battle_engine_changes',
        'no_hero_stats_or_final_numbers_changes', 'no_db_writes_or_migrations',
        'no_player_data_mutation', 'no_tower_guide_home_menu_runtime_changes',
        'no_required_or_optional_validator_weakening', 'no_fake_pass',
    ]
    for k in must_be_true:
        if not constraints.get(k):
            fail(f'constraint not honored: {k}')

    print('[PASS] PROJECT_HERO_GEAR_PROGRESSION_BIBLE master validator')


if __name__ == '__main__':
    main()
