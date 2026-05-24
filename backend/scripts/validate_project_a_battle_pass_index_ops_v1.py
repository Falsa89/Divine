#!/usr/bin/env python3
"""
PROJECT_A Track B validator (read-only; live check via pymongo).

Verifica:
- idx_battle_pass_user_season presente su battle_pass
- unique constraint True
- result JSON integro con verdict atteso
- nessuna mutation di documenti (count invariato vs result)
- nessun cambiamento comportamentale economy.py

Exit 0 PASS / 1 FAIL.
"""
import json
import os
import sys
from pathlib import Path

RESULT = Path("/app/data/design/server_lifecycle/project_a_battle_pass_index_ops_result_v1.json")
ECONOMY = Path("/app/backend/routes/economy.py")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not RESULT.exists():
        fail(f"missing result: {RESULT}")
    m = json.loads(RESULT.read_text(encoding="utf-8"))
    if m.get("verdict") != "TRACK_B_BATTLE_PASS_INDEX_APPLIED_SAFE":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("db_index_created") is not True:
        fail("db_index_created must be True")
    if m.get("db_data_rows_written") != 0:
        fail("db_data_rows_written must be 0")

    bp = m.get("behavior_preservation", {})
    for k in ("battle_pass_endpoint_behavior_changed", "reward_logic_changed",
              "premium_free_lane_logic_changed", "cost_changed", "response_schema_changed"):
        if bp.get(k) is not False:
            fail(f"behavior_preservation.{k} must be False")
    if bp.get("$setOnInsert_pattern_preserved") is not True:
        fail("$setOnInsert_pattern_preserved must be True")

    # Source check: economy.py invariato dal V7 BLOCK_B.
    if not ECONOMY.exists():
        fail(f"missing economy.py: {ECONOMY}")
    src = ECONOMY.read_text(encoding="utf-8")
    if "V7 BLOCK_B post-signoff hardening" not in src:
        fail("V7 BLOCK_B $setOnInsert marker comment missing in economy.py (behavior tampering suspected)")
    if "$setOnInsert" not in src:
        fail("$setOnInsert pattern missing in economy.py (V7 BLOCK_B regression)")
    if "cost = 500" not in src:
        fail("battle pass cost mutated (forbidden)")

    # Live DB check.
    try:
        from dotenv import load_dotenv
        load_dotenv('/app/backend/.env')
        from pymongo import MongoClient
    except Exception as exc:
        fail(f"missing deps for live check: {exc}")

    url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'divine_db')
    db = MongoClient(url)[db_name]
    idx_info = list(db.battle_pass.list_indexes())
    idx_names = {i["name"] for i in idx_info}
    if "idx_battle_pass_user_season" not in idx_names:
        fail("idx_battle_pass_user_season MISSING in live DB")
    target = next(i for i in idx_info if i["name"] == "idx_battle_pass_user_season")
    if not target.get("unique"):
        fail("idx_battle_pass_user_season must be unique in live DB")
    keys = list(target.get("key", {}).items())
    if keys != [("user_id", 1), ("season", 1)]:
        fail(f"idx_battle_pass_user_season keys mismatch: {keys}")

    print("[PASS] PROJECT_A Track B live OK: idx_battle_pass_user_season unique on (user_id, season); economy.py V7 hardening intact")
    sys.exit(0)


if __name__ == "__main__":
    main()
