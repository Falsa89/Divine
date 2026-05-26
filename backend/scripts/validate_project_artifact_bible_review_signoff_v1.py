#!/usr/bin/env python3
"""
PROJECT_ARTIFACT_BIBLE_REVIEW_SIGNOFF master validator (design-review only).

Verifica end-to-end:
  - Track A: full manifest review include tutti i 10 file source con md5/bytes
  - Track B: entry-by-entry copre tutte le 32 reliquie (approved + future_reserved = 32)
  - Track C: 8 decisioni di reconciliation, nessuna esposizione player-facing dei legacy placeholders
  - Track D: 5 sistemi signed, ambiguous entries risolte
  - Track E: gate decision READY, esempi safe identificati
  - Track F: blocker matrix con almeno 15 blockers
  - Track G: validator base ri-eseguito green; review validator registrato
  - Track I: completion con design_only_mode e runtime_changes = 0
  - Invarianti battle_engine.py / .env

NESSUN DB WRITE. PURE STATIC.
"""
import json, sys, hashlib
from pathlib import Path

ROOT = Path('/app')

def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def load(rel): return json.loads((ROOT / rel).read_text())

def main():
    # ---- Track A
    a = load('data/design/artifacts/review/artifact_bible_full_manifest_review_v1.json')
    assert a['verdict'] == 'TRACK_A_ARTIFACT_BIBLE_FULL_MANIFEST_REVIEW_READY'
    assert len(a['manifest']) == 10, f"manifest should cover 10 files, has {len(a['manifest'])}"
    assert a['all_files_present'] is True
    assert a['all_files_non_empty'] is True
    # Verify each source file still exists and md5 matches
    for entry in a['manifest']:
        p = ROOT / entry['path']
        assert p.exists(), f"manifest references missing file: {entry['path']}"
        assert md5(p) == entry['md5'], f"manifest md5 drift on {entry['path']}"

    # ---- Track B
    b = load('data/design/artifacts/review/artifact_entry_by_entry_canonical_review_v1.json')
    assert b['verdict'] == 'TRACK_B_ARTIFACT_ENTRY_BY_ENTRY_CANONICAL_REVIEW_READY'
    assert b['entries_total'] == 32
    assert b['reviewed_entries'] == 32
    approved_n = len(b['approved_entries'])
    fr_n = len(b['future_reserved_entries'])
    assert approved_n + fr_n == 32, f"approved({approved_n}) + future_reserved({fr_n}) != 32"
    assert b['signoff_decision'] == 'APPROVED_FOR_PREVIEW_POPULATION_GATE'
    # Cross-check IDs with the Bible
    bible = load('data/design/artifacts/artifact_bible_launch_draft_v1.json')
    bible_ids = {e['artifact_id'] for e in bible['artifacts']}
    review_ids = set(b['approved_entries']) | {e['id'] for e in b['future_reserved_entries']}
    assert review_ids.issubset(bible_ids), f"review references unknown ids: {review_ids - bible_ids}"

    # ---- Track C: legacy placeholder reconciliation
    c = load('data/design/artifacts/review/artifact_placeholder_legacy_reconciliation_v1.json')
    assert c['verdict'] == 'TRACK_C_PLACEHOLDER_AND_LEGACY_NAME_RECONCILIATION_READY'
    assert c['player_facing_exposure_to_legacy_placeholders'] is False
    assert c['db_writes_in_track_c'] == 0
    must_address = {'holy_grail', 'eye_of_ra', 'mjolnir_frag', 'yata_mirror',
                    'golden_apple', 'aegis_shard'}
    addressed_ids = {d.get('legacy_placeholder_id') for d in c['decisions']
                     if d.get('legacy_placeholder_id')}
    assert must_address.issubset(addressed_ids), f"missing legacy decisions: {must_address - addressed_ids}"
    # Anche exclusive + economy
    concepts = {d.get('legacy_concept') for d in c['decisions'] if d.get('legacy_concept')}
    assert 'old_exclusive_items_route' in concepts
    assert 'economy_artifact_like_material' in concepts

    # ---- Track D: boundary signoff
    d = load('data/design/artifacts/review/artifact_system_boundary_signoff_v1.json')
    assert d['verdict'] == 'TRACK_D_SYSTEM_BOUNDARY_SIGNOFF_READY'
    assert d['five_systems_orthogonal'] is True
    funcs = d['any_artifact_functioning_as']
    for k in ('equipment_gear', 'hero_exclusive_weapon', 'rune_socket',
              'constellation_dupe_material', 'live_combat_buff'):
        assert funcs[k] is False, f"boundary violation: {k}"

    # ---- Track E: preview gate
    e = load('data/design/artifacts/review/artifact_preview_population_readiness_gate_v1.json')
    assert e['verdict'] == 'TRACK_E_PREVIEW_POPULATION_READINESS_GATE_READY'
    assert e['gate_decision'] == 'READY_TO_POPULATE_PREVIEW_IN_NEXT_PACK'
    assert e['ui_population_NOT_executed_in_this_pack'] is True
    assert e['db_writes_in_track_e'] == 0
    n_safe = len(e['recommended_preview_set_examples_safe'])
    assert 6 <= n_safe <= 12, f"preview examples must be 6-12, got {n_safe}"

    # ---- Track F: blocker matrix
    f = load('data/design/artifacts/review/artifact_import_runtime_blocker_matrix_v1.json')
    assert f['verdict'] == 'TRACK_F_IMPORT_AND_RUNTIME_BLOCKER_MATRIX_READY'
    assert len(f['blockers']) >= 15
    assert f['runtime_activation_allowed_now'] is False

    # ---- Track G
    g = load('data/design/artifacts/review/artifact_static_guard_validation_update_v1.json')
    assert g['verdict'] == 'TRACK_G_STATIC_GUARD_VALIDATION_AND_UPDATE_READY'
    audit = g['live_static_audit_summary']
    for k in ('hidden_banners_v2_contains_artifact', 'hidden_banners_v2_contains_constellation',
              'artifacts_route_redirect_only', 'artifacts_preview_no_mutation_endpoint',
              'no_combat_wiring_to_artifacts', 'no_combat_wiring_to_constellations',
              'flag_ARTIFACT_LIVE_BONUS_ENABLED_off'):
        assert audit[k] is True, f"static audit failed on {k}"

    # ---- Track I + invariants
    i = load('data/design/artifacts/review/artifact_review_signoff_completion_v1.json')
    assert i['verdict'] == 'TRACK_I_ARTIFACT_REVIEW_COMPLETION_READY'
    assert i['global_verdict_local_container'] == 'PROJECT_ARTIFACT_BIBLE_REVIEW_SIGNOFF_READY'
    rc = i['runtime_changes_made']
    for k in ('frontend_route_changes', 'frontend_logic_changes', 'backend_route_changes',
              'backend_logic_changes', 'db_writes_from_scripts', 'battle_engine_changes',
              'gacha_rate_changes'):
        assert rc[k] == 0
    for kb in ('iap_implementation', 'artifact_banner_activation',
               'constellation_banner_activation', 'character_bible_mutation'):
        assert rc[kb] is False
    inv = i['invariants']
    assert md5('/app/backend/battle_engine.py') == inv['backend/battle_engine.py']
    assert md5('/app/backend/.env') == inv['backend/.env']

    # ---- Live static guards (re-verify on filesystem)
    gacha = (ROOT / 'frontend/app/(tabs)/gacha.tsx').read_text()
    assert "HIDDEN_BANNERS_V2 = new Set(['artifact', 'constellation'])" in gacha
    art = (ROOT / 'frontend/app/artifacts.tsx').read_text()
    assert "router.replace('/artifacts-preview')" in art
    prev = (ROOT / 'frontend/app/artifacts-preview.tsx').read_text()
    for bad in ('/api/artifacts/pull', '/api/artifacts/fuse', '/api/artifacts/equip',
                '/api/constellations/equip', '/api/constellations/fuse'):
        assert bad not in prev, f'forbidden endpoint in preview: {bad}'

    print('[PASS] PROJECT_ARTIFACT_BIBLE_REVIEW_SIGNOFF master validator')
    return 0

if __name__ == '__main__':
    sys.exit(main())
