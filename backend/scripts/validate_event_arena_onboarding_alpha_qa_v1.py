#!/usr/bin/env python3
# Validator: PROJECT-EVENT-ARENA-ONBOARDING-ALPHA-QA
# Pack: MEGA_RELEASE_ACCELERATION_19_v70
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
QA = "data/design/qa/event_arena_onboarding_alpha_slice_qa_matrix_v1.json"
REPORT = "data/design/release_acceleration/alpha_readiness_progress_report_v14.json"

REPORT_EXP = {
    "event_first_alpha_slice": "preview_ready_v70",
    "arena_first_alpha_slice": "preview_ready_v70",
    "first_session_onboarding": "preview_ready_v70",
    "hero_asset_staging_import": "deferred_waiting_for_real_asset_pack",
    "training_combat_onboarding": "preview_ready_v69",
    "event_arena_alpha_gate": "design_ready_v69",
    "story_alpha_slice": "preview_ready_v68",
    "boss_alpha_loop": "preview_ready_v68",
    "tower_alpha_loop": "preview_ready_v68",
    "reward_grant": False,
    "permanent_progress": False,
    "permanent_onboarding_complete": False,
    "db_writes": 0,
    "battle_engine_runtime": False,
    "event_currency_enabled": False,
    "arena_ranking_enabled": False,
    "matchmaking_live": False,
    "real_asset_import": False,
    "file_copy_enabled": False,
    "fake_pass": False,
    "validator_weakening": False,
}
REQ_NEXT = {
    "first_session_onboarding_hardening_or_menu_preview_gate",
    "hero_asset_staging_import_and_resolver_super_pack_only_after_asset_pack_supplied",
    "alpha_internal_qa_execution_super_pack",
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
    print("PROJECT-EVENT-ARENA-ONBOARDING-ALPHA-QA: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
