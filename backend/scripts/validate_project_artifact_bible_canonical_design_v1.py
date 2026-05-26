#!/usr/bin/env python3
"""
PROJECT_ARTIFACT_BIBLE_CANONICAL_DESIGN master validator (design-only).

Verifica end-to-end:
  - Track A: audit JSON presente + classifica routes correttamente
  - Track B: taxonomy v1 con 10 categorie canoniche
  - Track C: Bible draft con 30-40 entries, fields required, no P2W stats
  - Track D: boundary documenta 5 sistemi ortogonali
  - Track E: lock policy /artifacts redirect, /artifacts-preview read-only
  - Track F: migration plan 10 stage, stage 1 db_writes=0
  - Track G: guards documentati >= 6
  - Track I: completion JSON con design_only_mode=True e runtime_changes=0
  - Static guards reali:
      * HIDDEN_BANNERS_V2 = {'artifact','constellation'} in gacha.tsx
      * artifacts.tsx fa solo redirect
      * artifacts-preview.tsx senza mutation calls verso /api/artifacts/* o /api/constellations/*
      * battle_engine.py / battle_core.py senza riferimenti a user_artifacts/user_constellations
  - Invarianti: battle_engine.py + .env md5 intatti

NESSUN DB WRITE. PURE STATIC.
"""
import json, sys, hashlib, re
from pathlib import Path

ROOT = Path('/app')

def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def load_json(rel): return json.loads((ROOT / rel).read_text())

