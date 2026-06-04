#!/usr/bin/env python3
# Validator: PROJECT-EVENT-ARENA-FIRST-ALPHA-SLICE-CONTRACT
# Pack: MEGA_RELEASE_ACCELERATION_19_v70
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "top": "data/design/modes/event_arena_first_alpha_slice_contract_v1.json",
    "event": "data/design/modes/event_first_alpha_slice_contract_v1.json",
    "arena": "data/design/modes/arena_first_alpha_slice_contract_v1.json",
    "forbidden": "data/design/modes/event_arena_first_alpha_forbidden_scope_v1.json",
}
TOP_EXP = {
    "alpha_slice_preview": True,
    "authoritative_runtime": False,
    "backend_used": False,
    "battle_engine_runtime_used": False,
    "db_writes": 0,
    "reward_grant_enabled": False,
    "permanent_progress_enabled": False,
    "result_authoritative": False,
    "event_currency_enabled": False,
    "arena_ranking_enabled": False,
    "leaderboard_writes": False,
    "matchmaking_live": False,
    "public_pvp_enabled": False,
    "manual_approval_required": True,
}


def main() -> int:
    errors = []
    for k, rel in FILES.items():
        if not os.path.isfile(os.path.join(ROOT, rel)):
            errors.append(f"MISSING_FILE: {k}={rel}")
    if errors:
        for e in errors:
            print(e)
        return 1

    top = json.load(open(os.path.join(ROOT, FILES["top"]), "r", encoding="utf-8"))
    for k, v in TOP_EXP.items():
        if top.get(k) != v:
            errors.append(f"TOP_BAD: {k}={top.get(k)!r} expected {v!r}")

    event = json.load(open(os.path.join(ROOT, FILES["event"]), "r", encoding="utf-8"))
    if event.get("single_test_event_preview") is not True:
        errors.append("EVENT_NOT_SINGLE_TEST_PREVIEW")
    if event.get("event_id") != "event_alpha_test_001":
        errors.append("EVENT_BAD_ID")
    if event.get("event_currency_enabled") is not False:
        errors.append("EVENT_CURRENCY_ENABLED")
    ev_steps = event.get("timeline_steps_preview") or []
    if not (5 <= len(ev_steps) <= 7):
        errors.append(f"EVENT_STEPS_OUT_OF_RANGE: {len(ev_steps)}")

    arena = json.load(open(os.path.join(ROOT, FILES["arena"]), "r", encoding="utf-8"))
    if arena.get("bot_non_ranked_preview") is not True:
        errors.append("ARENA_NOT_BOT_NON_RANKED")
    if arena.get("arena_match_id") != "arena_alpha_bot_001":
        errors.append("ARENA_BAD_MATCH_ID")
    if arena.get("opponent_type") != "bot_preview":
        errors.append("ARENA_BAD_OPPONENT")
    if arena.get("bracket_preview") != "unranked_alpha":
        errors.append("ARENA_BAD_BRACKET")
    if arena.get("arena_ranking_enabled") is not False:
        errors.append("ARENA_RANKING_ENABLED")
    if arena.get("matchmaking_live") is not False:
        errors.append("ARENA_MATCHMAKING_LIVE")
    ar_steps = arena.get("timeline_steps_preview") or []
    if not (5 <= len(ar_steps) <= 7):
        errors.append(f"ARENA_STEPS_OUT_OF_RANGE: {len(ar_steps)}")

    forbidden = json.load(open(os.path.join(ROOT, FILES["forbidden"]), "r", encoding="utf-8"))
    for must in ["db_writes", "reward_grant", "event_currency", "arena_ranking",
                 "leaderboard_writes", "matchmaking_live", "battle_engine_runtime",
                 "import_from_story_tsx", "import_from_combat_tsx", "real_asset_import"]:
        if must not in (forbidden.get("forbidden") or []):
            errors.append(f"FORBIDDEN_MISSING: {must}")

    if errors:
        for e in errors:
            print(e)
        return 1
    print("PROJECT-EVENT-ARENA-FIRST-ALPHA-SLICE-CONTRACT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
