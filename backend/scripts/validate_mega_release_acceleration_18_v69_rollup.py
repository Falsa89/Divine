#!/usr/bin/env python3
# Validator: MEGA-RELEASE-ACCELERATION-18-v69-ROLLUP
# Pack: MEGA_RELEASE_ACCELERATION_18_v69
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ROLLUP = "data/design/release_acceleration/mega_release_acceleration_18_v69_rollup_marker_v1.json"

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
    "docs/divine/413_TRAINING_COMBAT_ONBOARDING_CONTRACT.md",
    "docs/divine/414_TRAINING_COMBAT_ONBOARDING_PREVIEW_UI.md",
    "docs/divine/415_EVENT_ARENA_ALPHA_GATE_DESIGN.md",
    "docs/divine/416_EVENT_ARENA_ALPHA_GATE_PREVIEW_UI.md",
    "docs/divine/417_HERO_ASSET_DRYRUN_MANIFEST_READINESS.md",
    "docs/divine/418_TRAINING_EVENT_ARENA_ASSET_READINESS_QA.md",
    "docs/divine/419_MEGA_RELEASE_ACCELERATION_18_TRAINING_EVENT_ARENA_ASSET_READINESS_v69.md",
]

VALIDATORS = [
    "backend/scripts/validate_training_combat_onboarding_contract_v1.py",
    "backend/scripts/validate_training_combat_onboarding_preview_ui_v1.py",
    "backend/scripts/validate_event_arena_alpha_gate_design_v1.py",
    "backend/scripts/validate_event_arena_alpha_gate_preview_ui_v1.py",
    "backend/scripts/validate_hero_asset_dryrun_manifest_readiness_v1.py",
    "backend/scripts/validate_training_event_arena_asset_readiness_qa_v1.py",
    "backend/scripts/validate_mega_release_acceleration_18_v69_rollup.py",
]

SCREENS = [
    "frontend/app/training-combat-onboarding-preview.tsx",
    "frontend/app/event-arena-alpha-gate-preview.tsx",
]

SCANNER = "backend/scripts/hero_asset_dryrun_manifest_scanner_v1.py"
EXPECTED_TAG = "PUBLIC_SYNC_TAG_v69_MEGA_RELEASE_ACCELERATION_18_TRAINING_EVENT_ARENA_ASSET_READINESS"


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
    for k in (
        "db_writes",
    ):
        if marker.get(k) != 0:
            errors.append(f"BAD_{k.upper()}")
    for k in (
        "reward_grant_enabled", "permanent_progress_enabled",
        "battle_engine_runtime_used", "backend_route_changed",
        "server_py_changed", "story_tsx_changed", "combat_tsx_changed",
        "event_currency_enabled", "arena_ranking_enabled",
        "real_asset_import", "file_copy_enabled",
        "asset_runtime_resolver_changed", "character_bible_changed",
        "validator_weakening", "fake_pass",
    ):
        if marker.get(k) is not False:
            errors.append(f"BAD_{k.upper()}")

    for d in DOCS + VALIDATORS + SCREENS + [SCANNER]:
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
    print("MEGA-RELEASE-ACCELERATION-18-v69-ROLLUP: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
