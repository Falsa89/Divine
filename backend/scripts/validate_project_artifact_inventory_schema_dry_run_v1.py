#!/usr/bin/env python3
"""
PROJECT_ARTIFACT_INVENTORY_SCHEMA_DRY_RUN master validator.

Pure static + in-memory schema validation:
  - Track A: source manifest + legacy GET audit JSON present.
  - Track B: schema design defines 5 collections with required fields and indexes.
  - Track C: sample documents validate against schema, NO forbidden fields,
             idempotency key pattern correct, locked-revoke blocked scenario.
  - Track D: future API contracts marked design_only, no live impl.
  - Track E: migration/rollback plan defines stages without DB write.
  - Invarianti: MD5 lock su battle_engine.py / backend/.env / frontend.
  - Catalog GET preservati nel modulo routes.
  - 7 POST mutativi legacy restano lockati 423.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
DRY_RUN_DIR = ROOT / 'data/design/artifacts/inventory_schema_dry_run'
ROUTE_FILE = ROOT / 'backend/routes/artifacts.py'

FORBIDDEN_INVENTORY_FIELDS = {
    "level", "stars_upgrade_progress", "equipped", "equip_slot",
    "stat_bonus_active", "combat_modifier", "craft_cost", "fuse_cost",
    "price", "purchase_url", "pity_count", "hero_stat_delta", "pvp_power",
    "gacha_pity_counter",
}

REQUIRED_COLLECTIONS = {
    "artifact_catalog_snapshot",
    "user_artifact_inventory",
    "artifact_inventory_ledger",
    "artifact_collection_state",
    "artifact_idempotency_registry",
}


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def load(rel):
    return json.loads((ROOT / rel).read_text())


def main():
    # ---- Track A: source + legacy GET audit
    a = load('data/design/artifacts/inventory_schema_dry_run/artifact_inventory_source_legacy_get_audit_v1.json')
    assert a['verdict'] == 'TRACK_A_ARTIFACT_INVENTORY_SOURCE_AND_LEGACY_GET_AUDIT_READY'
    # MD5 di artifact_bible verificato
    bible_entry = next(x for x in a['sources_reread']['canonical'] if 'launch_draft_v1.json' in x['path'])
    assert md5(ROOT / bible_entry['path']) == bible_entry['md5'], "Bible MD5 drift"
    # GET legacy auditati: artifacts/constellations/banners/special
    audited_eps = {x['endpoint'] for x in a['legacy_get_endpoints_audit']}
    assert {"GET /api/artifacts", "GET /api/constellations", "GET /api/banners/special"}.issubset(audited_eps)
    # Mutation endpoints status
    assert a['current_runtime_surface_state']['mutation_endpoints_status_code'] == 423
    assert len(a['current_runtime_surface_state']['mutation_endpoints_locked']) == 7
    # Inventory overlap: new collection MUST be named user_artifact_inventory
    assert a['existing_inventory_collections_overlap_audit']['new_artifact_inventory_must_be_named'] == 'user_artifact_inventory'
    assert 'user_artifacts' in a['existing_inventory_collections_overlap_audit']['must_NOT_extend_collections']

    # ---- Track B: schema design
    b = load('data/design/artifacts/inventory_schema_dry_run/artifact_inventory_schema_design_v1.json')
    assert b['verdict'] == 'TRACK_B_ARTIFACT_INVENTORY_SCHEMA_DESIGN_READY'
    assert b['design_status'] == 'design_only_not_applied'
    designed_collections = {c['name'] for c in b['collections']}
    assert REQUIRED_COLLECTIONS.issubset(designed_collections), \
        f"missing collections: {REQUIRED_COLLECTIONS - designed_collections}"
    # No live collection
    for c in b['collections']:
        assert c.get('is_live') is False, f"collection {c['name']} must be is_live=False"
    # forbidden fields globally listed
    forbidden_in_design = set(b['forbidden_global'])
    assert {"stat_bonus_active", "combat_modifier", "price", "purchase_url"}.issubset(forbidden_in_design)
    # user_artifact_inventory forbidden fields list
    uai = next(c for c in b['collections'] if c['name'] == 'user_artifact_inventory')
    uai_forbidden = set(uai.get('forbidden_fields', []))
    assert {"level", "equip_slot", "stat_bonus_active", "combat_modifier", "price"}.issubset(uai_forbidden)
    # idempotency design
    assert 'key_pattern' in b['idempotency_design']
    # constellations separate
    assert b['separation_from_other_systems']['constellations']['separate'] is True

    # ---- Track C: sample documents dry-run
    c = load('data/design/artifacts/inventory_schema_dry_run/artifact_inventory_sample_documents_v1.json')
    assert c['verdict'] == 'TRACK_C_ARTIFACT_INVENTORY_SAMPLE_DOCUMENT_DRY_RUN_READY'
    assert c['dry_run_mode'] == 'in_memory_static_no_db_insert'
    assert c['in_memory_validation_summary']['db_writes_performed'] == 0
    assert c['in_memory_validation_summary']['db_collections_created'] == 0
    assert c['in_memory_validation_summary']['docs_failed'] == 0
    # Verifica forbidden fields assenti nei sample
    def _check_no_forbidden(doc, ctx):
        if isinstance(doc, dict):
            for k in doc.keys():
                assert k not in FORBIDDEN_INVENTORY_FIELDS, f"forbidden field '{k}' in {ctx}"
            for k, v in doc.items():
                _check_no_forbidden(v, f"{ctx}.{k}")
        elif isinstance(doc, list):
            for i, v in enumerate(doc):
                _check_no_forbidden(v, f"{ctx}[{i}]")
    for inv_doc in c['sample_user_artifact_inventory']:
        _check_no_forbidden(inv_doc, "sample_user_artifact_inventory")
        # Required fields
        for req in ("inventory_id", "user_id", "server_profile_id", "artifact_id",
                    "quantity", "source_type", "status", "locked", "metadata_version"):
            assert req in inv_doc, f"missing required field {req}"
        assert inv_doc['status'] in ("owned", "archived", "revoked")
        assert isinstance(inv_doc['locked'], bool)
        assert inv_doc['quantity'] >= 0
    # Ledger events
    for evt in c['sample_ledger_events']:
        _check_no_forbidden(evt, "sample_ledger_events")
        for req in ("event_id", "user_id", "server_profile_id", "artifact_id",
                    "delta_quantity", "event_type", "source_type",
                    "idempotency_key", "actor_system"):
            assert req in evt, f"ledger missing required {req}"
        # idempotency_key pattern
        assert re.match(r'^[a-z_]+:[^:]+:[^:]+:relic_[a-z0-9_]+$', evt['idempotency_key']), \
            f"bad idempotency_key pattern: {evt['idempotency_key']}"
    # Duplicate grant scenario => second attempt is idempotent no-op
    dup = c['sample_duplicate_grant_scenario']
    assert dup['first_attempt']['idempotency_key'] == dup['second_attempt_same_key']['idempotency_key']
    assert dup['second_attempt_same_key']['expected_result'].startswith('idempotent_noop')
    assert dup['second_attempt_same_key']['quantity_change'] == 0
    # Revoke scenario => locked item blocked
    rev = c['sample_revoke_rollback_scenario']
    assert rev['locked_state'] is True
    assert rev['expected_result'] == 'revoke_blocked_locked_item'
    # alternative unlocked => compensating ledger entry with delta_quantity negative
    alt = rev['alternative_with_locked_false_user_alpha']
    assert alt['compensating_event']['delta_quantity'] < 0
    assert alt['compensating_event']['event_type'] == 'revoke'
    assert alt['inventory_post_state']['status'] == 'revoked'
    assert alt['never_hard_delete'] is True
    # Collection state with bonus inactive
    cs = c['sample_collection_state_bonus_inactive']
    assert cs['bonus_status'] == 'inactive'

    # ---- Track D: future API contract design-only
    d = load('data/design/artifacts/inventory_schema_dry_run/artifact_inventory_future_api_contract_v1.json')
    assert d['verdict'] == 'TRACK_D_ARTIFACT_INVENTORY_FUTURE_API_CONTRACT_DESIGN_READY'
    assert d['implementation_status'].startswith('design_only')
    assert d['live_now_state']['no_endpoint_implemented_in_this_pack'] is True
    assert d['live_now_state']['backend_route_changes_this_pack'] == 0
    for ep in d['future_endpoints']:
        assert ep.get('design_only') is True or ep.get('live_now') is False, \
            f"endpoint {ep['path']} must be design_only"
        # Forbidden fields not in design response envelopes
        env = ep.get('response_envelope_design') or {}
        env_str = json.dumps(env)
        for ff in ("price", "purchase_url", "stat_bonus_active", "combat_modifier"):
            assert ff not in env_str, f"forbidden field {ff} in {ep['path']} envelope"

    # ---- Track E: migration/rollback plan
    e = load('data/design/artifacts/inventory_schema_dry_run/artifact_inventory_db_migration_rollback_plan_v1.json')
    assert e['verdict'] == 'TRACK_E_ARTIFACT_INVENTORY_DB_MIGRATION_ROLLBACK_DRY_RUN_PLAN_READY'
    assert e['applied_now'] is False
    assert e['db_writes_performed'] == 0
    assert len(e['migration_stages']) >= 6
    assert e['rollback_plan']['global_strategy'].startswith('never_hard_delete')
    inv_rollback = e['rollback_plan']['rollback_invariants']
    assert inv_rollback['battle_engine_unchanged'] is True
    assert inv_rollback['gacha_rates_unchanged'] is True

    # ---- Track H: completion
    h = load('data/design/artifacts/inventory_schema_dry_run/artifact_inventory_schema_dry_run_completion_v1.json')
    assert h['verdict'] == 'TRACK_H_ARTIFACT_INVENTORY_SCHEMA_DRY_RUN_COMPLETION_READY'
    rc = h['runtime_changes_made']
    assert rc['frontend_ui_changes'] == 0
    assert rc['frontend_logic_changes'] == 0
    assert rc['backend_route_changes'] == 0
    assert rc['backend_logic_changes'] == 0
    assert rc['db_writes_from_scripts'] == 0
    assert rc['db_collections_created_live'] == 0
    assert rc['battle_engine_changes'] == 0
    assert rc['gacha_rate_changes'] == 0
    assert rc['inventory_state_added_live'] is False
    assert rc['new_endpoint_added_live'] is False
    assert rc['locked_endpoint_unlocked'] is False
    assert rc['validator_required_weakened'] is False

    # ---- Invariants MD5
    inv = h['invariants']
    assert md5('/app/backend/battle_engine.py') == inv['backend/battle_engine.py'], "battle_engine drift"
    assert md5('/app/backend/.env') == inv['backend/.env'], "backend/.env drift"
    assert md5('/app/frontend/app/artifacts-preview.tsx') == inv['frontend/app/artifacts-preview.tsx']
    assert md5('/app/frontend/app/artifacts.tsx') == inv['frontend/app/artifacts.tsx']
    assert md5('/app/frontend/app/(tabs)/gacha.tsx') == inv['frontend/app/(tabs)/gacha.tsx']

    # ---- Live re-check: catalog GET preserved + 7 POST locked still in source
    src = ROUTE_FILE.read_text()
    assert '@router.get("/artifacts/catalog")' in src
    assert '@router.get("/artifacts/catalog/preview")' in src
    assert 'ARTIFACT_MUTATION_ENDPOINT_LOCKED' in src
    assert 'CONSTELLATION_MUTATION_ENDPOINT_LOCKED' in src
    assert 'ARTIFACT_MUTATION_LOCK_STATUS = 423' in src
    # No new mutation endpoint added in routes for inventory
    assert '/artifacts/inventory' not in src, \
        "New /artifacts/inventory endpoint must NOT be implemented in this pack"
    assert '/artifacts/inventory/grant' not in src
    assert '/artifacts/inventory/revoke' not in src

    # ---- Frontend: artifacts-preview not modified (already verified by MD5)
    pre = (ROOT / 'frontend/app/artifacts-preview.tsx').read_text()
    assert '/api/artifacts/inventory' not in pre
    assert 'fetch(' not in pre

    print('[PASS] PROJECT_ARTIFACT_INVENTORY_SCHEMA_DRY_RUN master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
