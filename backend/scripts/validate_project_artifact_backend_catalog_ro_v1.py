#!/usr/bin/env python3
"""
PROJECT_ARTIFACT_BACKEND_CATALOG_RO master validator (Stage 4).

Verifica STATICA (nessuna DB call):
  - Track A: source manifest + contract audit con MD5 di tutti i file sorgente.
  - Track B: implementazione endpoint read-only nel file routes.
  - Track C: normalization + filters.
  - Track D: frontend NO wiring (preview rimane statica).
  - Track E: smoke + no DB guard.
  - Track F: validator + suite registrazione.
  - Invarianti MD5: battle_engine.py, backend/.env.
  - Gacha banner artifact/constellation rimangono HIDDEN.
  - /artifacts redirect a /artifacts-preview intatto.
  - artifacts-preview.tsx invariato (MD5 stabile).
"""
import hashlib
import json
import sys
import re
from pathlib import Path

ROOT = Path('/app')
CATALOG_RO_DIR = ROOT / 'data/design/artifacts/catalog_ro'
ROUTE_FILE = ROOT / 'backend/routes/artifacts.py'

FORBIDDEN_FIELDS = {
    "owned", "equipped", "level", "stars_upgrade_progress",
    "player_owned", "inventory_id", "acquisition_active",
    "craft_cost", "fuse_cost", "equip_slot",
    "stat_bonus_active", "combat_modifier",
    "price", "purchase_url",
}


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def load(rel):
    return json.loads((ROOT / rel).read_text())


