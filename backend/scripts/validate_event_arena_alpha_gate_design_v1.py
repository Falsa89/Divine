#!/usr/bin/env python3
# Validator: PROJECT-EVENT-ARENA-ALPHA-GATE-DESIGN
# Pack: MEGA_RELEASE_ACCELERATION_18_v69
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "contract": "data/design/modes/event_arena_alpha_gate_contract_v1.json",
    "event": "data/design/modes/event_alpha_gate_design_v1.json",
    "arena": "data/design/modes/arena_alpha_gate_design_v1.json",
    "forbidden": "data/design/modes/event_arena_forbidden_scope_v1.json",
}

CONTRACT_EXP = {
    "alpha_gate_design": True,
    "authoritative_runtime": False,
    "backend_used": False,
    "battle_engine_runtime_used": False,
    "db_writes": 0,
    "reward_grant_enabled": False,
    "event_currency_enabled": False,
    "arena_ranking_enabled": False,
    "leaderboard_writes": False,
    "matchmaking_live": False,
    "public_pvp_enabled": False,
    "manual_approval_required": True,
}

EVENT_GATES_REQUIRED = {
    "event_design_contract_signed",
    "event_currency_design_locked",
    "event_reward_table_design_locked",
    "event_idempotency_design_locked",
    "event_rollback_design_locked",
    "event_observation_plan_signed",
    "event_anti_abuse_design_locked",
    "manual_approval_pre_live",
}
ARENA_GATES_REQUIRED = {
    "arena_design_contract_signed",
    "arena_ranking_design_locked",
    "arena_mmr_design_locked",
    "arena_match_idempotency_design_locked",
    "arena_rollback_design_locked",
    "arena_observation_plan_signed",
    "arena_anti_abuse_design_locked",
    "manual_approval_pre_live",
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

    contract = json.load(open(os.path.join(ROOT, FILES["contract"]), "r", encoding="utf-8"))
    for k, v in CONTRACT_EXP.items():
        if contract.get(k) != v:
            errors.append(f"CONTRACT_BAD: {k}={contract.get(k)!r} expected {v!r}")

    event = json.load(open(os.path.join(ROOT, FILES["event"]), "r", encoding="utf-8"))
    if not EVENT_GATES_REQUIRED.issubset(set(event.get("required_gates") or [])):
        errors.append("EVENT_GATES_MISSING")
    if event.get("event_currency_enabled") is not False:
        errors.append("EVENT_CURRENCY_NOT_DISABLED")
    if event.get("db_writes") != 0:
        errors.append("EVENT_BAD_DB_WRITES")

    arena = json.load(open(os.path.join(ROOT, FILES["arena"]), "r", encoding="utf-8"))
    if not ARENA_GATES_REQUIRED.issubset(set(arena.get("required_gates") or [])):
        errors.append("ARENA_GATES_MISSING")
    if arena.get("arena_ranking_enabled") is not False:
        errors.append("ARENA_RANKING_NOT_DISABLED")
    if arena.get("matchmaking_live") is not False:
        errors.append("ARENA_MATCHMAKING_LIVE")
    if arena.get("db_writes") != 0:
        errors.append("ARENA_BAD_DB_WRITES")

    forbidden = json.load(open(os.path.join(ROOT, FILES["forbidden"]), "r", encoding="utf-8"))
    for must in [
        "db_writes", "reward_grant", "event_currency", "arena_ranking",
        "leaderboard_writes", "matchmaking_live", "battle_engine_runtime",
        "import_from_story_tsx", "import_from_combat_tsx",
    ]:
        if must not in (forbidden.get("forbidden") or []):
            errors.append(f"FORBIDDEN_MISSING: {must}")

    if errors:
        for e in errors:
            print(e)
        return 1
    print("PROJECT-EVENT-ARENA-ALPHA-GATE-DESIGN: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
