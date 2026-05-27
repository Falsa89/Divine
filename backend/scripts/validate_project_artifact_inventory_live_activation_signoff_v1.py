#!/usr/bin/env python3
"""
PROJECT_ARTIFACT_INVENTORY_LIVE_ACTIVATION_SIGNOFF master validator.

Pure static / no DB / no env injection:
  - Track A: previous stages revalidation (all 6 stages COMPLETE).
  - Track B: approval matrix 9 entries, all NOT_GRANTED.
  - Track C: canary scope + write budget defined; allowlist empty by default.
  - Track D: runbook + rollback; no apply executed.
  - Track E: post-apply lock policy.
  - Track F: suite registration proof marker JSON.
  - Track H: completion totals all zeros.
  - Invariants MD5 unchanged.
  - .env NOT modified (no live markers injected).
  - Legacy POST still locked 423.
  - Catalog GET still in routes file.
  - No new live endpoint introduced.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path('/app')
SIG_DIR = ROOT / 'data/design/artifacts/live_signoff'
ROUTE_FILE = ROOT / 'backend/routes/artifacts.py'

REQUIRED_FUTURE_MARKERS = {
    "PROJECT_ARTIFACT_INVENTORY_LIVE_APPROVAL",
    "ARTIFACT_INVENTORY_RUNTIME_ENABLED",
    "ARTIFACT_INVENTORY_CANARY_SCOPE_APPROVED",
    "ARTIFACT_INVENTORY_ROLLBACK_OWNER_APPROVED",
    "ARTIFACT_INVENTORY_QA_APPROVED",
}


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def load(rel):
    return json.loads((ROOT / rel).read_text())


def main():
    # ---- Track A
    a = load('data/design/artifacts/live_signoff/artifact_live_signoff_previous_stage_revalidation_v1.json')
    assert a['verdict'] == 'TRACK_A_ARTIFACT_LIVE_SIGNOFF_PREVIOUS_STAGE_REVALIDATION_READY'
    assert a['stage_chain_complete'] is True
    assert a['stage_6_complete_public_repo_verified'] is True
    assert a['unresolved_blockers'] == []
    assert a['signoff_pack_can_proceed'] is True
    # 7 stages
    assert len(a['stage_chain_status']) >= 7
    # All previous stages must be COMPLETE_PUBLIC_REPO_VERIFIED
    for s in a['stage_chain_status']:
        assert s['status'] == 'COMPLETE_PUBLIC_REPO_VERIFIED', \
            f"stage {s['stage']} not complete public: {s['status']}"
    # Safe-default runner state echoed
    rs = a['safe_default_runner_state']
    assert rs['default_mode_dry_run'] is True
    assert rs['refuses_apply_without_markers'] is True
    assert rs['refuses_apply_without_cli_flag'] is True
    # All 5 new collections must be NOT_PRESENT in DB state echo
    for c in ('artifact_catalog_snapshot', 'user_artifact_inventory',
              'artifact_inventory_ledger', 'artifact_collection_state',
              'artifact_idempotency_registry'):
        assert a['db_state'][c] == 'NOT_PRESENT'

    # ---- Track B: approval matrix
    b = load('data/design/artifacts/live_signoff/artifact_live_activation_approval_matrix_v1.json')
    assert b['verdict'] == 'TRACK_B_ARTIFACT_LIVE_ACTIVATION_APPROVAL_MATRIX_READY'
    assert b['matrix_design_only'] is True
    assert b['approvals_summary']['granted_in_this_pack'] == 0
    assert b['approvals_summary']['missing'] == b['approvals_summary']['total']
    assert b['approvals_summary']['total'] >= 9
    assert b['future_apply_blocked_until_all_granted'] is True
    # Each approval has required fields
    required_markers_in_matrix = set()
    for ap in b['approvals_required_for_future_live_apply']:
        assert 'id' in ap
        assert ap['status_in_this_pack'] == 'NOT_GRANTED'
        if 'required_marker' in ap and ap['required_marker'].startswith(('PROJECT_', 'ARTIFACT_')):
            # extract pure marker name
            key = ap['required_marker'].split('=')[0]
            required_markers_in_matrix.add(key)
    # All 5 required future markers referenced in matrix
    assert REQUIRED_FUTURE_MARKERS.issubset(required_markers_in_matrix), \
        f"matrix missing future markers: {REQUIRED_FUTURE_MARKERS - required_markers_in_matrix}"

    # ---- Track C: canary + budget
    c = load('data/design/artifacts/live_signoff/artifact_live_canary_scope_write_budget_v1.json')
    assert c['verdict'] == 'TRACK_C_ARTIFACT_LIVE_CANARY_SCOPE_AND_WRITE_BUDGET_READY'
    cs = c['canary_scope_definition']
    assert cs['scope_type'] == 'internal_only'
    assert cs['player_facing'] is False
    assert cs['allowlist_default'] == []
    assert cs['allowlist_required'] is True
    assert cs['allowlist_max_size_initial'] <= 5
    # Budgets reasonable + forbidden writes are zero
    wb = c['write_budget_first_apply']
    assert wb['users_collection_writes_allowed'] == 0
    assert wb['user_artifacts_legacy_writes_allowed'] == 0
    assert wb['user_constellations_legacy_writes_allowed'] == 0
    assert wb['teams_collection_writes_allowed'] == 0
    assert wb['abort_if_budget_exceeded'] is True
    # Allowed vs forbidden
    allowed = set(c['allowed_collections_first_apply'])
    forbidden = set(c['forbidden_collections_first_apply'])
    assert allowed.isdisjoint(forbidden)
    assert {'users', 'user_artifacts', 'user_constellations', 'teams'}.issubset(forbidden)
    assert {'artifact_catalog_snapshot', 'user_artifact_inventory',
            'artifact_inventory_ledger', 'artifact_collection_state',
            'artifact_idempotency_registry'}.issubset(allowed)
    fs = c['forbidden_scopes']
    assert all(fs[k] is True for k in (
        'broad_rollout', 'player_facing_ui', 'acquisition_source_player_initiated',
        'paid_flow', 'combat_bonus', 'gacha_banner_activation',
        'real_player_grant_outside_allowlist'))
    inv_w = c['write_pipeline_invariants']
    assert inv_w['idempotency_key_required'] is True
    assert inv_w['all_writes_logged_in_ledger'] is True

    # ---- Track D: runbook + rollback
    d = load('data/design/artifacts/live_signoff/artifact_live_apply_runbook_rollback_v1.json')
    assert d['verdict'] == 'TRACK_D_ARTIFACT_LIVE_APPLY_RUNBOOK_AND_ROLLBACK_READY'
    assert d['runbook_design_only'] is True
    assert d['no_apply_executed_in_this_pack'] is True
    assert d['apply_command']['this_pack_does_NOT_invoke'] is True
    # env_marker_verification contains all 5 markers
    env_strs = set(d['env_marker_verification_required'])
    for mk in REQUIRED_FUTURE_MARKERS:
        assert any(mk in s for s in env_strs), f"runbook missing marker {mk}"
    assert d['canary_user_verification']['allowlist_must_be_non_empty'] is True
    assert d['canary_user_verification']['allowlist_max_size'] <= 5
    # Rollback: never hard-delete after live
    assert 'NEVER db.<collection>.deleteMany' in str(d['rollback_runbook']['post_live_rollback_commands'])
    assert len(d['abort_criteria']) >= 5

    # ---- Track E: post-apply lock policy
    e = load('data/design/artifacts/live_signoff/artifact_runtime_locks_post_apply_policy_v1.json')
    assert e['verdict'] == 'TRACK_E_ARTIFACT_RUNTIME_LOCKS_POST_APPLY_POLICY_READY'
    locks = e['locks_that_remain_after_future_internal_apply']
    for k in ('gacha_artifact_banner_hidden', 'gacha_constellation_banner_hidden',
              'legacy_post_artifacts_pull_remains_423',
              'legacy_post_artifacts_fuse_remains_423',
              'legacy_post_constellations_equip_remains_423',
              'no_equip_endpoint_added', 'no_fuse_endpoint_added',
              'no_craft_endpoint_added', 'no_pull_endpoint_added',
              'no_combat_bonus_active', 'no_iap_flow_added',
              'no_public_inventory_route_unless_separate_endpoint_pack',
              'no_player_initiated_acquisition'):
        assert locks[k] is True, f"lock {k} must remain True"
    forbidden_actions = set(e['forbidden_after_apply_until_separate_pack'])
    assert any('unhide artifact banner' in f for f in forbidden_actions)
    assert any('combat bonus' in f for f in forbidden_actions)

    # ---- Track F: proof marker
    f = load('data/design/artifacts/live_signoff/artifact_live_signoff_suite_registration_proof_marker_v1.json')
    assert f['purpose'] == 'DEDICATED_SUITE_REGISTRATION_PROOF_MARKER'
    assert f['validator_file_role'] == 'OPTIONAL'
    assert f['weakens_REQUIRED_validators'] is False

    # ---- Track H: completion totals
    h = load('data/design/artifacts/live_signoff/artifact_live_signoff_completion_v1.json')
    assert h['verdict'] == 'TRACK_H_ARTIFACT_LIVE_SIGNOFF_COMPLETION_READY'
    assert h['global_verdict_local'] == 'PROJECT_ARTIFACT_INVENTORY_LIVE_ACTIVATION_SIGNOFF_READY_NOT_APPLIED'
    rc = h['runtime_changes_made']
    for k in ('frontend_ui_changes', 'frontend_logic_changes',
              'backend_route_changes', 'backend_logic_changes',
              'db_writes_from_scripts', 'db_collections_created_live',
              'battle_engine_changes', 'gacha_rate_changes',
              'hidden_banners_changes', 'env_live_markers_injected'):
        assert rc[k] == 0, f"runtime change {k} must be 0"
    for k in ('iap_implementation', 'artifact_banner_activation',
              'constellation_banner_activation', 'character_bible_mutation',
              'inventory_state_added_live', 'ownership_state_added_live',
              'new_endpoint_added_live', 'locked_endpoint_unlocked',
              'validator_required_weakened'):
        assert rc[k] is False, f"bool change {k} must be False"

    # ---- Invariants MD5 (live)
    inv = h['invariants']
    for rel, expected in inv.items():
        actual = md5(ROOT / rel)
        assert actual == expected, f"MD5 drift on {rel}: expected {expected}, got {actual}"

    # ---- .env was NOT modified (no live markers injected)
    env_md5 = md5(ROOT / 'backend/.env')
    assert env_md5 == 'ff60bbb79efa329b71aa8ed351ea89b3', \
        f"backend/.env MD5 drifted! Live markers may have been injected! got {env_md5}"
    # Also check process env: no marker should be present in this validator's run
    for mk in REQUIRED_FUTURE_MARKERS:
        assert mk not in os.environ or os.environ.get(mk) == '', \
            f"FORBIDDEN: live marker {mk} present in process env during signoff pack"

    # ---- Live runtime checks
    src = ROUTE_FILE.read_text()
    assert '@router.get("/artifacts/catalog")' in src
    assert '@router.get("/artifacts/catalog/preview")' in src
    assert 'ARTIFACT_MUTATION_LOCK_STATUS = 423' in src
    assert 'ARTIFACT_MUTATION_ENDPOINT_LOCKED' in src
    assert 'CONSTELLATION_MUTATION_ENDPOINT_LOCKED' in src
    # No new inventory live endpoint added
    assert '/artifacts/inventory' not in src

    # ---- Frontend untouched
    pre = (ROOT / 'frontend/app/artifacts-preview.tsx').read_text()
    assert '/api/artifacts/inventory' not in pre
    assert 'fetch(' not in pre

    print('[PASS] PROJECT_ARTIFACT_INVENTORY_LIVE_ACTIVATION_SIGNOFF master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
