#!/usr/bin/env python3
# Validator: PROJECT-BOSS-TOWER-ALPHA-LOOP-CONTRACTS
# Pack: MEGA_RELEASE_ACCELERATION_17_v68
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

FILES = {
    "contract": "data/design/modes/boss_tower_alpha_loop_contract_v1.json",
    "boss": "data/design/modes/boss_alpha_loop_preview_fixture_v1.json",
    "tower": "data/design/modes/tower_alpha_loop_preview_fixture_v1.json",
    "forbidden": "data/design/modes/boss_tower_alpha_loop_forbidden_scope_v1.json",
}


def main() -> int:
    errors = []
    for key, rel in FILES.items():
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p):
            errors.append(f"MISSING_FILE: {key}={rel}")
    if errors:
        for e in errors:
            print(e)
        return 1

    contract = json.load(open(os.path.join(ROOT, FILES["contract"]), "r", encoding="utf-8"))
    for k, v in {
        "alpha_loop_preview": True,
        "authoritative_runtime": False,
        "backend_used": False,
        "battle_engine_runtime_used": False,
        "db_writes": 0,
        "reward_grant_enabled": False,
        "permanent_progress_enabled": False,
        "result_authoritative": False,
        "local_preview_adapter": True,
        "leaderboard_writes": False,
        "ranking_writes": False,
        "battle_engine_py_changed": False,
        "backend_route_changed": False,
        "public_menu_routing": False,
    }.items():
        if contract.get(k) != v:
            errors.append(f"CONTRACT_BAD: {k}={contract.get(k)!r} expected {v!r}")

    boss = json.load(open(os.path.join(ROOT, FILES["boss"]), "r", encoding="utf-8"))
    if boss.get("mode") != "boss":
        errors.append("BOSS_BAD_MODE")
    bts = boss.get("timeline_steps_preview") or []
    if not (5 <= len(bts) <= 7):
        errors.append(f"BOSS_STEPS_OUT_OF_RANGE: {len(bts)}")
    if not boss.get("enrage_hint_preview"):
        errors.append("BOSS_MISSING_ENRAGE_HINT")
    if not boss.get("weakness_hint_preview"):
        errors.append("BOSS_MISSING_WEAKNESS_HINT")
    if boss.get("reward_grant_enabled") is not False:
        errors.append("BOSS_BAD_REWARD")

    tower = json.load(open(os.path.join(ROOT, FILES["tower"]), "r", encoding="utf-8"))
    if tower.get("mode") != "tower":
        errors.append("TOWER_BAD_MODE")
    tts = tower.get("timeline_steps_preview") or []
    if not (5 <= len(tts) <= 7):
        errors.append(f"TOWER_STEPS_OUT_OF_RANGE: {len(tts)}")
    for req in ("tower_id", "floor_id", "floor_number_preview", "modifier_hint_preview", "enemy_family_preview"):
        if req not in tower:
            errors.append(f"TOWER_MISSING_KEY: {req}")
    if tower.get("reward_grant_enabled") is not False:
        errors.append("TOWER_BAD_REWARD")

    forbidden = json.load(open(os.path.join(ROOT, FILES["forbidden"]), "r", encoding="utf-8"))
    for must in [
        "db_writes",
        "live_reward_grant",
        "permanent_progress",
        "battle_engine_runtime",
        "leaderboard_writes",
        "ranking_writes",
        "import_from_story_tsx",
        "import_from_combat_tsx",
    ]:
        if must not in (forbidden.get("forbidden") or []):
            errors.append(f"FORBIDDEN_MISSING: {must}")

    if errors:
        for e in errors:
            print(e)
        return 1

    print("PROJECT-BOSS-TOWER-ALPHA-LOOP-CONTRACTS: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