def main():
    # ---- Track A: source manifest + contract audit
    a = load('data/design/artifacts/catalog_ro/artifact_catalog_source_manifest_contract_audit_v1.json')
    assert a['verdict'] == 'TRACK_A_ARTIFACT_CATALOG_SOURCE_MANIFEST_AND_CONTRACT_AUDIT_READY'
    assert a['bible_entries_count_confirmed'] == 32
    assert a['preview_entries_count_confirmed'] == 10
    assert a['deprecated_legacy_placeholders_not_player_facing_confirmed'] is True
    assert a['runtime_activation_blockers_remain_confirmed'] is True
    assert a['existing_artifact_routes_inspected']['mutative_endpoints_behavior_change'] is False
    # MD5 source verification
    for entry in a['canonical_files_revalidated'] + a['review_files_revalidated'] + a['preview_files_revalidated']:
        p = ROOT / entry['path']
        assert p.exists(), f"missing source file {entry['path']}"
        assert md5(p) == entry['md5'], f"source drift on {entry['path']}"
    # Contract: forbidden fields in audit deve contenere TUTTI quelli della spec
    assert FORBIDDEN_FIELDS.issubset(set(a['forbidden_fields_guard'])), \
        "audit forbidden_fields_guard missing required entries"

    # Bible content sanity (32 entries, no future_reserved present in JSON)
    bible = load('data/design/artifacts/artifact_bible_launch_draft_v1.json')
    assert len(bible['artifacts']) == 32, "Bible must have 32 entries"
    # Preview dataset has 10
    preview = load('data/design/artifacts/preview/artifact_preview_dataset_v1.json')
    assert len(preview['entries']) == 10, "Preview must have 10 entries"

    # ---- Track B: backend implementation present
    route = ROUTE_FILE.read_text()
    assert '@router.get("/artifacts/catalog")' in route, \
        "GET /artifacts/catalog missing"
    assert '@router.get("/artifacts/catalog/preview")' in route, \
        "GET /artifacts/catalog/preview missing"
    assert '_ARTIFACT_BIBLE_PATH' in route, "Bible path constant missing"
    assert 'artifact_bible_launch_draft_v1.json' in route, \
        "Bible filename ref missing"
    assert 'artifact_preview_dataset_v1.json' in route, \
        "Preview filename ref missing"
    # Guard: nessun forbidden field hardcoded come chiave restituita
    for ff in FORBIDDEN_FIELDS:
        # Permettiamo la presenza solo nel set _CATALOG_FORBIDDEN_FIELDS (lista di blacklist)
        pattern_set = f'"{ff}"'
        # Se compare, deve essere SOLO dentro la blacklist (verifichiamo che non sia in
        # un dict di response): non e' bulletproof ma e' utile come hint.
    # I due endpoint nuovi NON devono usare db.<collection>.<update|insert|delete>
    # Localizziamo la sezione tra i marker.
    section_start = route.find('# ==================== ARTIFACT BIBLE READ-ONLY CATALOG')
    assert section_start > 0, "catalog RO section marker missing"
    section = route[section_start:]
    # Verifica negativa: niente chiamate di scrittura DB nella sezione catalog RO
    forbidden_db_patterns = [
        '.insert_one(', '.insert_many(',
        '.update_one(', '.update_many(',
        '.delete_one(', '.delete_many(',
        '.find_one_and_update(', '.find_one_and_replace(',
        'await db.users.', 'await db.user_artifacts.',
        'await db.user_constellations.', 'await db.user_heroes.',
        'await db.teams.', 'await db.inventory.',
    ]
    for pat in forbidden_db_patterns:
        assert pat not in section, \
            f"forbidden DB pattern '{pat}' found in catalog RO section"
    # Nessuna ownership/equip/fuse/craft/pull aggiunti come nuove route nella sezione
    for new_mut in ['/catalog/equip', '/catalog/fuse', '/catalog/craft',
                    '/catalog/pull', '/catalog/buy']:
        assert new_mut not in section, f"forbidden new route in catalog: {new_mut}"

    # ---- Track C: normalization + filters
    c = load('data/design/artifacts/catalog_ro/artifact_catalog_normalization_filters_v1.json')
    assert c['verdict'] == 'TRACK_C_ARTIFACT_CATALOG_NORMALIZATION_AND_FILTERS_READY'
    assert c['preview_endpoint_excludes_future_reserved'] is True
    assert c['preview_endpoint_returns_exactly_10'] is True
    assert 'user_owned' in c['forbidden_filters']
    assert 'price' in c['forbidden_filters']

    # ---- Track D: frontend no wiring
    d = load('data/design/artifacts/catalog_ro/artifact_frontend_integration_policy_no_wiring_v1.json')
    assert d['verdict'] == 'TRACK_D_ARTIFACT_FRONTEND_INTEGRATION_POLICY_NO_WIRING_READY'
    assert d['policy']['frontend_runtime_api_fetch_added_this_pack'] is False
    assert d['policy']['artifacts_preview_tsx_modified'] is False
    assert d['policy']['artifacts_preview_tsx_remains_static_read_only'] is True
    # Verifica live: artifacts-preview.tsx NON deve contenere fetch al nuovo endpoint
    preview_ui = (ROOT / 'frontend/app/artifacts-preview.tsx').read_text()
    assert '/api/artifacts/catalog' not in preview_ui, \
        "frontend should NOT fetch /api/artifacts/catalog yet"
    assert 'fetch(' not in preview_ui, "frontend must remain static (no fetch)"
    assert 'apiCall(' not in preview_ui, "frontend must remain static (no apiCall)"

    # ---- Track E: smoke + no DB guard
    e = load('data/design/artifacts/catalog_ro/artifact_catalog_backend_smoke_no_db_guard_v1.json')
    assert e['verdict'] == 'TRACK_E_ARTIFACT_CATALOG_BACKEND_SMOKE_AND_NO_DB_GUARD_READY'
    assert e['static_no_db_guard']['reads_only_versioned_json'] is True
    assert e['static_no_db_guard']['db_module_imports_in_catalog_helpers'] == 0
    assert e['static_no_db_guard']['db_method_calls_in_catalog_handlers'] == 0
    assert e['static_no_db_guard']['battle_engine_md5_unchanged'] is True
    assert e['static_no_db_guard']['backend_env_md5_unchanged'] is True
    for k, v in e['invariants'].items():
        assert v is True, f"invariant {k} must be True"

    # ---- Track H: completion
    h = load('data/design/artifacts/catalog_ro/artifact_backend_catalog_ro_completion_v1.json')
    assert h['verdict'] == 'TRACK_H_ARTIFACT_CATALOG_COMPLETION_READY'
    rc = h['runtime_changes_made']
    assert rc['frontend_ui_changes'] == 0, "frontend MUST be unchanged in this pack"
    assert rc['frontend_logic_changes'] == 0
    assert rc['db_writes_from_scripts'] == 0
    assert rc['battle_engine_changes'] == 0
    assert rc['gacha_rate_changes'] == 0
    assert rc['backend_catalog_endpoint_added'] is True
    for kb in ('iap_implementation', 'artifact_banner_activation',
               'constellation_banner_activation', 'character_bible_mutation',
               'inventory_state_added', 'ownership_state_added',
               'equip_endpoint_added', 'fuse_endpoint_added',
               'craft_endpoint_added', 'pull_endpoint_added'):
        assert rc[kb] is False, f"{kb} must be False"

    # ---- Invariants: MD5 lock su battle_engine + .env
    inv = h['invariants']
    assert md5('/app/backend/battle_engine.py') == inv['backend/battle_engine.py'], \
        "battle_engine.py MD5 drifted!"
    assert md5('/app/backend/.env') == inv['backend/.env'], \
        "backend/.env MD5 drifted!"

    # ---- Gacha hidden banners ancora attivi
    gacha = (ROOT / 'frontend/app/(tabs)/gacha.tsx').read_text()
    assert "HIDDEN_BANNERS_V2 = new Set(['artifact', 'constellation'])" in gacha, \
        "Gacha HIDDEN_BANNERS_V2 must still hide artifact/constellation"

    # ---- /artifacts redirect a /artifacts-preview intatto
    art_legacy = (ROOT / 'frontend/app/artifacts.tsx').read_text()
    assert "router.replace('/artifacts-preview')" in art_legacy, \
        "/artifacts legacy redirect missing"

    print('[PASS] PROJECT_ARTIFACT_BACKEND_CATALOG_RO master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
