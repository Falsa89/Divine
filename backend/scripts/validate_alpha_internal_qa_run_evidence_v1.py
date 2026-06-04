#!/usr/bin/env python3
# Validator: PROJECT-ALPHA-INTERNAL-QA-RUN-EVIDENCE
# Pack: MEGA_RELEASE_ACCELERATION_21_v72
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "run": "data/design/qa/alpha_internal_qa_run_result_v1.json",
    "smoke": "data/design/qa/alpha_internal_qa_route_smoke_result_v1.json",
    "assertion": "data/design/qa/alpha_internal_qa_guardrail_assertion_result_v1.json",
    "marker": "data/design/qa/alpha_internal_qa_run_evidence_marker_v1.json",
}


def main() -> int:
    errors = []
    for k, rel in FILES.items():
        if not os.path.isfile(os.path.join(ROOT, rel)):
            errors.append(f"MISSING_FILE: {k}={rel}")
    if errors:
        for e in errors: print(e)
        return 1

    run = json.load(open(os.path.join(ROOT, FILES["run"]), "r", encoding="utf-8"))
    for k, v in {
        "run_read_only": True, "network_used": False, "backend_calls": False,
        "db_writes": 0, "reward_grant": False, "account_persistence": False,
        "real_asset_import": False, "runner_overall_ready": True,
    }.items():
        if run.get(k) != v:
            errors.append(f"RUN_BAD: {k}={run.get(k)!r} expected {v!r}")
    if run.get("screens_missing"):
        errors.append("RUN_SCREENS_MISSING_NOT_EMPTY")
    if run.get("contracts_missing"):
        errors.append("RUN_CONTRACTS_MISSING_NOT_EMPTY")

    smoke = json.load(open(os.path.join(ROOT, FILES["smoke"]), "r", encoding="utf-8"))
    if smoke.get("static_local_existence_only") is not True:
        errors.append("SMOKE_NOT_STATIC")
    if smoke.get("network_navigation_used") is not False:
        errors.append("SMOKE_NETWORK_USED")
    if smoke.get("db_writes") != 0:
        errors.append("SMOKE_BAD_DB_WRITES")
    routes = smoke.get("routes") or []
    if len(routes) < 7:
        errors.append(f"SMOKE_TOO_FEW_ROUTES: {len(routes)}")
    for r in routes:
        if r.get("result") != "PASS":
            errors.append(f"SMOKE_ROUTE_FAIL: {r.get('route')}")
        if r.get("deeplink_only") is not True:
            errors.append(f"SMOKE_ROUTE_NOT_DEEPLINK: {r.get('route')}")

    assertion = json.load(open(os.path.join(ROOT, FILES["assertion"]), "r", encoding="utf-8"))
    asserts = assertion.get("assertions") or []
    required_ids = {
        "no_backend_fetch_in_preview_screens", "no_api_story_battle",
        "no_api_battle_simulate", "no_import_from_story_tsx",
        "no_import_from_combat_tsx", "no_async_storage",
        "no_reward_grant_active", "no_public_menu_routing",
        "no_asset_import_or_copy", "no_battle_engine_runtime",
    }
    have_ids = {a.get("id") for a in asserts}
    if not required_ids.issubset(have_ids):
        errors.append(f"ASSERTION_IDS_MISSING: {sorted(required_ids - have_ids)}")
    for a in asserts:
        if a.get("result") != "PASS":
            errors.append(f"ASSERTION_FAIL: {a.get('id')}")
    if assertion.get("overall") != "PASS":
        errors.append("ASSERTION_OVERALL_NOT_PASS")

    marker = json.load(open(os.path.join(ROOT, FILES["marker"]), "r", encoding="utf-8"))
    if marker.get("run_read_only") is not True:
        errors.append("MARKER_NOT_READ_ONLY")
    if marker.get("db_writes") != 0:
        errors.append("MARKER_BAD_DB_WRITES")

    if errors:
        for e in errors: print(e)
        return 1
    print("PROJECT-ALPHA-INTERNAL-QA-RUN-EVIDENCE: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