def main():
    # ---- Track A
    a = load_json('data/design/artifacts/artifact_existing_surface_audit_v1.json')
    assert a['verdict'] == 'TRACK_A_EXISTING_ARTIFACT_SURFACE_AUDIT_READY'
    assert a['runtime_combat_artifact_wiring'] is False
    assert a['runtime_combat_constellation_wiring'] is False
    # Frontend surfaces classification
    fs = {s['path']: s for s in a['frontend_surfaces']}
    assert fs['frontend/app/artifacts.tsx']['lock_status'] == 'locked_redirect'
    assert fs['frontend/app/artifacts-preview.tsx']['lock_status'] == 'preview_only_read_only'

    # ---- Track B
    b = load_json('data/design/artifacts/artifact_canonical_taxonomy_v1.json')
    assert b['verdict'] == 'TRACK_B_ARTIFACT_CANONICAL_TAXONOMY_READY'
    cat_ids = {c['id'] for c in b['categories']}
    required_cats = {'divine_relic', 'mythic_weapon_relic', 'sacred_symbol',
                     'primordial_fragment', 'pantheon_emblem', 'world_memory',
                     'forbidden_relic', 'event_relic', 'collaboration_relic',
                     'hero_signature_relic'}
    assert required_cats.issubset(cat_ids), f'missing categories: {required_cats - cat_ids}'

    # ---- Track C: Bible draft
    c = load_json('data/design/artifacts/artifact_bible_launch_draft_v1.json')
    assert c['verdict'] == 'TRACK_C_ARTIFACT_BIBLE_LAUNCH_DRAFT_READY'
    n = c['entries_count']
    assert 30 <= n <= 40, f'bible entries {n} not in 30-40'
    assert len(c['artifacts']) == n
    # Required fields per entry
    required_fields = ['artifact_id', 'display_name_it', 'category', 'faction_or_origin',
                       'associated_hero_id', 'associated_character_status', 'rarity_band',
                       'release_status', 'gameplay_status', 'short_lore_it',
                       'visual_identity', 'forbidden_interpretations',
                       'source_hint_future', 'ui_copy_short_it']
    for e in c['artifacts']:
        for f in required_fields:
            assert f in e, f"entry {e.get('artifact_id')} missing field {f}"
        # gameplay_status must be cosmetic_prestige_only / capped_bonus_future / inactive
        assert e['gameplay_status'] in {'cosmetic_prestige_only', 'capped_bonus_future', 'inactive'}
        # associated_character_status must be one of allowed
        assert e['associated_character_status'] in {'none', 'current_launch', 'future_reserved'}
    assert c['no_p2w_stat_bonus_in_bible'] is True

    # ---- Track D
    d = load_json('data/design/artifacts/artifact_constellation_relic_boundary_v1.json')
    assert d['verdict'] == 'TRACK_D_CONSTELLATION_AND_RELIC_BOUNDARY_READY'
    sys_keys = set(d['systems'].keys())
    assert sys_keys == {'artifacts', 'constellations', 'divine_weapons', 'equipment', 'runes'}

    # ---- Track E
    e = load_json('data/design/artifacts/artifact_preview_ui_copy_lock_policy_v1.json')
    assert e['verdict'] == 'TRACK_E_ARTIFACT_PREVIEW_UI_COPY_AND_LOCK_POLICY_READY'
    assert e['routes']['/artifacts']['status'] == 'locked_redirect'
    assert e['routes']['/artifacts-preview']['status'] == 'preview_read_only'
    assert e['placeholder_names_policy']['legacy_backend_names_visible_in_player_ui'] is False

    # ---- Track F
    f = load_json('data/design/artifacts/artifact_migration_import_plan_v1.json')
    assert f['verdict'] == 'TRACK_F_ARTIFACT_MIGRATION_AND_IMPORT_PLAN_READY'
    assert len(f['stages']) == 10
    assert f['stages'][0]['db_writes'] is False
    assert f['current_stage'] == 1
    assert f['db_writes_in_current_pack'] == 0

    # ---- Track G
    g = load_json('data/design/artifacts/artifact_static_guard_beta_harness_v1.json')
    assert g['verdict'] == 'TRACK_G_ARTIFACT_STATIC_GUARD_BETA_HARNESS_READY'
    assert len(g['guards']) >= 6
    assert g['package_json_stable'] is True
    assert g['yarn_lock_stable'] is True

    # ---- Track I + invariants
    i = load_json('data/design/artifacts/artifact_bible_canonical_design_completion_v1.json')
    assert i['verdict'] == 'TRACK_I_ARTIFACT_BIBLE_COMPLETION_READY'
    assert i['design_only_mode'] is True
    rc = i['runtime_changes_made']
    for k in ('frontend_route_changes', 'frontend_logic_changes', 'backend_route_changes',
              'backend_logic_changes', 'db_writes_from_scripts', 'battle_engine_changes',
              'gacha_rate_changes'):
        assert rc[k] == 0, f'{k} must be 0'
    for kb in ('iap_implementation', 'artifact_banner_activation',
               'constellation_banner_activation', 'character_bible_mutation'):
        assert rc[kb] is False, f'{kb} must be False'
    inv = i['files_untouched_critical_invariants']
    assert md5('/app/backend/battle_engine.py') == inv['backend/battle_engine.py'], 'battle_engine.py drift'
    assert md5('/app/backend/.env') == inv['backend/.env'], '.env drift'

    # ---- Live static guards (read filesystem)
    gacha_text = (ROOT / 'frontend/app/(tabs)/gacha.tsx').read_text()
    assert "HIDDEN_BANNERS_V2 = new Set(['artifact', 'constellation'])" in gacha_text, \
        "HIDDEN_BANNERS_V2 missing artifact/constellation"

    art_text = (ROOT / 'frontend/app/artifacts.tsx').read_text()
    assert "router.replace('/artifacts-preview')" in art_text, "artifacts.tsx must redirect"
    # No live mutation in artifacts.tsx
    for bad in ('apiCall(', 'fetch(', '/api/artifacts/pull', '/api/artifacts/fuse',
                '/api/artifacts/equip'):
        assert bad not in art_text, f'artifacts.tsx contains forbidden mutation token: {bad}'

    prev_text = (ROOT / 'frontend/app/artifacts-preview.tsx').read_text()
    for bad in ('/api/artifacts/pull', '/api/artifacts/fuse', '/api/artifacts/equip',
                '/api/constellations/equip', '/api/constellations/fuse'):
        assert bad not in prev_text, f'artifacts-preview.tsx contains forbidden endpoint: {bad}'

    be_text = (ROOT / 'backend/battle_engine.py').read_text()
    bc_text = (ROOT / 'backend/battle_core.py').read_text() if (ROOT / 'backend/battle_core.py').exists() else ''
    for bad in ('user_artifacts', 'user_constellations'):
        assert bad not in be_text, f'battle_engine.py references {bad} \u2014 forbidden'
        assert bad not in bc_text, f'battle_core.py references {bad} \u2014 forbidden'

    print('[PASS] PROJECT_ARTIFACT_BIBLE_CANONICAL_DESIGN master validator')
    return 0

if __name__ == '__main__':
    sys.exit(main())
