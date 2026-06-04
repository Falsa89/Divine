#!/usr/bin/env python3
# Validator: PROJECT-ONBOARDING-MENU-GATE-ALPHA-QA-MATRIX
# Pack: MEGA_RELEASE_ACCELERATION_20_v71
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
QA = "data/design/qa/onboarding_menu_gate_alpha_internal_qa_matrix_v1.json"
REPORT = "data/design/release_acceleration/alpha_readiness_progress_report_v15.json"

REPORT_EXP = {
    "first_session_onboarding": "preview_hardened_v71",
    "alpha_preview_menu_gate": "design_ready_v71",
    "alpha_internal_qa_execution": "ready_v71",
    "alpha_preview_hub": "deeplink_only_v71",
    "hero_asset_staging_import": "deferred_waiting_for_real_asset_pack",
    "event_first_alpha_slice": "preview_ready_v70",
    "arena_first_alpha_slice": "preview_ready_v70",
    "training_combat_onboarding": "preview_ready_v69",
    "story_alpha_slice": "preview_ready_v68",
    "boss_alpha_loop": "preview_ready_v68",
    "tower_alpha_loop": "preview_ready_v68",
    "reward_grant": False,
    "permanent_progress": False,
    "permanent_onboarding_complete": False,
    "account_persistence": False,
    "db_writes": 0,
    "battle_engine_runtime": False,
    "event_currency_enabled": False,
    "arena_ranking_enabled": False,
    "matchmaking_live": False,
    "public_menu_routing_enabled": False,
    "real_asset_import": False,
    "fake_pass": False,
    "validator_weakening": False,
}
REQ_NEXT = {
    "alpha_internal_qa_run_and_bugfix_batch",
    "hero_asset_staging_import_and_resolver_super_pack_only_after_asset_pack_supplied",
    "menu_public_exposure_design_after_QA",
}


def main() -> int:
    errors = []
    for rel in (QA, REPORT):
        if not os.path.isfile(os.path.join(ROOT, rel)):
            errors.append(f"MISSING_FILE: {rel}")
    if errors:
        for e in errors:
            print(e)
        return 1

    qa = json.load(open(os.path.join(ROOT, QA), "r", encoding="utf-8"))
    cases = qa.get("cases") or []
    if len(cases) < 20:
        errors.append(f"QA_TOO_FEW_CASES: {len(cases)}")
    severities = {c.get("severity") for c in cases}
    for sev in ("P0", "P1", "P2", "P3"):
        if sev not in severities:
            errors.append(f"QA_MISSING_SEVERITY: {sev}")
    if qa.get("db_writes") != 0:
        errors.append("QA_BAD_DB_WRITES")

    rep = json.load(open(os.path.join(ROOT, REPORT), "r", encoding="utf-8"))
    for k, v in REPORT_EXP.items():
        if rep.get(k) != v:
            errors.append(f"REPORT_BAD: {k}={rep.get(k)!r} expected {v!r}")
    nxt = set(rep.get("next_recommended") or [])
    if not REQ_NEXT.issubset(nxt):
        errors.append("REPORT_NEXT_MISSING")

    if errors:
        for e in errors:
            print(e)
        return 1
    print("PROJECT-ONBOARDING-MENU-GATE-ALPHA-QA-MATRIX: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
