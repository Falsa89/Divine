#!/usr/bin/env python3
# Validator: PROJECT-TRAINING-COMBAT-ONBOARDING-CONTRACT
# Pack: MEGA_RELEASE_ACCELERATION_18_v69
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "contract": "data/design/onboarding/training_combat_onboarding_contract_v1.json",
    "flow": "data/design/onboarding/combat_basics_tutorial_flow_v1.json",
    "forbidden": "data/design/onboarding/training_preview_forbidden_scope_v1.json",
}

EXPECTED_CONTRACT = {
    "onboarding_preview": True,
    "authoritative_runtime": False,
    "backend_used": False,
    "battle_engine_runtime_used": False,
    "story_tsx_changed": False,
    "combat_tsx_changed": False,
    "db_writes": 0,
    "reward_grant_enabled": False,
    "permanent_progress_enabled": False,
    "result_authoritative": False,
    "local_preview_adapter": True,
}
EXPECTED_TEACHES = {
    "team_positioning",
    "attack_order",
    "skill_preview",
    "result_preview",
    "reward_preview_disabled",
    "progress_preview_disabled",
    "preview_vs_real_battle",
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
    for k, v in EXPECTED_CONTRACT.items():
        if contract.get(k) != v:
            errors.append(f"CONTRACT_BAD: {k}={contract.get(k)!r} expected {v!r}")
    if not EXPECTED_TEACHES.issubset(set(contract.get("teaches") or [])):
        errors.append("CONTRACT_TEACHES_MISSING")

    flow = json.load(open(os.path.join(ROOT, FILES["flow"]), "r", encoding="utf-8"))
    steps = flow.get("steps") or []
    if not (5 <= len(steps) <= 7):
        errors.append(f"FLOW_STEPS_OUT_OF_RANGE: {len(steps)}")
    if flow.get("db_writes") != 0:
        errors.append("FLOW_BAD_DB_WRITES")
    if flow.get("reward_grant_enabled") is not False:
        errors.append("FLOW_BAD_REWARD")

    forbidden = json.load(open(os.path.join(ROOT, FILES["forbidden"]), "r", encoding="utf-8"))
    for must in [
        "db_writes", "reward_grant", "permanent_progress",
        "battle_engine_runtime", "import_from_story_tsx", "import_from_combat_tsx",
    ]:
        if must not in (forbidden.get("forbidden") or []):
            errors.append(f"FORBIDDEN_MISSING: {must}")

    if errors:
        for e in errors:
            print(e)
        return 1
    print("PROJECT-TRAINING-COMBAT-ONBOARDING-CONTRACT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
