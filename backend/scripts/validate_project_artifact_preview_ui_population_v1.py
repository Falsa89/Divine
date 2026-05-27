#!/usr/bin/env python3
"""
PROJECT_ARTIFACT_PREVIEW_UI_POPULATION master validator (read-only frontend).

Verifica end-to-end:
  - Track A: manifest revalidation con MD5 di tutti i source canonical + review
  - Track B: dataset 10 entries, niente future_reserved, niente legacy placeholder
  - Track C: UI artifacts-preview.tsx contiene il dataset e nessun forbidden token
  - Track D: lock guards intatti (HIDDEN_BANNERS_V2, redirect, no mutation)
  - Track E: smoke statici coperti
  - Track H: completion verdict + invarianti

Nessun DB write. Pure static.
"""
import json, sys, hashlib
from pathlib import Path

ROOT = Path('/app')
FORBIDDEN_LIVE_LABELS = ['EVOCA', 'EQUIPAGGIA', 'FONDI', 'CRAFT', 'ACQUISTA', 'OTTIENI ORA']
FUTURE_RESERVED_IDS = {
    'relic_occhio_solare', 'relic_emblema_asgard', 'relic_emblema_yamato',
    'relic_frammento_martello_tonante', 'relic_specchio_riflesso_perduto',
    'relic_pomo_giovinezza',
}
LEGACY_PLACEHOLDER_DISPLAY_NAMES = [
    'Santo Graal', 'Occhio di Ra', 'Frammento di Mjolnir',
    'Specchio di Yata', "Mela d'Oro di Idunn",
]

def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def load(rel): return json.loads((ROOT / rel).read_text())

def main():
    # ---- Track A
    a = load('data/design/artifacts/preview/artifact_preview_source_manifest_revalidation_v1.json')
    assert a['verdict'] == 'TRACK_A_ARTIFACT_PREVIEW_SOURCE_MANIFEST_REVALIDATION_READY'
    assert a['bible_entries_count_confirmed'] == 32
    assert a['preview_readiness_gate_confirmed'] == 'READY_TO_POPULATE_PREVIEW_IN_NEXT_PACK'
    # Verify MD5 on source files
    for entry in a['canonical_files_revalidated'] + a['review_files_revalidated']:
        p = ROOT / entry['path']
        assert p.exists(), f"missing source file {entry['path']}"
        assert md5(p) == entry['md5'], f"source drift on {entry['path']}"

    # ---- Track B
    b = load('data/design/artifacts/preview/artifact_preview_dataset_v1.json')
    assert b['verdict'] == 'TRACK_B_ARTIFACT_PREVIEW_DATASET_SELECTION_READY'
    assert b['entries_count'] == 10
    assert len(b['entries']) == 10
    ds_ids = {e['artifact_id'] for e in b['entries']}
    assert ds_ids.isdisjoint(FUTURE_RESERVED_IDS), \
        f"dataset contains future_reserved: {ds_ids & FUTURE_RESERVED_IDS}"
    assert b['no_future_reserved_in_dataset'] is True
    assert b['no_legacy_placeholder_names_in_dataset'] is True
    # Cross-check with canonical Bible
    bible = load('data/design/artifacts/artifact_bible_launch_draft_v1.json')
    bible_ids = {e['artifact_id'] for e in bible['artifacts']}
    assert ds_ids.issubset(bible_ids), f"dataset has unknown ids: {ds_ids - bible_ids}"

    # ---- Track C: live UI inspection
    ui = (ROOT / 'frontend/app/artifacts-preview.tsx').read_text()
    # Required strings
    for s in ('Reliquie Divine', 'Sistema in preparazione', 'ANTEPRIMA',
              'Non ottenibile ora'):
        assert s in ui, f"required UI string missing: {s!r}"
    # All 10 dataset ids appear in UI
    for e in b['entries']:
        assert e['artifact_id'] in ui, f"dataset id {e['artifact_id']} not in UI"
        assert e['display_name_it'] in ui, f"display name {e['display_name_it']!r} not in UI"
    # No future_reserved ids in UI
    for fr in FUTURE_RESERVED_IDS:
        assert fr not in ui, f"future_reserved id leaked into UI: {fr}"
    # No legacy placeholder display names
    for legacy in LEGACY_PLACEHOLDER_DISPLAY_NAMES:
        assert legacy not in ui, f"legacy placeholder leaked into UI: {legacy}"
    # No forbidden live labels
    for lbl in FORBIDDEN_LIVE_LABELS:
        assert lbl not in ui, f"forbidden live label in UI: {lbl}"
    # No mutation endpoints / API calls
    for bad in ('/api/artifacts/pull', '/api/artifacts/pull10', '/api/artifacts/fuse',
                '/api/artifacts/equip', '/api/constellations/equip',
                '/api/constellations/fuse', 'fetch(', 'apiCall('):
        assert bad not in ui, f"forbidden token in UI: {bad}"

    # ---- Track D: lock guards
    d = load('data/design/artifacts/preview/artifact_route_lock_guard_validation_v1.json')
    assert d['verdict'] == 'TRACK_D_ARTIFACT_ROUTE_AND_LOCK_GUARD_VALIDATION_READY'
    assert d['summary']['all_guards_ok'] is True
    assert d['summary']['backend_changes'] == 0
    assert d['summary']['db_writes'] == 0
    # Live re-check
    gacha = (ROOT / 'frontend/app/(tabs)/gacha.tsx').read_text()
    assert "HIDDEN_BANNERS_V2 = new Set(['artifact', 'constellation'])" in gacha
    assert "LOCKED_BANNERS_V2 = new Set(['premium', 'targeted'])" in gacha
    art_legacy = (ROOT / 'frontend/app/artifacts.tsx').read_text()
    assert "router.replace('/artifacts-preview')" in art_legacy

    # ---- Track E: smoke
    e = load('data/design/artifacts/preview/artifact_preview_beta_harness_smoke_v1.json')
    assert e['verdict'] == 'TRACK_E_ARTIFACT_PREVIEW_BETA_HARNESS_SMOKE_READY'

    # ---- Track H + invariants
    h = load('data/design/artifacts/preview/artifact_preview_ui_population_completion_v1.json')
    assert h['verdict'] == 'TRACK_H_ARTIFACT_PREVIEW_COMPLETION_READY'
    rc = h['runtime_changes_made']
    assert rc['frontend_ui_changes'] == 1  # only the preview UI populated
    for k in ('frontend_logic_changes', 'backend_route_changes', 'backend_logic_changes',
              'db_writes_from_scripts', 'battle_engine_changes', 'gacha_rate_changes'):
        assert rc[k] == 0, f"{k} must be 0"
    for kb in ('iap_implementation', 'artifact_banner_activation',
               'constellation_banner_activation', 'character_bible_mutation',
               'backend_catalog_endpoint_added', 'inventory_state_added'):
        assert rc[kb] is False, f"{kb} must be False"
    inv = h['invariants']
    assert md5('/app/backend/battle_engine.py') == inv['backend/battle_engine.py']
    assert md5('/app/backend/.env') == inv['backend/.env']

    print('[PASS] PROJECT_ARTIFACT_PREVIEW_UI_POPULATION master validator')
    return 0

if __name__ == '__main__':
    sys.exit(main())
