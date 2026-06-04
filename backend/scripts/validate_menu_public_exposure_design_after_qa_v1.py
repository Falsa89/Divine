#!/usr/bin/env python3
# Validator: PROJECT-MENU-PUBLIC-EXPOSURE-DESIGN-AFTER-QA
# Pack: MEGA_RELEASE_ACCELERATION_21_v72
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "design": "data/design/navigation/menu_public_exposure_design_after_qa_v1.json",
    "gates": "data/design/navigation/menu_public_exposure_gate_matrix_v1.json",
    "forbidden": "data/design/navigation/menu_public_exposure_forbidden_scope_v1.json",
    "marker": "data/design/navigation/menu_public_exposure_design_marker_v1.json",
}
DESIGN_EXP = {
    "design_only": True,
    "public_menu_exposure_enabled": False,
    "home_menu_routing_enabled": False,
    "production_navigation_changed": False,
    "db_writes": 0,
    "manual_approval_required": True,
    "qa_pass_required": True,
    "zero_p0_required": True,
    "zero_p1_required": True,
    "asset_pack_required_for_production_exposure": True,
}
REQUIRED_GATES = {
    "qa_pass", "zero_p0_open", "zero_p1_open",
    "guardrail_assertions_pass", "md5_invariants_intact",
    "manual_approval", "closed_alpha_testing_complete",
    "asset_pack_for_production_exposure",
}


def main() -> int:
    errors = []
    for k, rel in FILES.items():
        if not os.path.isfile(os.path.join(ROOT, rel)):
            errors.append(f"MISSING_FILE: {k}={rel}")
    if errors:
        for e in errors: print(e)
        return 1

    design = json.load(open(os.path.join(ROOT, FILES["design"]), "r", encoding="utf-8"))
    for k, v in DESIGN_EXP.items():
        if design.get(k) != v:
            errors.append(f"DESIGN_BAD: {k}={design.get(k)!r} expected {v!r}")

    gates = json.load(open(os.path.join(ROOT, FILES["gates"]), "r", encoding="utf-8"))
    gate_ids = {g.get("id") for g in (gates.get("gates") or [])}
    if not REQUIRED_GATES.issubset(gate_ids):
        errors.append(f"GATES_MISSING: {sorted(REQUIRED_GATES - gate_ids)}")
    if gates.get("overall_ready_for_public_exposure") is not False:
        errors.append("GATES_READY_TRUE_NOT_ALLOWED")
    if gates.get("public_menu_exposure_enabled") is not False:
        errors.append("GATES_PUBLIC_MENU_EXPOSURE_TRUE")

    forbidden = json.load(open(os.path.join(ROOT, FILES["forbidden"]), "r", encoding="utf-8"))
    for must in ["public_menu_exposure", "home_cta_route",
                 "production_navigation_changes", "reward_progress_persistence",
                 "battle_engine_runtime", "import_from_story_tsx",
                 "import_from_combat_tsx"]:
        if must not in (forbidden.get("forbidden") or []):
            errors.append(f"FORBIDDEN_MISSING: {must}")

    marker = json.load(open(os.path.join(ROOT, FILES["marker"]), "r", encoding="utf-8"))
    if marker.get("public_menu_exposure_enabled") is not False:
        errors.append("MARKER_PUBLIC_MENU_ENABLED")
    if marker.get("manual_approval_required") is not True:
        errors.append("MARKER_NO_MANUAL_APPROVAL")
    if marker.get("db_writes") != 0:
        errors.append("MARKER_BAD_DB_WRITES")

    if errors:
        for e in errors: print(e)
        return 1
    print("PROJECT-MENU-PUBLIC-EXPOSURE-DESIGN-AFTER-QA: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
