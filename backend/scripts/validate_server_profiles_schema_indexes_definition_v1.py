#!/usr/bin/env python3
"""
V7 BLOCK_C validator (read-only, design-only).

Verifica la definizione canonica degli indici per server_profiles SENZA
chiamare create_index e SENZA toccare il DB.

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

MARKER = Path("/app/data/design/server_lifecycle/server_profiles_schema_indexes_definition_v1.json")
V6_SCHEMA_PROPOSAL = Path("/app/data/design/server_lifecycle/server_profiles_canonical_schema_proposal_v1.json")

EXPECTED_INDEXES = {
    "idx_user_server": {"unique": True, "fields": ["user_id", "server_id"]},
    "idx_user_active": {"unique": False, "fields": ["user_id", "is_archived"]},
    "idx_server_active": {"unique": False, "fields": ["server_id", "is_archived"]},
}


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not MARKER.exists():
        fail(f"missing marker: {MARKER}")
    m = json.loads(MARKER.read_text(encoding="utf-8"))

    if m.get("verdict") != "BLOCK_C_SERVER_PROFILES_SCHEMA_INDEXES_DEFINITION_READY":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be False (design-only)")
    if m.get("db_index_created") is not False:
        fail("db_index_created must be False (no DB write in V7)")

    indexes = m.get("indexes_canonical_definition", [])
    if not isinstance(indexes, list) or len(indexes) != 3:
        fail(f"expected 3 canonical indexes, got {len(indexes) if isinstance(indexes, list) else 'n/a'}")

    by_name = {idx.get("name"): idx for idx in indexes}
    for expected_name, props in EXPECTED_INDEXES.items():
        if expected_name not in by_name:
            fail(f"missing canonical index: {expected_name}")
        idx = by_name[expected_name]
        if idx.get("unique") is not props["unique"]:
            fail(f"index {expected_name} unique flag mismatch (expected {props['unique']})")
        fields_actual = [f.get("field") for f in idx.get("fields", [])]
        if fields_actual != props["fields"]:
            fail(f"index {expected_name} fields mismatch: expected {props['fields']} got {fields_actual}")
        if idx.get("collection") != "server_profiles":
            fail(f"index {expected_name} collection must be server_profiles")
        if not idx.get("deferred_to_pack"):
            fail(f"index {expected_name} must declare deferred_to_pack for apply")

    forb = m.get("forbidden_in_block_c_respected", {})
    for key in ("db_index_creation", "db_write", "collection_creation", "runtime_endpoint_implementation"):
        if forb.get(key) is not False:
            fail(f"forbidden_in_block_c_respected.{key} must be False")

    # Upstream V6 schema proposal cross-reference must still exist.
    if not V6_SCHEMA_PROPOSAL.exists():
        fail(f"upstream V6 schema proposal missing: {V6_SCHEMA_PROPOSAL}")

    print("[PASS] V7 BLOCK_C 3 canonical indexes defined; no DB write; upstream V6 proposal preserved")
    sys.exit(0)


if __name__ == "__main__":
    main()
