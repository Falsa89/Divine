#!/usr/bin/env python3
# Validator: PROJECT-BOSS-TOWER-ALPHA-LOOP-PREVIEW-UI
# Pack: MEGA_RELEASE_ACCELERATION_17_v68
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCREEN = "frontend/app/boss-tower-alpha-loop-preview.tsx"
MARKER = "data/design/modes/boss_tower_alpha_loop_preview_ui_marker_v1.json"


def strip_comments(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    return src


def strip_safe_tokens(src: str) -> str:
    safe_tokens = [
        "battle_engine_runtime_used",
        "battle_engine_runtime",
        "battle_engine_py_changed",
    ]
    for t in safe_tokens:
        src = src.replace(t, "")
    return src

FORBIDDEN_SUBSTRINGS = [
    "/api/story/battle",
    "/api/battle/simulate",
    "from \"./story\"",
    "from './story'",
    "from \"./combat\"",
    "from './combat'",
    "battle_engine",
    "react-native-reanimated",
    "AsyncStorage",
    "@react-native-async-storage",
    "fetch(",
]

REQUIRED_SUBSTRINGS = [
    "Boss Alpha Loop",
    "Tower Alpha Loop",
    "DEEPLINK-ONLY",
    "result_authoritative",
    "reward_grant_enabled",
]


def main() -> int:
    errors = []
    p_screen = os.path.join(ROOT, SCREEN)
    p_marker = os.path.join(ROOT, MARKER)
    if not os.path.isfile(p_screen):
        errors.append(f"MISSING_SCREEN: {SCREEN}")
    if not os.path.isfile(p_marker):
        errors.append(f"MISSING_MARKER: {MARKER}")
    if errors:
        for e in errors:
            print(e)
        return 1

    text = open(p_screen, "r", encoding="utf-8").read()
    code = strip_safe_tokens(strip_comments(text))
    for bad in FORBIDDEN_SUBSTRINGS:
        if bad in code:
            errors.append(f"FORBIDDEN_SUBSTRING: {bad}")
    for good in REQUIRED_SUBSTRINGS:
        if good not in text:
            errors.append(f"REQUIRED_MISSING: {good}")

    marker = json.load(open(p_marker, "r", encoding="utf-8"))
    if marker.get("deeplink_only") is not True:
        errors.append("MARKER_NOT_DEEPLINK_ONLY")
    if marker.get("db_writes") != 0:
        errors.append("MARKER_BAD_DB_WRITES")
    if marker.get("battle_engine_runtime_used") is not False:
        errors.append("MARKER_BAD_BE_RUNTIME_USED")
    if marker.get("reward_grant_enabled") is not False:
        errors.append("MARKER_BAD_REWARD_GRANT")

    if errors:
        for e in errors:
            print(e)
        return 1

    print("PROJECT-BOSS-TOWER-ALPHA-LOOP-PREVIEW-UI: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
