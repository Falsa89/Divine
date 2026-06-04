#!/usr/bin/env python3
# Validator: PROJECT-FIRST-SESSION-ONBOARDING-CONTRACT
# Pack: MEGA_RELEASE_ACCELERATION_19_v70
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "contract": "data/design/onboarding/first_session_onboarding_contract_v1.json",
    "flow": "data/design/onboarding/first_session_preview_flow_v1.json",
    "forbidden": "data/design/onboarding/first_session_onboarding_forbidden_scope_v1.json",
}

CONTRACT_EXP = {
    "onboarding_preview": True,
    "first_session_preview_only": True,
    "authoritative_runtime": False,
    "backend_used": False,
    "db_writes": 0,
    "permanent_onboarding_complete": False,
    "reward_grant_enabled": False,
    "inventory_mutation": False,
    "wallet_mutation": False,
    "account_flag_writes": False,
    "tutorial_completion_persistence": False,
    "forced_public_routing": False,
    "async_storage_persistence": False,
    "links_are_deeplink_only": True,
    "manual_approval_required": True,
}
EXPECTED_STEPS = {
    "welcome", "training_combat_onboarding_preview", "story_alpha_slice_preview",
    "event_arena_gate_or_alpha_preview", "hero_asset_status_explainer", "next_steps_summary",
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
    if set(contract.get("steps") or []) != EXPECTED_STEPS:
        errors.append("CONTRACT_STEPS_MISMATCH")

    flow = json.load(open(os.path.join(ROOT, FILES["flow"]), "r", encoding="utf-8"))
    if flow.get("db_writes") != 0:
        errors.append("FLOW_BAD_DB_WRITES")
    if flow.get("permanent_onboarding_complete") is not False:
        errors.append("FLOW_BAD_ONBOARDING_COMPLETE")
    if flow.get("async_storage_persistence") is not False:
        errors.append("FLOW_BAD_ASYNC_STORAGE")
    flow_steps = flow.get("steps") or []
    if len(flow_steps) != 6:
        errors.append(f"FLOW_BAD_STEP_COUNT: {len(flow_steps)}")

    forbidden = json.load(open(os.path.join(ROOT, FILES["forbidden"]), "r", encoding="utf-8"))
    for must in ["db_writes", "reward_grant", "permanent_progress",
                 "permanent_onboarding_complete", "account_flag_writes",
                 "async_storage_persistence", "battle_engine_runtime",
                 "import_from_story_tsx", "import_from_combat_tsx"]:
        if must not in (forbidden.get("forbidden") or []):
            errors.append(f"FORBIDDEN_MISSING: {must}")

    if errors:
        for e in errors:
            print(e)
        return 1
    print("PROJECT-FIRST-SESSION-ONBOARDING-CONTRACT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
