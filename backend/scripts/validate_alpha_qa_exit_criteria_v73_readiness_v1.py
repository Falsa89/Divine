#!/usr/bin/env python3
# Validator: PROJECT-ALPHA-QA-EXIT-CRITERIA-v73-READINESS
# Pack: MEGA_RELEASE_ACCELERATION_21_v72
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "criteria": "data/design/qa/alpha_internal_qa_exit_criteria_v1.json",
    "readiness": "data/design/release_acceleration/v72_to_v73_readiness_report_v1.json",
    "marker": "data/design/qa/alpha_qa_exit_criteria_marker_v1.json",
    "report": "data/design/release_acceleration/alpha_readiness_progress_report_v16.json",
    "matrix": "data/design/qa/alpha_internal_qa_run_bugfix_menu_design_matrix_v1.json",
}
CRITERIA_REQUIRED = {
    "no_p0_open", "no_p1_open_or_waiver", "no_guardrail_violation",
    "no_db_write", "no_reward_grant", "no_permanent_progress",
    "no_account_persistence", "no_public_menu_exposure",
    "ts_clean_on_modified_screens", "master_suite_zero_required_fail",
    "md5_invariants_unchanged", "qa_evidence_complete",
}
REPORT_EXP = {
    "alpha_internal_qa_run": "completed_v72",
    "alpha_bug_backlog": "ready_v72",
    "alpha_bugfix_batch": "applied_or_deferred_v72",
    "menu_public_exposure_design": "design_ready_v72",
    "public_menu_exposure": False,
    "first_session_onboarding": "preview_hardened_v71",
    "alpha_preview_hub": "deeplink_only_v71",
    "hero_asset_staging_import": "deferred_waiting_for_real_asset_pack",
    "reward_grant": False,
    "permanent_progress": False,
    "account_persistence": False,
    "db_writes": 0,
    "battle_engine_runtime": False,
    "real_asset_import": False,
    "fake_pass": False,
    "validator_weakening": False,
}
REQ_NEXT = {
    "alpha_bugfix_batch_2_if_findings",
    "menu_preview_gate_public_design_review_if_QA_clean",
    "hero_asset_staging_import_and_resolver_super_pack_only_after_asset_pack_supplied",
    "closed_alpha_testing_plan",
}


def main() -> int:
    errors = []
    for k, rel in FILES.items():
        if not os.path.isfile(os.path.join(ROOT, rel)):
            errors.append(f"MISSING_FILE: {k}={rel}")
    if errors:
        for e in errors: print(e)
        return 1

    crit = json.load(open(os.path.join(ROOT, FILES["criteria"]), "r", encoding="utf-8"))
    crit_ids = {c.get("id") for c in (crit.get("criteria") or [])}
    if not CRITERIA_REQUIRED.issubset(crit_ids):
        errors.append(f"CRITERIA_MISSING: {sorted(CRITERIA_REQUIRED - crit_ids)}")
    if crit.get("overall_exit_pass") is not True:
        errors.append("CRITERIA_OVERALL_NOT_PASS")
    for c in crit.get("criteria") or []:
        if c.get("required") and not c.get("satisfied"):
            errors.append(f"CRITERIA_NOT_SATISFIED: {c.get('id')}")

    readiness = json.load(open(os.path.join(ROOT, FILES["readiness"]), "r", encoding="utf-8"))
    if readiness.get("qa_clean") is not True:
        errors.append("READINESS_NOT_CLEAN")
    if readiness.get("public_menu_exposure_enabled") is not False:
        errors.append("READINESS_PUBLIC_MENU_ENABLED")
    if readiness.get("hero_asset_staging_import_status") != "deferred_waiting_for_real_asset_pack":
        errors.append("READINESS_ASSET_NOT_DEFERRED")

    rep = json.load(open(os.path.join(ROOT, FILES["report"]), "r", encoding="utf-8"))
    for k, v in REPORT_EXP.items():
        if rep.get(k) != v:
            errors.append(f"REPORT_BAD: {k}={rep.get(k)!r} expected {v!r}")
    nxt = set(rep.get("next_recommended") or [])
    if not REQ_NEXT.issubset(nxt):
        errors.append(f"REPORT_NEXT_MISSING: {sorted(REQ_NEXT - nxt)}")

    qa = json.load(open(os.path.join(ROOT, FILES["matrix"]), "r", encoding="utf-8"))
    if qa.get("db_writes") != 0:
        errors.append("QA_BAD_DB_WRITES")
    cases = qa.get("cases") or []
    if len(cases) < 15:
        errors.append(f"QA_TOO_FEW_CASES: {len(cases)}")
    severities = {c.get("severity") for c in cases}
    for sev in ("P0", "P1", "P2", "P3"):
        if sev not in severities:
            errors.append(f"QA_MISSING_SEVERITY: {sev}")

    if errors:
        for e in errors: print(e)
        return 1
    print("PROJECT-ALPHA-QA-EXIT-CRITERIA-v73-READINESS: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
