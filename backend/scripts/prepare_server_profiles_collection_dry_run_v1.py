#!/usr/bin/env python3
"""
V8 BLOCK_A — SERVER_PROFILES_COLLECTION dry-run preparation script.

NON viene eseguito automaticamente: stampa solo le operazioni DB pianificate.
L'apply effettivo richiede V8_BLOCK_A_APPLY=YES E un futuro ops pack autorizzato.

Default mode (no env):
  - prints intended ops
  - does NOT touch the DB
  - exits 0 with status DRY_RUN

Apply mode (V8_BLOCK_A_APPLY=YES, only via explicit ops pack):
  - creates server_profiles collection if missing (mongo create_collection idempotent)
  - creates 3 canonical indexes (idempotent: skip-if-exists by name)
  - exits 0 with status APPLIED

Questo script NON e' wirato in supervisord, NON e' chiamato da nessun endpoint,
NON viene invocato dalla validator suite.

Exit 0 OK / 1 FAIL.
"""
import json
import os
import sys
from pathlib import Path

GATE_ENV = "V8_BLOCK_A_APPLY"
GATE_OK = "YES"
PLAN = Path("/app/data/design/server_lifecycle/server_profiles_collection_creation_plan_v1.json")

CANONICAL_INDEXES = [
    {"name": "idx_user_server", "keys": [("user_id", 1), ("server_id", 1)], "unique": True},
    {"name": "idx_user_active", "keys": [("user_id", 1), ("is_archived", 1)], "unique": False},
    {"name": "idx_server_active", "keys": [("server_id", 1), ("is_archived", 1)], "unique": False},
]


def _print_intended_ops() -> None:
    print("=== INTENDED DB OPERATIONS (NOT EXECUTED) ===")
    print("1) db.create_collection('server_profiles') if not exists")
    for idx in CANONICAL_INDEXES:
        keys = ", ".join(f"('{f}', {o})" for f, o in idx["keys"])
        unique = ", unique=True" if idx["unique"] else ""
        print(f"2) db.server_profiles.create_index([{keys}]{unique}, name='{idx['name']}')")
    print("=== END (no DB op executed) ===")


def main() -> None:
    if not PLAN.exists():
        print(f"[FAIL] plan JSON missing: {PLAN}")
        sys.exit(1)

    gated = os.environ.get(GATE_ENV) == GATE_OK
    if not gated:
        _print_intended_ops()
        print(json.dumps({
            "status": "DRY_RUN",
            "gating_env": f"{GATE_ENV}={GATE_OK} required for apply",
            "db_writes_executed": 0,
            "collection_created": False,
            "indexes_created": 0,
        }))
        sys.exit(0)

    # ---- Apply branch (only when explicitly gated) ----
    # NOTE: in V8 BLOCK_A this branch must NOT be executed. The branch exists only
    # so a future ops pack can reuse this same script verbatim.
    print("[GUARD] V8_BLOCK_A_APPLY=YES detected but V8 BLOCK_A pack does NOT authorize apply.")
    print("[GUARD] Refusing to mutate DB. Use a dedicated future ops pack with its own pack-level marker.")
    print(json.dumps({
        "status": "APPLY_REFUSED_NO_PACK_AUTHORIZATION",
        "db_writes_executed": 0,
        "collection_created": False,
        "indexes_created": 0,
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
