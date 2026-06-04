#!/usr/bin/env python3
# Validator: PROJECT-FIRST-SESSION-ONBOARDING-HARDENING
# Pack: MEGA_RELEASE_ACCELERATION_20_v71
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "contract": "data/design/onboarding/first_session_onboarding_hardening_contract_v1.json",
    "machine": "data/design/onboarding/first_session_onboarding_state_machine_preview_v1.json",
    "forbidden": "data/design/onboarding/first_session_onboarding_hardening_forbidden_scope_v1.json",
    "marker": "data/design/onboarding/first_session_onboarding_hardening_marker_v1.json",
}
SCREEN = "frontend/app/first-session-onboarding-preview.tsx"

CONTRACT_EXP = {
    "onboarding_hardening_preview": True,
    "authoritative_runtime": False,
    "backend_used": False,
    "db_writes": 0,
    "permanent_onboarding_complete": False,
    "account_flag_writes": False,
    "async_storage_persistence": False,
    "reward_grant_enabled": False,
    "progress_persistence_enabled": False,
    "local_preview_only": True,
    "public_mandatory_routing": False,
}
EXPECTED_STATES = {
    "intro", "training_preview", "story_alpha_preview",
    "event_arena_preview", "asset_status_explainer", "qa_ready_summary",
}

FORBIDDEN_SCREEN_SUBSTRINGS = [
    "/api/story/battle", "/api/battle/simulate",
    "from \"./story\"", "from './story'",
    "from \"./combat\"", "from './combat'",
    "battle_engine", "react-native-reanimated",
    "AsyncStorage", "@react-native-async-storage", "fetch(",
]
REQUIRED_SCREEN_SUBSTRINGS = [
    "HARDENED v71", "Hardening Panel", "DISABILITATO",
    "state machine (preview)",
    "permanent_onboarding_complete", "account_mutation",
    "async_storage_persistence",
]


def strip_comments(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    return src


def strip_safe_tokens(src: str) -> str:
    for t in ["battle_engine_runtime_used", "battle_engine_runtime", "async_storage_persistence"]:
        src = src.replace(t, "")
    return src


def main() -> int:
    errors = []
    for k, rel in FILES.items():
        if not os.path.isfile(os.path.join(ROOT, rel)):
            errors.append(f"MISSING_FILE: {k}={rel}")
    if not os.path.isfile(os.path.join(ROOT, SCREEN)):
        errors.append(f"MISSING_SCREEN: {SCREEN}")
    if errors:
        for e in errors:
            print(e)
        return 1

    contract = json.load(open(os.path.join(ROOT, FILES["contract"]), "r", encoding="utf-8"))
    for k, v in CONTRACT_EXP.items():
        if contract.get(k) != v:
            errors.append(f"CONTRACT_BAD: {k}={contract.get(k)!r} expected {v!r}")
    if set(contract.get("states") or []) != EXPECTED_STATES:
        errors.append("CONTRACT_STATES_MISMATCH")

    machine = json.load(open(os.path.join(ROOT, FILES["machine"]), "r", encoding="utf-8"))
    if machine.get("complete_action_enabled") is not False:
        errors.append("MACHINE_COMPLETE_ENABLED")
    if machine.get("db_writes") != 0:
        errors.append("MACHINE_BAD_DB_WRITES")
    states_in_machine = {s.get("id") for s in (machine.get("states") or [])}
    if states_in_machine != EXPECTED_STATES:
        errors.append("MACHINE_STATES_MISMATCH")

    forbidden = json.load(open(os.path.join(ROOT, FILES["forbidden"]), "r", encoding="utf-8"))
    for must in ["db_writes", "reward_grant", "permanent_onboarding_complete",
                 "account_flag_writes", "async_storage_persistence",
                 "battle_engine_runtime", "import_from_story_tsx",
                 "import_from_combat_tsx", "complete_onboarding_button_active"]:
        if must not in (forbidden.get("forbidden") or []):
            errors.append(f"FORBIDDEN_MISSING: {must}")

    marker = json.load(open(os.path.join(ROOT, FILES["marker"]), "r", encoding="utf-8"))
    if marker.get("hardened") is not True:
        errors.append("MARKER_NOT_HARDENED")
    if marker.get("complete_action_enabled") is not False:
        errors.append("MARKER_COMPLETE_ENABLED")

    text = open(os.path.join(ROOT, SCREEN), "r", encoding="utf-8").read()
    code = strip_safe_tokens(strip_comments(text))
    for bad in FORBIDDEN_SCREEN_SUBSTRINGS:
        if bad in code:
            errors.append(f"SCREEN_FORBIDDEN_SUBSTRING: {bad}")
    for good in REQUIRED_SCREEN_SUBSTRINGS:
        if good not in text:
            errors.append(f"SCREEN_REQUIRED_MISSING: {good}")

    if errors:
        for e in errors:
            print(e)
        return 1
    print("PROJECT-FIRST-SESSION-ONBOARDING-HARDENING: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
