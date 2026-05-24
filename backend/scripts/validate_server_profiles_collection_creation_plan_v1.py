#!/usr/bin/env python3
"""
V8 BLOCK_A validator (read-only).

Verifica:
- plan JSON integrity + verdict
- dry-run script presente, non auto-run, gated
- upstream references V6/V7 esistenti
- nessuna DB write/index/collection mutation autorizzata

NON tocca DB, NON esegue lo script dry-run, NON fa HTTP.
Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

PLAN = Path("/app/data/design/server_lifecycle/server_profiles_collection_creation_plan_v1.json")
DRY_RUN_SCRIPT = Path("/app/backend/scripts/prepare_server_profiles_collection_dry_run_v1.py")
V6_SCHEMA = Path("/app/data/design/server_lifecycle/server_profiles_canonical_schema_proposal_v1.json")
V7_INDEXES = Path("/app/data/design/server_lifecycle/server_profiles_schema_indexes_definition_v1.json")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not PLAN.exists():
        fail(f"missing plan: {PLAN}")
    m = json.loads(PLAN.read_text(encoding="utf-8"))
    if m.get("verdict") != "BLOCK_A_SERVER_PROFILES_COLLECTION_CREATION_READY":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be False (design-only)")
    if m.get("db_collection_created") is not False:
        fail("db_collection_created must be False")
    if m.get("db_index_created") is not False:
        fail("db_index_created must be False")
    if m.get("db_writes_executed") != 0:
        fail("db_writes_executed must be 0")

    if not DRY_RUN_SCRIPT.exists():
        fail(f"dry-run script missing: {DRY_RUN_SCRIPT}")
    src = DRY_RUN_SCRIPT.read_text(encoding="utf-8")
    if "V8_BLOCK_A_APPLY" not in src:
        fail("dry-run script missing gating env V8_BLOCK_A_APPLY")
    if "NON viene eseguito automaticamente" not in src and "NOT EXECUTED" not in src:
        fail("dry-run script missing explicit 'not auto-run' contract in docstring/output")
    if "APPLY_REFUSED_NO_PACK_AUTHORIZATION" not in src:
        fail("dry-run script missing apply guard 'APPLY_REFUSED_NO_PACK_AUTHORIZATION'")

    # Upstream design references.
    if not V6_SCHEMA.exists():
        fail(f"upstream V6 schema missing: {V6_SCHEMA}")
    if not V7_INDEXES.exists():
        fail(f"upstream V7 indexes missing: {V7_INDEXES}")

    # Forbidden scope.
    forb = m.get("forbidden_in_block_a_respected", {})
    for k in ("live_collection_creation", "live_index_creation", "migration_backfill",
              "endpoint_implementation", "feature_flag_enable", "second_server"):
        if forb.get(k) is not False:
            fail(f"forbidden_in_block_a_respected.{k} must be False")

    # Three indexes consistency.
    idxs = m.get("three_indexes_to_create_when_apply_authorized", [])
    if len(idxs) != 3:
        fail(f"expected 3 indexes, got {len(idxs)}")
    names = {i.get("name") for i in idxs}
    if names != {"idx_user_server", "idx_user_active", "idx_server_active"}:
        fail(f"index names mismatch: {names}")

    print("[PASS] V8 BLOCK_A plan integrity OK; dry-run script gated; upstream V6/V7 preserved")
    sys.exit(0)


if __name__ == "__main__":
    main()
