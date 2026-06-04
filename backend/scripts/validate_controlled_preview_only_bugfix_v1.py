#!/usr/bin/env python3
# Validator: PROJECT-CONTROLLED-PREVIEW-ONLY-BUGFIX
# Pack: MEGA_RELEASE_ACCELERATION_21_v72
import hashlib, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "apply": "data/design/qa/alpha_internal_qa_bugfix_apply_result_v1.json",
    "marker": "data/design/qa/controlled_preview_only_bugfix_marker_v1.json",
}

PROTECTED = {
    "backend/battle_engine.py": "151ca35ad3bc35f0a6209cb3744ed440",
    "backend/.env": "ff60bbb79efa329b71aa8ed351ea89b3",
    "backend/routes/artifacts.py": "893f244d85fd45cbe825996463995293",
    "frontend/app/battlepass.tsx": "54568b8cb75a07033f78ef6593aba839",
    "frontend/app/vip.tsx": "45fcc9890b6b128c37088bc33aa54caf",
    "backend/server.py": "055df030553f4791e8cac14254f1b148",
    "frontend/app/combat.tsx": "fc792a05b2ada6e677d80400732ae5c3",
    "frontend/app/story.tsx": "8520627b4e63f86821d73d8d3880bac3",
}

ALLOWED_FIX_FILES = {
    "frontend/app/alpha-preview-hub.tsx",
    "frontend/app/first-session-onboarding-preview.tsx",
    "frontend/app/training-combat-onboarding-preview.tsx",
    "frontend/app/event-arena-alpha-gate-preview.tsx",
    "frontend/app/event-arena-first-alpha-slice-preview.tsx",
    "frontend/app/story-alpha-slice-preview.tsx",
    "frontend/app/boss-tower-alpha-loop-preview.tsx",
}


def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    errors = []
    for k, rel in FILES.items():
        if not os.path.isfile(os.path.join(ROOT, rel)):
            errors.append(f"MISSING_FILE: {k}={rel}")
    if errors:
        for e in errors: print(e)
        return 1

    apply_ = json.load(open(os.path.join(ROOT, FILES["apply"]), "r", encoding="utf-8"))
    safety = apply_.get("safety_flags") or {}
    for k in ("reward_grant", "account_persistence", "public_menu_routing_enabled",
              "backend_route_changed", "story_tsx_changed", "combat_tsx_changed",
              "battle_engine_runtime_used", "real_asset_import"):
        if safety.get(k) is not False:
            errors.append(f"SAFETY_BAD_{k.upper()}")
    if safety.get("db_writes") != 0:
        errors.append("SAFETY_BAD_DB_WRITES")

    files_touched = apply_.get("files_touched") or []
    for f in files_touched:
        if f not in ALLOWED_FIX_FILES:
            errors.append(f"FIX_FILE_NOT_ALLOWED: {f}")

    if apply_.get("applied") is True:
        if apply_.get("applied_fixes_count", 0) <= 0:
            errors.append("APPLY_INCONSISTENT_COUNT")
        if apply_.get("ts_check_required") is not True:
            errors.append("APPLY_TS_CHECK_NOT_REQUIRED")
        if apply_.get("ts_check_result") != "PASS":
            errors.append("APPLY_TS_CHECK_NOT_PASS")
    else:
        if apply_.get("applied_fixes_count", 0) != 0:
            errors.append("APPLY_FALSE_BUT_COUNT_NONZERO")
        if not apply_.get("reason"):
            errors.append("APPLY_FALSE_NO_REASON")

    marker = json.load(open(os.path.join(ROOT, FILES["marker"]), "r", encoding="utf-8"))
    if marker.get("all_fixes_preview_only") is not True:
        errors.append("MARKER_NOT_PREVIEW_ONLY")
    if marker.get("db_writes") != 0:
        errors.append("MARKER_BAD_DB_WRITES")

    for rel, expected in PROTECTED.items():
        actual = md5(os.path.join(ROOT, rel))
        if actual != expected:
            errors.append(f"MD5_PROTECTED_CHANGED: {rel} got {actual}")

    if errors:
        for e in errors: print(e)
        return 1
    print("PROJECT-CONTROLLED-PREVIEW-ONLY-BUGFIX: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
