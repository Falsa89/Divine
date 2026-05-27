#!/usr/bin/env python3
"""
PROJECT_ARTIFACT_INVENTORY_GATED_IMPORT master validator.

Static + runtime checks:
  - Track A: readiness audit JSON consistent.
  - Track B: source/target mapping uses canonical Bible only.
  - Track C: migration script safe-default (no DB at import, guards present).
  - Track D: apply_or_ready_not_applied = READY_NOT_APPLIED + 0 DB writes.
  - Track E: runtime/frontend guards rechecked; legacy POST still 423.
  - Invariants MD5 unchanged.
  - Live runner refuses apply without markers (exit 2) and without CLI flag (exit 3).
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path('/app')
GATED_DIR = ROOT / 'data/design/artifacts/gated_import'
ROUTE_FILE = ROOT / 'backend/routes/artifacts.py'
RUNNER = ROOT / 'backend/scripts/artifact_inventory_gated_import_apply.py'


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def load(rel):
    return json.loads((ROOT / rel).read_text())


def main():
    # ---- Track A
    a = load('data/design/artifacts/gated_import/artifact_gated_import_readiness_audit_v1.json')
    assert a['verdict'] == 'TRACK_A_ARTIFACT_GATED_IMPORT_READINESS_AUDIT_READY'
    assert a['apply_decision'] == 'READY_NOT_APPLIED'
    assert a['live_markers_observed_in_env']['PROJECT_ARTIFACT_INVENTORY_LIVE_APPROVAL'] == 'ABSENT'
    assert a['live_markers_observed_in_env']['ARTIFACT_INVENTORY_RUNTIME_ENABLED'] == 'ABSENT'
    assert a['prior_stages_state']['stage_5_schema_dry_run']['status'] == 'COMPLETE'
    assert a['prior_stages_state']['stage_4_5_hardening']['locked_post_endpoints_count'] == 7
    for col, state in a['db_collections_state'].items():
        assert state == 'NOT_PRESENT', f"collection {col} should NOT be present"
    # Legacy GET not used as source
    forbidden = set(a['legacy_get_endpoints_must_NOT_be_used_as_import_source'])
    assert {"GET /api/artifacts", "GET /api/constellations", "GET /api/banners/special"}.issubset(forbidden)

    # ---- Track B
    b = load('data/design/artifacts/gated_import/artifact_import_source_target_mapping_v1.json')
    assert b['verdict'] == 'TRACK_B_ARTIFACT_IMPORT_SOURCE_TARGET_MAPPING_READY'
    assert b['source_strategy'].startswith('canonical_design_files_only')
    src_paths = {s['path'] for s in b['sources']}
    assert any('artifact_bible_launch_draft_v1.json' in p for p in src_paths)
    # Forbidden sources include user_artifacts legacy
    forb = b['explicitly_forbidden_sources']
    assert any(x.get('collection') == 'user_artifacts' for x in forb)
    assert any(x.get('endpoint') == 'GET /api/artifacts' for x in forb)
    # 5 targets, all gated
    target_collections = {t['collection'] for t in b['targets']}
    assert {'artifact_catalog_snapshot', 'user_artifact_inventory',
            'artifact_inventory_ledger', 'artifact_collection_state',
            'artifact_idempotency_registry'}.issubset(target_collections)
    for t in b['targets']:
        assert t['created_only_with_live_markers'] is True
    assert b['canary_internal_only_scope']['max_canary_grants_per_run'] == 0
    assert b['rollback_revoke_reference']['never_hard_delete_after_live'] is True

    # ---- Track C
    c = load('data/design/artifacts/gated_import/artifact_migration_script_safe_default_v1.json')
    assert c['verdict'] == 'TRACK_C_ARTIFACT_MIGRATION_SCRIPT_OR_PLAN_SAFE_DEFAULT_READY'
    assert c['script_default_mode'] == 'dry_run'
    assert c['script_refuses_apply_if_any_flag_missing'] is True
    assert c['script_registered_in_server_startup'] is False
    assert c['script_registered_in_supervisord'] is False
    assert c['script_registered_in_cron'] is False
    for k, v in c['safe_defaults_summary'].items():
        assert v is True, f"safe default {k} must be True"
    # Static analysis: script must NOT import motor at module top-level
    runner_src = RUNNER.read_text()
    # Take the first 25 lines (header/import block)
    head = '\n'.join(runner_src.splitlines()[:30])
    assert 'import motor' not in head and 'from motor' not in head, \
        "runner must not import motor at top-level (no DB at import time)"
    # Apply path must be gated by both env markers AND CLI flag
    assert 'PROJECT_ARTIFACT_INVENTORY_LIVE_APPROVAL' in runner_src
    assert 'ARTIFACT_INVENTORY_RUNTIME_ENABLED' in runner_src
    assert '--i-understand-this-will-write' in runner_src

    # ---- Track D: ready_not_applied
    d = load('data/design/artifacts/gated_import/artifact_gated_import_apply_or_ready_not_applied_v1.json')
    assert d['verdict'] == 'TRACK_D_ARTIFACT_GATED_IMPORT_READY_NOT_APPLIED_MISSING_LIVE_MARKERS'
    assert d['execution_path_taken'] == 'READY_NOT_APPLIED'
    assert d['live_markers_present'] is False
    for k in ('db_writes_performed', 'collections_created', 'indexes_created',
              'grants_emitted', 'revokes_emitted', 'users_touched',
              'endpoints_added_live', 'frontend_changes',
              'battle_engine_changes', 'gacha_changes', 'iap_changes',
              'character_bible_mutations'):
        assert d[k] == 0, f"{k} must be 0"
    assert d['attempted_apply_without_markers_result']['exit_code'] == 2
    assert d['attempted_apply_without_markers_result']['db_writes_performed_during_attempt'] == 0

    # ---- Track E: runtime guards
    e = load('data/design/artifacts/gated_import/artifact_gated_import_runtime_frontend_guard_v1.json')
    assert e['verdict'] == 'TRACK_E_ARTIFACT_GATED_IMPORT_RUNTIME_AND_FRONTEND_GUARD_READY'
    assert e['runtime_recheck']['GET_artifacts_catalog_count'] == 32
    assert e['runtime_recheck']['GET_artifacts_catalog_preview_count'] == 10
    assert e['runtime_recheck']['locked_post_endpoints_all_return_423'] is True
    assert e['runtime_recheck']['new_inventory_endpoints_added_this_pack'] == 0
    assert e['frontend_recheck']['artifacts_preview_tsx_modified'] is False
    assert e['frontend_recheck']['gacha_hidden_banners_v2_contains_artifact_and_constellation'] is True
    for k, v in e['systems_not_touched'].items():
        assert v is True, f"system_not_touched.{k} must be True"
    # live MD5 check
    for rel, expected in e['invariants_md5'].items():
        actual = md5(ROOT / rel)
        assert actual == expected, f"MD5 drift on {rel}: expected {expected}, got {actual}"

    # ---- Track H: completion
    h = load('data/design/artifacts/gated_import/artifact_gated_import_completion_v1.json')
    assert h['verdict'] == 'TRACK_H_ARTIFACT_GATED_IMPORT_COMPLETION_READY'
    assert h['global_verdict_local'] == 'PROJECT_ARTIFACT_INVENTORY_GATED_IMPORT_READY_NOT_APPLIED_MISSING_LIVE_MARKERS'
    rc = h['runtime_changes_made']
    for k in ('frontend_ui_changes', 'frontend_logic_changes',
              'backend_route_changes', 'backend_logic_changes',
              'db_writes_from_scripts', 'db_collections_created_live',
              'battle_engine_changes', 'gacha_rate_changes',
              'hidden_banners_changes'):
        assert rc[k] == 0, f"completion runtime change {k} must be 0"
    for k in ('iap_implementation', 'artifact_banner_activation',
              'constellation_banner_activation', 'character_bible_mutation',
              'inventory_state_added_live', 'ownership_state_added_live',
              'new_endpoint_added_live', 'locked_endpoint_unlocked',
              'validator_required_weakened'):
        assert rc[k] is False, f"completion bool change {k} must be False"

    # ---- Live runtime checks
    src = ROUTE_FILE.read_text()
    assert '@router.get("/artifacts/catalog")' in src
    assert '@router.get("/artifacts/catalog/preview")' in src
    # No new inventory endpoint added
    assert '/artifacts/inventory' not in src
    # Legacy POST locked markers preserved
    assert 'ARTIFACT_MUTATION_LOCK_STATUS = 423' in src
    assert 'ARTIFACT_MUTATION_ENDPOINT_LOCKED' in src
    assert 'CONSTELLATION_MUTATION_ENDPOINT_LOCKED' in src

    # ---- Frontend untouched
    pre = (ROOT / 'frontend/app/artifacts-preview.tsx').read_text()
    assert '/api/artifacts/inventory' not in pre
    assert 'fetch(' not in pre

    # ---- Live behavior of the runner: invoke dry-run and apply-without-markers
    res_dry = subprocess.run(
        [sys.executable, str(RUNNER)],
        capture_output=True, text=True, timeout=30,
    )
    assert res_dry.returncode == 0, f"dry-run exit code {res_dry.returncode}"
    out_dry = json.loads(res_dry.stdout)
    assert out_dry['mode'] == 'dry_run'
    assert out_dry['verdict'] == 'READY_NOT_APPLIED_MISSING_LIVE_MARKERS'
    assert out_dry['db_writes_performed'] == 0
    assert out_dry['catalog_snapshot_rows_that_would_be_inserted'] == 32

    res_refuse = subprocess.run(
        [sys.executable, str(RUNNER), '--apply', '--i-understand-this-will-write'],
        capture_output=True, text=True, timeout=30,
    )
    assert res_refuse.returncode == 2, f"refusal exit code expected 2 got {res_refuse.returncode}"
    out_refuse = json.loads(res_refuse.stdout)
    assert out_refuse['mode'] == 'refused'
    assert out_refuse['db_writes_performed'] == 0

    print('[PASS] PROJECT_ARTIFACT_INVENTORY_GATED_IMPORT master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
