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
# V7 BLOCK_B has authorized the post-signoff hardening apply. When that marker is
# present with runtime_patch_applied=True, the legacy $set-only pattern is
# legitimately superseded by the $setOnInsert+$set composition.
V7_BLOCK_B_MARKER = Path("/app/data/design/system_safety/v7_battle_pass_technical_hardening_marker.json")


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

    # V7-aware transition: if V7 BLOCK_B marker exists and authorizes the apply,
    # the new $setOnInsert pattern is expected; otherwise, the legacy $set
    # pattern MUST still be present (no unauthorized apply).
    v7_applied = False
    if V7_BLOCK_B_MARKER.exists():
        try:
            v7m = json.loads(V7_BLOCK_B_MARKER.read_text(encoding="utf-8"))
            if (v7m.get("verdict") == "BLOCK_B_BATTLE_PASS_TECHNICAL_HARDENING_POST_SIGNOFF_APPLIED_SAFE"
                    and v7m.get("runtime_patch_applied") is True):
                v7_applied = True
        except Exception as exc:
            fail(f"V7 BLOCK_B marker present but unparseable: {exc}")

    if v7_applied:
        # Post-V7: hardened form must be in place.
        if '$setOnInsert' not in src:
            fail("V7 BLOCK_B marker authorizes apply but $setOnInsert pattern not detected in economy.py")
        if 'V7 BLOCK_B post-signoff hardening' not in src:
            fail("V7 BLOCK_B marker authorizes apply but in-code marker comment missing in economy.py")
    else:
        # Pre-V7: legacy form must still be present (no unauthorized apply).
        if 'battle_pass.update_one({"user_id": uid}, {"$set": {"is_premium": True}}, upsert=True)' not in src:
            fail("legacy battle_pass buy-premium upsert pattern not detected; possible unauthorized patch (no V7 BLOCK_B authorization)")
        # The $setOnInsert form must NOT be present (i.e., apply did not happen).
        if '$setOnInsert' in src and 'battle_pass' in src.split('$setOnInsert')[1][:200]:
            fail("$setOnInsert on battle_pass detected; apply path used despite READY_NOT_APPLIED and no V7 BLOCK_B authorization")

    reasons = m.get("reasons_for_ready_not_applied", [])
    if len(reasons) < 3:
        fail("expected >=3 reasons documented for READY_NOT_APPLIED")

    if v7_applied:
        print("[PASS] V4 BLOCK_A historical READY_NOT_APPLIED marker intact; superseded by V7 BLOCK_B authorized apply")
    else:
        print("[PASS] V4 BLOCK_A READY_NOT_APPLIED state intact (no unauthorized apply)")
    sys.exit(0)


if __name__ == "__main__":
    main()
