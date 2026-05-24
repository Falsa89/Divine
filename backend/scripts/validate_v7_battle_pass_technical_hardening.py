#!/usr/bin/env python3
"""
V7 BLOCK_B validator (read-only).

Verifica che POST /api/battlepass/buy-premium usi ora il pattern $setOnInsert
(con i 5 default canonici: exp, level, claimed_free, claimed_premium, season) +
$set: {is_premium: True}, e che la logica della response sia invariata.

Verifica inoltre:
- marker integrity (verdict, runtime_patch_applied=True, no DB migration, no index creation)
- nessun side-effect di reward/lane/cost
- presenza riferimento al signoff V6 BLOCK_A

NON esegue HTTP, NON tocca DB. Sicuro in suite.

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

MARKER = Path("/app/data/design/system_safety/v7_battle_pass_technical_hardening_marker.json")
ECONOMY = Path("/app/backend/routes/economy.py")
V6_BLOCK_A_SIGNOFF = Path("/app/data/design/server_lifecycle/battle_pass_bp_d1_d3_d4_signoff_record_v1.json")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    # ---- 1. Marker integrity ----
    if not MARKER.exists():
        fail(f"missing marker: {MARKER}")
    m = json.loads(MARKER.read_text(encoding="utf-8"))
    if m.get("verdict") != "BLOCK_B_BATTLE_PASS_TECHNICAL_HARDENING_POST_SIGNOFF_APPLIED_SAFE":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not True:
        fail("runtime_patch_applied must be True")
    if m.get("db_migration_required") is not False:
        fail("db_migration_required must be False")
    if m.get("db_index_created") is not False:
        fail("db_index_created must be False (V7 does NOT create indexes)")
    changes = m.get("changes", {})
    for key in ("reward_change", "premium_lane_logic_change", "free_lane_logic_change",
                "cost_change", "response_schema_change", "behavior_change"):
        if changes.get(key) is not False:
            fail(f"changes.{key} must be False")

    # ---- 2. Source code: new $setOnInsert pattern present in battle_pass.update_one ----
    if not ECONOMY.exists():
        fail(f"missing target file: {ECONOMY}")
    src = ECONOMY.read_text(encoding="utf-8")
    if 'V7 BLOCK_B post-signoff hardening' not in src:
        fail("V7 BLOCK_B marker comment not found in economy.py")
    if '$setOnInsert' not in src:
        fail("$setOnInsert not detected in economy.py (V7 BLOCK_B hardening missing)")
    # Verify the 5 canonical default fields are wired on insert.
    for default_field in ('"exp": 0', '"level": 1', '"claimed_free": []',
                          '"claimed_premium": []', '"season": 1'):
        if default_field not in src:
            fail(f"default field {default_field} not found in $setOnInsert payload")
    # is_premium must still be in $set (behavior preserved).
    if '"$set": {"is_premium": True}' not in src:
        fail('$set: {"is_premium": True} block not detected (behavior must be preserved)')
    # Cost preserved.
    if 'cost = 500' not in src:
        fail("buy-premium cost changed (must remain 500 gems)")
    if 'Servono {cost} gemme!' not in src and "Servono {cost} gemme" not in src:
        fail("buy-premium error message changed (response shape preserved)")
    # Response unchanged.
    if 'return {"success": True}' not in src:
        fail('buy_premium_pass response shape changed (must remain {"success": True})')

    # ---- 3. Old buggy pattern must be GONE (not coexisting). ----
    # The legacy line was: $set: {is_premium: True}, upsert=True  with no $setOnInsert in the same call.
    # We detect that the buy-premium block now has $setOnInsert before $set.
    buy_idx = src.find('async def buy_premium_pass')
    if buy_idx < 0:
        fail("buy_premium_pass function not found")
    block = src[buy_idx:buy_idx + 1200]
    if '$setOnInsert' not in block or '$set' not in block:
        fail("buy_premium_pass block missing $setOnInsert+$set composition")
    if block.find('$setOnInsert') > block.find('upsert=True'):
        fail("$setOnInsert must come BEFORE the upsert=True flag in the update_one call")

    # ---- 4. Cross-reference to V6 BLOCK_A signoff ----
    if not V6_BLOCK_A_SIGNOFF.exists():
        fail(f"V6 BLOCK_A signoff record missing (post-signoff dependency unmet): {V6_BLOCK_A_SIGNOFF}")

    print("[PASS] V7 BLOCK_B $setOnInsert hardening applicato; behavior/cost/response invariati; signoff dependency rispettata")
    sys.exit(0)


if __name__ == "__main__":
    main()
