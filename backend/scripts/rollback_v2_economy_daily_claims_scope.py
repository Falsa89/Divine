#!/usr/bin/env python3
"""
V2 BLOCK_A rollback script (MEGA_COMBO_SLC_ACCELERATION_V2).

Reverts the daily_claims insert wrapping on economy.py back to plain insert_one
and removes the ensure_server_scope import added by V2 BLOCK_A.

This is a TEXTUAL rollback. It does NOT touch the DB.
It is safe to run only if BLOCK_A is the only consumer of ensure_server_scope in economy.py.

Exit codes: 0 success / 1 failure / 2 nothing-to-do
"""
import sys
from pathlib import Path

ECONOMY = Path("/app/backend/routes/economy.py")

IMPORT_LINE = "from utils.server_scope import ensure_server_scope\n"
NEW_INSERT = "        await db.daily_claims.insert_one(ensure_server_scope({\"user_id\": uid, \"item_id\": item_id, \"date\": today, \"timestamp\": datetime.utcnow()}, uid))\n"
OLD_INSERT = "        await db.daily_claims.insert_one({\"user_id\": uid, \"item_id\": item_id, \"date\": today, \"timestamp\": datetime.utcnow()})\n"


def main() -> None:
    if not ECONOMY.exists():
        print(f"[FAIL] missing target: {ECONOMY}")
        sys.exit(1)

    src = ECONOMY.read_text(encoding="utf-8")
    changed = False

    if NEW_INSERT in src:
        src = src.replace(NEW_INSERT, OLD_INSERT)
        changed = True

    if IMPORT_LINE in src:
        src = src.replace(IMPORT_LINE, "")
        changed = True

    if not changed:
        print("[NOOP] BLOCK_A patch not detected (already rolled back?)")
        sys.exit(2)

    ECONOMY.write_text(src, encoding="utf-8")
    print("[OK] BLOCK_A rollback applied (textual)")
    sys.exit(0)


if __name__ == "__main__":
    main()
