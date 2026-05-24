#!/usr/bin/env python3
"""
V8 BLOCK_B — BATTLE_PASS unique index on (user_id, season) dry-run.

Default mode (no env):
  - prints intended create_index call
  - exits 0 with status DRY_RUN

Apply mode (V8_BLOCK_B_APPLY=YES):
  - in V8 BLOCK_B: APPLY_REFUSED_NO_PACK_AUTHORIZATION
  - branch present only for reuse by a future ops pack

NON viene eseguito automaticamente. Non in supervisord, non in suite.

Exit 0 OK / 1 FAIL.
"""
import json
import os
import sys
from pathlib import Path

GATE_ENV = "V8_BLOCK_B_APPLY"
GATE_OK = "YES"
PLAN = Path("/app/data/design/server_lifecycle/battle_pass_user_season_index_definition_v1.json")

INDEX_KEYS = [("user_id", 1), ("season", 1)]
INDEX_NAME = "idx_battle_pass_user_season"
INDEX_UNIQUE = True


def _print_intended_ops() -> None:
    print("=== INTENDED DB OPERATIONS (NOT EXECUTED) ===")
    keys = ", ".join(f"('{f}', {o})" for f, o in INDEX_KEYS)
    print(f"1) db.battle_pass.create_index([{keys}], unique={INDEX_UNIQUE}, name='{INDEX_NAME}')")
    print("2) Pre-flight (read-only, to be executed by future apply pack only):")
    print("   - db.battle_pass.count_documents({'season': {'$exists': False}})  # MUST be 0")
    print("   - aggregate: $group by (user_id, season), $match count > 1  # MUST be []")
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
            "index_created": False,
        }))
        sys.exit(0)

    # Apply branch: refused in V8 (only the future ops pack may use this).
    print("[GUARD] V8_BLOCK_B_APPLY=YES detected but V8 BLOCK_B pack does NOT authorize apply.")
    print("[GUARD] Refusing to mutate DB. Use a dedicated future ops pack with its own pack-level marker.")
    print(json.dumps({
        "status": "APPLY_REFUSED_NO_PACK_AUTHORIZATION",
        "db_writes_executed": 0,
        "index_created": False,
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
