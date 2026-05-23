#!/usr/bin/env python3
"""
V2 BLOCK_A post-apply validator (MEGA_COMBO_SLC_ACCELERATION_V2).

Verifica che la patch su economy.py W02 (daily_claims.insert_one) sia attiva:
- import ensure_server_scope presente
- chiamata ensure_server_scope avvolge l'insert daily_claims
- marker JSON consistente con verdict APPLIED_SAFE

Non esegue scritture DB. Read-only.

Exit codes: 0 PASS / 1 FAIL
"""
import json
import sys
from pathlib import Path

ECONOMY = Path("/app/backend/routes/economy.py")
MARKER = Path("/app/data/design/system_safety/v2_economy_daily_claims_scope_marker.json")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not ECONOMY.exists():
        fail(f"missing target file: {ECONOMY}")
    if not MARKER.exists():
        fail(f"missing marker: {MARKER}")

    src = ECONOMY.read_text(encoding="utf-8")

    if "from utils.server_scope import ensure_server_scope" not in src:
        fail("economy.py is missing ensure_server_scope import")

    # Heuristic: the daily_claims insert MUST be wrapped in ensure_server_scope
    # Look for the canonical pattern around the daily_claims insert.
    lines = src.splitlines()
    daily_insert_idx = -1
    for i, ln in enumerate(lines):
        if "db.daily_claims.insert_one" in ln:
            daily_insert_idx = i
            break
    if daily_insert_idx < 0:
        fail("db.daily_claims.insert_one not found")

    insert_line = lines[daily_insert_idx]
    if "ensure_server_scope(" not in insert_line:
        fail(f"daily_claims insert not wrapped in ensure_server_scope: {insert_line.strip()}")

    m = json.loads(MARKER.read_text(encoding="utf-8"))
    if m.get("verdict") != "BLOCK_A_ECONOMY_DAILY_CLAIMS_SCOPE_APPLIED_SAFE":
        fail(f"unexpected marker verdict: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not True:
        fail("marker runtime_patch_applied must be true")
    if m.get("db_migration_required") is not False:
        fail("marker must declare no DB migration")

    changes = m.get("changes", {})
    forbidden_flags = [
        "behavior_changed",
        "reward_amount_changed",
        "cooldown_changed",
        "currency_logic_changed",
        "vip_changed",
        "paid_balance_changed",
        "shop_changed",
        "battle_pass_changed",
        "server_select_changed",
    ]
    for k in forbidden_flags:
        if changes.get(k) is not False:
            fail(f"changes.{k} must be false in BLOCK_A (got {changes.get(k)})")

    print("[PASS] V2 BLOCK_A economy daily_claims scope APPLIED_SAFE")
    sys.exit(0)


if __name__ == "__main__":
    main()
