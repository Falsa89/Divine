#!/usr/bin/env python3
"""
V7 BLOCK_B rollback (gated, idempotent).

Ripristina il pattern legacy $set: {is_premium: True} sulla update_one di
battle_pass dentro POST /api/battlepass/buy-premium in
/app/backend/routes/economy.py, rimuovendo il blocco $setOnInsert introdotto
da V7 BLOCK_B.

Non viene eseguito automaticamente: richiede V7_BLOCK_B_ROLLBACK=YES.

Usage:
  V7_BLOCK_B_ROLLBACK=YES python3 /app/backend/scripts/rollback_v7_battle_pass_technical_hardening.py

Exit 0 OK / 1 FAIL.
"""
import os
import re
import sys
from pathlib import Path

GATE_ENV = "V7_BLOCK_B_ROLLBACK"
GATE_OK = "YES"
ECONOMY = Path("/app/backend/routes/economy.py")
MARKER = Path("/app/data/design/system_safety/v7_battle_pass_technical_hardening_marker.json")
ROLLBACK_ID = "v7_block_b_battle_pass_hardening"

# Match the V7 BLOCK_B inserted multi-line update_one (with $setOnInsert + $set) and rewrite
# to the legacy one-line $set form. Anchored to the comment marker introduced by V7.
V7_BLOCK_REGEX = re.compile(
    r"        # V7 BLOCK_B post-signoff hardening:.*?\n"
    r"        # Authorized by V6 BLOCK_A signoff record.*?\n"
    r"        # Behavior preserved:.*?\n"
    r"        await db\.battle_pass\.update_one\(\n"
    r"            \{\"user_id\": uid\},\n"
    r"            \{\n"
    r"                \"\$setOnInsert\": \{\"exp\": 0, \"level\": 1, \"claimed_free\": \[\], \"claimed_premium\": \[\], \"season\": 1\},\n"
    r"                \"\$set\": \{\"is_premium\": True\},\n"
    r"            \},\n"
    r"            upsert=True,\n"
    r"        \)\n",
    re.DOTALL,
)

LEGACY_REPLACEMENT = (
    '        await db.battle_pass.update_one({"user_id": uid}, '
    '{"$set": {"is_premium": True}}, upsert=True)\n'
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

    if 'V7 BLOCK_B post-signoff hardening' not in src:
        print(f"[OK] rollback {ROLLBACK_ID} already in target state (no-op)")
        sys.exit(0)

    new_src, n = V7_BLOCK_REGEX.subn(LEGACY_REPLACEMENT, src, count=1)
    if n == 0:
        fail("V7 BLOCK_B block could not be matched verbatim; manual review required")
    if '$setOnInsert' in new_src and 'battle_pass' in new_src.split('$setOnInsert')[1][:200]:
        fail("residual $setOnInsert on battle_pass detected after rollback")

    ECONOMY.write_text(new_src, encoding="utf-8")
    print(f"[OK] rollback {ROLLBACK_ID} applied: $setOnInsert pattern reverted to legacy $set in {ECONOMY}")
    print(f"     marker JSON preserved (history): {MARKER}")
    sys.exit(0)


if __name__ == "__main__":
    main()
