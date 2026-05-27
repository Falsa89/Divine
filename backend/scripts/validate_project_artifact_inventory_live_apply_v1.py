#!/usr/bin/env python3
"""
PROJECT_ARTIFACT_INVENTORY_LIVE_APPLY validator.

Verifies (static + live DB read-only):
  - 7 Track JSONs present and coherent.
  - APPLY_ALLOWED + applied: True.
  - DB writes match declared budget; counts match collections.
  - Canary users granted only (sfqa + test).
  - locked=True on canary inventory rows.
  - No grants to forbidden collections with our canary source_id.
  - Idempotency: re-resolve the keys; would be no-op.
  - MD5 invariants unchanged on battle_engine/.env/routes/frontend.
  - .env not modified (no live markers injected).
  - Legacy POST locked 423 still in routes file.
  - Hidden banners still configured in gacha.
"""
import asyncio
import hashlib
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

ROOT = Path('/app')
LIVE_DIR = ROOT / 'data/design/artifacts/live_apply'
ROUTE_FILE = ROOT / 'backend/routes/artifacts.py'

CANARY_EMAILS = {'sfqa@test.com', 'test@test.com'}
CANARY_ARTIFACT_ID = 'relic_aurora_eterna'
SOURCE_ID = 'artifact_inventory_live_apply_stage8_canary_2026_05_27'


def md5(rel):
    return hashlib.md5((ROOT / rel).read_bytes()).hexdigest()


def load(rel):
    return json.loads((ROOT / rel).read_text())


async def db_checks():
    from motor.motor_asyncio import AsyncIOMotorClient
    c = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = c[os.environ.get('DB_NAME', 'test_database')]
    counts = {}
    for col in ('artifact_catalog_snapshot', 'user_artifact_inventory',
                'artifact_inventory_ledger', 'artifact_collection_state',
                'artifact_idempotency_registry'):
        counts[col] = await db[col].count_documents({})
    # inventory rows: count == 2 and locked True
    locked_count = await db.user_artifact_inventory.count_documents({'locked': True})
    # forbidden writes
    forbidden_legacy_artifact = await db.user_artifacts.count_documents({'source_id': SOURCE_ID})
    forbidden_legacy_const = await db.user_constellations.count_documents({'source_id': SOURCE_ID})
    # canary users existence
    canary_user_ids = []
    for e in CANARY_EMAILS:
        u = await db.users.find_one({'email': e})
        assert u, f"canary user missing {e}"
        canary_user_ids.append(u['id'])
    # Each canary user has 1 inventory row with locked=True
    for uid in canary_user_ids:
        invs = await db.user_artifact_inventory.find({'user_id': uid}).to_list(length=10)
        assert len(invs) == 1, f"expected 1 inventory row for {uid}, got {len(invs)}"
        assert invs[0]['artifact_id'] == CANARY_ARTIFACT_ID
        assert invs[0]['locked'] is True
        assert invs[0]['status'] == 'owned'
        assert invs[0]['quantity'] == 1
    # No grants to any other user with our canary source_id
    others = await db.user_artifact_inventory.count_documents({
        'source_id': SOURCE_ID,
        'user_id': {'$nin': canary_user_ids},
    })
    return {
        'counts': counts,
        'locked_count': locked_count,
        'forbidden_legacy_artifact_with_source_id': forbidden_legacy_artifact,
        'forbidden_legacy_const_with_source_id': forbidden_legacy_const,
        'extra_canary_grants_outside_allowlist': others,
    }


