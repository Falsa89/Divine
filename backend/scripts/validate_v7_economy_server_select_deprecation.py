#!/usr/bin/env python3
"""
V7 BLOCK_A validator (read-only).

Verifica che il deprecation notice WARNING-level su POST /api/server/select sia
presente in /app/backend/routes/economy.py senza alcun cambio di comportamento
rispetto alla logica di selezione del server. Verifica inoltre l'integrita' del
marker JSON.

NON esegue HTTP, NON tocca DB. Sicuro in suite.

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

MARKER = Path("/app/data/design/system_safety/v7_economy_server_select_deprecation_marker.json")
ECONOMY = Path("/app/backend/routes/economy.py")
REMOVAL_PLAN_DOC = Path("/app/docs/divine/120D_LEGACY_SERVER_SELECT_REMOVAL_PLAN.md")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    # ---- 1. Marker integrity ----
    if not MARKER.exists():
        fail(f"missing marker: {MARKER}")
    m = json.loads(MARKER.read_text(encoding="utf-8"))
    if m.get("verdict") != "BLOCK_A_ECONOMY_SERVER_SELECT_DEPRECATION_NOTICE_APPLIED_SAFE":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not True:
        fail("marker says runtime_patch_applied must be True (V7 BLOCK_A applied)")
    if m.get("db_writes_executed") != 0:
        fail("db_writes_executed must be 0")
    if m.get("db_migration_required") is not False:
        fail("db_migration_required must be False")
    changes = m.get("changes", {})
    for key in ("behavior_changed", "response_schema_changed", "selection_logic_unchanged"):
        # The first two must be false; the third must be true.
        if key == "selection_logic_unchanged":
            if changes.get(key) is not True:
                fail(f"changes.{key} must be True")
        else:
            if changes.get(key) is not False:
                fail(f"changes.{key} must be False")

    # ---- 2. Source code: deprecation notice present in the right surface ----
    if not ECONOMY.exists():
        fail(f"missing target file: {ECONOMY}")
    src = ECONOMY.read_text(encoding="utf-8")
    if 'V7 BLOCK_A DEPRECATION NOTICE' not in src:
        fail("V7 BLOCK_A deprecation notice marker comment not found in economy.py")
    if 'divine.deprecation' not in src:
        fail("divine.deprecation logger name not found in economy.py (deprecation log missing)")
    if 'DEPRECATED /api/server/select' not in src:
        fail("deprecation WARNING line content not found in economy.py")
    # The legacy route definition must still be present and unchanged in behavior.
    if '@router.post("/server/select")' not in src:
        fail("POST /server/select route definition removed; behavior MUST be unchanged")
    if 'async def select_server' not in src:
        fail("select_server function removed; behavior MUST be unchanged")
    # Selection logic (server lookup) must still be present.
    if 'next((s for s in SERVERS if s["id"] == req.server_id)' not in src:
        fail("server selection logic (SERVERS lookup) altered or removed")

    # ---- 3. Removal plan doc cross-reference must exist ----
    if not REMOVAL_PLAN_DOC.exists():
        fail(f"upstream removal plan doc missing: {REMOVAL_PLAN_DOC}")

    # ---- 4. Forbidden scope respected ----
    forb = m.get("forbidden_in_block_a_respected", {})
    for key in ("endpoint_behavior_change", "endpoint_removal", "response_shape_change", "db_write_migration"):
        if forb.get(key) is not False:
            fail(f"forbidden_in_block_a_respected.{key} must be False")

    print("[PASS] V7 BLOCK_A deprecation notice presente; logica selezione invariata; marker integro")
    sys.exit(0)


if __name__ == "__main__":
    main()
