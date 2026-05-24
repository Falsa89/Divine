#!/usr/bin/env python3
"""
V7 BLOCK_A rollback (gated, idempotent).

Rimuove SOLO il blocco di deprecation notice WARNING-level introdotto dal
patch V7 BLOCK_A su POST /api/server/select in /app/backend/routes/economy.py.
Non viene eseguito automaticamente: richiede env var V7_BLOCK_A_ROLLBACK=YES.

Usage:
  V7_BLOCK_A_ROLLBACK=YES python3 /app/backend/scripts/rollback_v7_economy_server_select_deprecation.py

Exit 0 OK / 1 FAIL.
"""
import os
import re
import sys
from pathlib import Path

GATE_ENV = "V7_BLOCK_A_ROLLBACK"
GATE_OK = "YES"
ECONOMY = Path("/app/backend/routes/economy.py")
MARKER = Path("/app/data/design/system_safety/v7_economy_server_select_deprecation_marker.json")
ROLLBACK_ID = "v7_block_a_server_select_deprecation"

# The exact V7 BLOCK_A inserted block (between the function signature and the SERVERS lookup).
BLOCK_REGEX = re.compile(
    r"        # V7 BLOCK_A DEPRECATION NOTICE.*?\n"
    r"        # See: /app/docs/divine/120D_LEGACY_SERVER_SELECT_REMOVAL_PLAN\.md.*?\n"
    r"        # Behavior unchanged; passive warning only\.\n"
    r"        import logging as _logging\n"
    r"        _logging\.getLogger\(\"divine\.deprecation\"\)\.warning\(\n"
    r"            \"DEPRECATED /api/server/select called by user_id=%s server_id=%s; \"\n"
    r"            \"will be removed after SLC-H live wiring per LEGACY_SERVER_SELECT_REMOVAL_PLAN v1\",\n"
    r"            current_user\.get\(\"id\"\), req\.server_id,\n"
    r"        \)\n",
    re.DOTALL,
)


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if os.environ.get(GATE_ENV) != GATE_OK:
        print(f"[GATED] rollback {ROLLBACK_ID} NOT executed. Set {GATE_ENV}={GATE_OK} to proceed.")
        sys.exit(0)

    if not ECONOMY.exists():
        fail(f"missing target file: {ECONOMY}")
    src = ECONOMY.read_text(encoding="utf-8")

    if 'V7 BLOCK_A DEPRECATION NOTICE' not in src:
        # Already rolled back (idempotent success).
        print(f"[OK] rollback {ROLLBACK_ID} already in target state (no-op)")
        sys.exit(0)

    new_src, n = BLOCK_REGEX.subn("", src, count=1)
    if n == 0:
        fail("V7 BLOCK_A block could not be matched verbatim; manual review required")
    if 'V7 BLOCK_A DEPRECATION NOTICE' in new_src:
        fail("residual V7 BLOCK_A marker detected after substitution")

    ECONOMY.write_text(new_src, encoding="utf-8")
    print(f"[OK] rollback {ROLLBACK_ID} applied: deprecation notice block removed from {ECONOMY}")
    print(f"     marker JSON preserved (history): {MARKER}")
    sys.exit(0)


if __name__ == "__main__":
    main()
