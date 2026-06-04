#!/usr/bin/env python3
# Validator: MEGA-RELEASE-ACCELERATION-21-v72-ROLLUP
# Pack: MEGA_RELEASE_ACCELERATION_21_v72
import hashlib, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ROLLUP = "data/design/release_acceleration/mega_release_acceleration_21_v72_rollup_marker_v1.json"

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
    "docs/divine/433_ALPHA_INTERNAL_QA_RUN_EVIDENCE.md",
    "docs/divine/434_ALPHA_INTERNAL_QA_BUG_BACKLOG_TRIAGE.md",
    "docs/divine/435_CONTROLLED_PREVIEW_ONLY_BUGFIX_BATCH.md",
    "docs/divine/436_MENU_PUBLIC_EXPOSURE_DESIGN_AFTER_QA.md",
    "docs/divine/437_ALPHA_QA_EXIT_CRITERIA_AND_v73_READINESS.md",
    "docs/divine/438_MEGA_RELEASE_ACCELERATION_21_ALPHA_QA_MENU_DESIGN_v72.md",
]
VALIDATORS = [
    "backend/scripts/validate_alpha_internal_qa_run_evidence_v1.py",
    "backend/scripts/validate_alpha_internal_qa_bug_backlog_v1.py",
    "backend/scripts/validate_controlled_preview_only_bugfix_v1.py",
    "backend/scripts/validate_menu_public_exposure_design_after_qa_v1.py",
    "backend/scripts/validate_alpha_qa_exit_criteria_v73_readiness_v1.py",
    "backend/scripts/validate_mega_release_acceleration_21_v72_rollup.py",
]
EXPECTED_TAG = "PUBLIC_SYNC_TAG_v72_MEGA_RELEASE_ACCELERATION_21_ALPHA_QA_MENU_DESIGN"


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
    if marker.get("bugfix_applied") is not False:
        errors.append("BAD_BUGFIX_APPLIED")
    for k in (
        "reward_grant_enabled", "permanent_progress_enabled",
        "permanent_onboarding_complete", "battle_engine_runtime_used",
        "backend_route_changed", "server_py_changed",
        "story_tsx_changed", "combat_tsx_changed",
        "event_currency_enabled", "arena_ranking_enabled", "matchmaking_live",
        "account_flag_writes", "async_storage_persistence",
        "public_menu_routing_enabled", "public_menu_exposure_enabled",
        "production_navigation_changed",
        "real_asset_import", "file_copy_enabled",
        "asset_runtime_resolver_changed", "character_bible_changed",
        "hero_roster_changed", "validator_weakening", "fake_pass",
    ):
        if marker.get(k) is not False:
            errors.append(f"BAD_{k.upper()}")

    for d in DOCS + VALIDATORS:
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
        for e in errors: print(e)
        return 1
    print("MEGA-RELEASE-ACCELERATION-21-v72-ROLLUP: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
