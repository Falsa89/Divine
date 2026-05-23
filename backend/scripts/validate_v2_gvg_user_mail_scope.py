#!/usr/bin/env python3
"""
V2 BLOCK_B post-apply validator (MEGA_COMBO_SLC_ACCELERATION_V2).

Verifica che la patch su gvg.py (user_mail.insert_one) sia attiva.
Non esegue scritture DB. Read-only.
"""
import json
import sys
from pathlib import Path

GVG = Path("/app/backend/routes/gvg.py")
MARKER = Path("/app/data/design/system_safety/v2_gvg_user_mail_scope_marker.json")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not GVG.exists():
        fail(f"missing target file: {GVG}")
    if not MARKER.exists():
        fail(f"missing marker: {MARKER}")

    src = GVG.read_text(encoding="utf-8")

    if "from utils.server_scope import ensure_server_scope" not in src:
        fail("gvg.py is missing ensure_server_scope import (expected pre-existing)")

    # Locate the user_mail insert and verify wrapping
    if "db.user_mail.insert_one" not in src:
        fail("db.user_mail.insert_one not found in gvg.py")

    # Heuristic: check that the user_mail insert is wrapped in ensure_server_scope.
    # Find the line and confirm ensure_server_scope appears on the same statement.
    idx = src.find("db.user_mail.insert_one")
    window = src[idx:idx + 200]
    if "ensure_server_scope(" not in window:
        fail("user_mail insert is not wrapped in ensure_server_scope")

    m = json.loads(MARKER.read_text(encoding="utf-8"))
    if m.get("verdict") != "BLOCK_B_GVG_USER_MAIL_SCOPE_APPLIED_SAFE":
        fail(f"unexpected marker verdict: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not True:
        fail("marker runtime_patch_applied must be true")

    changes = m.get("changes", {})
    forbidden_flags = [
        "mail_content_changed",
        "recipient_changed",
        "inbox_behavior_changed",
        "gvg_war_logic_changed",
        "rewards_changed",
        "ranking_changed",
        "matching_changed",
        "attack_defense_changed",
    ]
    for k in forbidden_flags:
        if changes.get(k) is not False:
            fail(f"changes.{k} must be false in BLOCK_B (got {changes.get(k)})")

    print("[PASS] V2 BLOCK_B gvg user_mail scope APPLIED_SAFE")
    sys.exit(0)


if __name__ == "__main__":
    main()
