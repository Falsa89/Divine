#!/usr/bin/env python3
# Validator: MEGA-RELEASE-ACCELERATION-17-v68-ROLLUP
# Pack: MEGA_RELEASE_ACCELERATION_17_v68
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ROLLUP = "data/design/release_acceleration/mega_release_acceleration_17_v68_rollup_marker_v1.json"

# MD5 invariants ufficiali (5) + extra unchanged guardrails (4).
INVARIANTS_OFFICIAL = {
    "backend/battle_engine.py": "151ca35ad3bc35f0a6209cb3744ed440",
    "backend/.env": "ff60bbb79efa329b71aa8ed351ea89b3",
    "backend/routes/artifacts.py": "893f244d85fd45cbe825996463995293",
    "frontend/app/battlepass.tsx": "54568b8cb75a07033f78ef6593aba839",
    "frontend/app/vip.tsx": "45fcc9890b6b128c37088bc33aa54caf",
}
EXTRA_UNCHANGED = {
    "backend/server.py": "055df030553f4791e8cac14254f1b148",
    "frontend/app/combat.tsx": "fc792a05b2ada6e677d80400732ae5c3",
    "frontend/app/story.tsx": "8520627b4e63f86821d73d8d3880bac3",
}

DOCS = [
    "docs/divine/406_STORY_FIRST_PLAYABLE_ALPHA_SLICE_CONTRACT.md",
    "docs/divine/407_STORY_ALPHA_SLICE_PREVIEW_SCREEN.md",
    "docs/divine/408_BOSS_TOWER_ALPHA_LOOP_CONTRACTS.md",
    "docs/divine/409_BOSS_TOWER_ALPHA_LOOP_PREVIEW_UI.md",
    "docs/divine/410_ALPHA_SLICE_RESULT_IDEMPOTENCY_BOUNDARY.md",
    "docs/divine/411_STORY_BOSS_TOWER_ALPHA_LOOP_QA.md",
    "docs/divine/412_MEGA_RELEASE_ACCELERATION_17_STORY_BOSS_TOWER_ALPHA_LOOP_v68.md",
]

VALIDATORS = [
    "backend/scripts/validate_story_first_playable_alpha_slice_contract_v1.py",
    "backend/scripts/validate_story_alpha_slice_preview_screen_v1.py",
    "backend/scripts/validate_boss_tower_alpha_loop_contracts_v1.py",
    "backend/scripts/validate_boss_tower_alpha_loop_preview_ui_v1.py",
    "backend/scripts/validate_alpha_slice_result_idempotency_boundary_v1.py",
    "backend/scripts/validate_story_boss_tower_alpha_loop_qa_v1.py",
    "backend/scripts/validate_mega_release_acceleration_17_v68_rollup.py",
]

SCREENS = [
    "frontend/app/story-alpha-slice-preview.tsx",
    "frontend/app/boss-tower-alpha-loop-preview.tsx",
]

EXPECTED_TAG = "PUBLIC_SYNC_TAG_v68_MEGA_RELEASE_ACCELERATION_17_STORY_BOSS_TOWER_ALPHA_LOOP"


def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    errors = []
    rp = os.path.join(ROOT, ROLLUP)
    if not os.path.isfile(rp):
        print(f"MISSING_ROLLUP: {ROLLUP}")
        return 1

    marker = json.load(open(rp, "r", encoding="utf-8"))
    if marker.get("public_sync_tag") != EXPECTED_TAG:
        errors.append("BAD_PUBLIC_SYNC_TAG")
    if marker.get("db_writes") != 0:
        errors.append("BAD_DB_WRITES")
    if marker.get("reward_grant_enabled") is not False:
        errors.append("BAD_REWARD_GRANT")
    if marker.get("permanent_progress_enabled") is not False:
        errors.append("BAD_PERMANENT_PROGRESS")
    if marker.get("battle_engine_runtime_used") is not False:
        errors.append("BAD_BE_RUNTIME")
    if marker.get("server_py_changed") is not False:
        errors.append("BAD_SERVER_PY_CHANGED")
    if marker.get("story_tsx_changed") is not False:
        errors.append("BAD_STORY_TSX_CHANGED")
    if marker.get("combat_tsx_changed") is not False:
        errors.append("BAD_COMBAT_TSX_CHANGED")
    if marker.get("validator_weakening") is not False:
        errors.append("BAD_VALIDATOR_WEAKENING")
    if marker.get("fake_pass") is not False:
        errors.append("BAD_FAKE_PASS")

    for d in DOCS + VALIDATORS + SCREENS:
        if not os.path.isfile(os.path.join(ROOT, d)):
            errors.append(f"MISSING: {d}")

    for rel, expected in INVARIANTS_OFFICIAL.items():
        actual = md5(os.path.join(ROOT, rel))
        if actual != expected:
            errors.append(f"MD5_OFFICIAL_MISMATCH: {rel} got {actual} expected {expected}")

    for rel, expected in EXTRA_UNCHANGED.items():
        actual = md5(os.path.join(ROOT, rel))
        if actual != expected:
            errors.append(f"MD5_EXTRA_MISMATCH: {rel} got {actual} expected {expected}")

    if errors:
        for e in errors:
            print(e)
        return 1

    print("MEGA-RELEASE-ACCELERATION-17-v68-ROLLUP: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
