#!/usr/bin/env python3
"""
V4 BLOCK_A validator (MEGA_COMBO_SLC_ACCELERATION_V4).

This block decided READY_NOT_APPLIED. The validator verifies that:
- the marker JSON exists with the correct verdict;
- no runtime patch was applied to economy.py for battle_pass.buy-premium upsert
  (i.e., the line still uses the legacy $set upsert pattern, not $setOnInsert).

Read-only. Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

MARKER = Path("/app/data/design/system_safety/v4_battle_pass_technical_hardening_marker.json")
ECONOMY = Path("/app/backend/routes/economy.py")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not MARKER.exists():
        fail(f"missing marker: {MARKER}")
    m = json.loads(MARKER.read_text(encoding="utf-8"))
    if m.get("verdict") != "BLOCK_A_BATTLE_PASS_TECHNICAL_HARDENING_READY_NOT_APPLIED":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be false")
    if m.get("db_writes_executed") != 0:
        fail("db_writes_executed must be 0")

    if not ECONOMY.exists():
        fail(f"missing target file: {ECONOMY}")
    src = ECONOMY.read_text(encoding="utf-8")

    # The legacy $set upsert pattern MUST still be present (no apply).
    if 'battle_pass.update_one({"user_id": uid}, {"$set": {"is_premium": True}}, upsert=True)' not in src:
        fail("legacy battle_pass buy-premium upsert pattern not detected; possible unauthorized patch")
    # The $setOnInsert form must NOT be present (i.e., apply did not happen).
    if '$setOnInsert' in src and 'battle_pass' in src.split('$setOnInsert')[1][:200]:
        fail("$setOnInsert on battle_pass detected; apply path used despite READY_NOT_APPLIED")

    reasons = m.get("reasons_for_ready_not_applied", [])
    if len(reasons) < 3:
        fail("expected >=3 reasons documented for READY_NOT_APPLIED")

    print("[PASS] V4 BLOCK_A READY_NOT_APPLIED state intact (no unauthorized apply)")
    sys.exit(0)


if __name__ == "__main__":
    main()