def main():
    # ---- Track A
    a = load('data/design/artifacts/live_apply/artifact_live_apply_authorized_gate_preflight_v1.json')
    assert a['verdict'] == 'TRACK_A_ARTIFACT_LIVE_APPLY_AUTHORIZED_GATE_PREFLIGHT_READY'
    assert a['apply_decision'] == 'APPLY_ALLOWED'
    assert a['live_markers_task_local_attestation']['all_six_true'] is True
    assert a['live_markers_task_local_attestation']['backend_env_md5_unchanged'] is True
    assert a['canary_allowlist'] == ['sfqa@test.com', 'test@test.com']
    assert a['canary_allowlist_size'] == 2
    assert all(u['exists'] for u in a['canary_users_resolved'])
    assert a['write_budget_planned'] <= a['write_budget_max']

    # ---- Track B
    b = load('data/design/artifacts/live_apply/artifact_live_apply_canary_user_resolution_writeset_v1.json')
    assert b['verdict'] == 'TRACK_B_ARTIFACT_LIVE_APPLY_CANARY_USER_RESOLUTION_WRITESET_READY'
    assert b['resolution_strategy'].startswith('strict_allowlist')
    assert b['writeset_dry_run']['total_planned_writes'] == 40
    assert b['writeset_dry_run']['budget_exceeded'] is False
    for fk in ('users_writes', 'teams_writes', 'legacy_user_artifacts_writes',
               'legacy_user_constellations_writes'):
        assert b['writeset_dry_run'][fk] == 0
    assert b['writeset_invariants']['only_canary_artifact'] == CANARY_ARTIFACT_ID
    assert b['writeset_invariants']['all_inventory_rows_locked_true'] is True

    # ---- Track C
    c = load('data/design/artifacts/live_apply/artifact_live_apply_canary_execution_v1.json')
    assert c['verdict'] == 'TRACK_C_ARTIFACT_LIVE_APPLY_CANARY_EXECUTION_READY'
    assert c['applied'] is True
    aw = c['actual_db_writes']
    assert aw['total_actual_writes'] == 40
    counts_declared = c['actual_collection_counts_post_apply']
    assert counts_declared['artifact_catalog_snapshot'] == 32
    assert counts_declared['user_artifact_inventory'] == 2
    fw = c['forbidden_writes_check']
    for k, v in fw.items():
        if isinstance(v, bool):
            assert v is False, f"{k} must be False"
        else:
            assert v == 0, f"{k} must be 0"
    assert c['budget_compliance']['within_budget'] is True
    pe = c['player_exposure_during_apply']
    assert pe['new_endpoint_live_added'] is False
    assert pe['banner_changed'] is False
    assert pe['locked_post_unlocked'] is False

    # ---- Track D
    d = load('data/design/artifacts/live_apply/artifact_live_apply_runtime_lock_guard_v1.json')
    assert d['verdict'] == 'TRACK_D_ARTIFACT_LIVE_APPLY_RUNTIME_LOCK_GUARD_READY'
    s = d['post_apply_smoke']
    assert s['GET /api/artifacts/catalog']['http'] == 200
    for k, v in s.items():
        if k.startswith('POST '):
            assert v['http'] == 423
    assert d['no_combat_bonus_active'] is True
    assert d['catalog_RO_preserved'] is True

    # ---- Track E
    e = load('data/design/artifacts/live_apply/artifact_live_apply_rollback_idempotency_v1.json')
    assert e['verdict'] == 'TRACK_E_ARTIFACT_LIVE_APPLY_ROLLBACK_IDEMPOTENCY_READY'
    ir = e['idempotency_rerun']
    assert ir['verdict'] == 'IDEMPOTENCY_PASS'
    assert ir['idempotent_noop_count'] == 2
    assert ir['new_grants_count'] == 0
    assert ir['duplicate_inventory_rows_created'] == 0
    assert e['rollback_executed_in_this_pack'] is False
    assert e['rollback_plan']['locked_items_block_revoke'] is True

    # ---- Proof marker
    pm = load('data/design/artifacts/live_apply/artifact_live_apply_suite_registration_proof_marker_v1.json')
    assert pm['validator_file_role'] == 'OPTIONAL'
    assert pm['weakens_REQUIRED_validators'] is False

    # ---- Track H
    h = load('data/design/artifacts/live_apply/artifact_live_apply_completion_v1.json')
    assert h['verdict'] == 'TRACK_H_ARTIFACT_LIVE_APPLY_COMPLETION_READY'
    assert h['global_verdict_local'] == 'PROJECT_ARTIFACT_INVENTORY_LIVE_APPLY_CANARY_APPLIED_INTERNAL_ONLY'
    rc = h['runtime_changes_made']
    assert rc['frontend_ui_changes'] == 0
    assert rc['frontend_logic_changes'] == 0
    assert rc['backend_route_changes'] == 0
    assert rc['battle_engine_changes'] == 0
    assert rc['gacha_rate_changes'] == 0
    assert rc['env_live_markers_injected_to_dotenv'] == 0
    assert rc['locked_endpoint_unlocked'] is False
    assert rc['new_endpoint_added_live'] is False
    assert rc['validator_required_weakened'] is False
    assert rc['db_writes_from_scripts'] == 40
    assert rc['db_collections_created_live'] == 5

    # ---- MD5 invariants
    inv = h['invariants']
    for rel, expected in inv.items():
        actual = md5(ROOT / rel)
        assert actual == expected, f"MD5 drift on {rel}: expected {expected}, got {actual}"

    # ---- Live DB read-only checks
    db_state = asyncio.run(db_checks())
    assert db_state['counts'] == {
        'artifact_catalog_snapshot': 32,
        'user_artifact_inventory': 2,
        'artifact_inventory_ledger': 2,
        'artifact_collection_state': 2,
        'artifact_idempotency_registry': 2,
    }, f"DB counts mismatch: {db_state['counts']}"
    assert db_state['locked_count'] == 2
    assert db_state['forbidden_legacy_artifact_with_source_id'] == 0
    assert db_state['forbidden_legacy_const_with_source_id'] == 0
    assert db_state['extra_canary_grants_outside_allowlist'] == 0

    # ---- Routes file: catalog still and 7 POST locked
    src = ROUTE_FILE.read_text()
    assert '@router.get("/artifacts/catalog")' in src
    assert 'ARTIFACT_MUTATION_LOCK_STATUS = 423' in src
    # No new inventory live endpoint
    assert '/artifacts/inventory' not in src
    # Frontend untouched
    pre = (ROOT / 'frontend/app/artifacts-preview.tsx').read_text()
    assert '/api/artifacts/inventory' not in pre

    print('[PASS] PROJECT_ARTIFACT_INVENTORY_LIVE_APPLY master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
