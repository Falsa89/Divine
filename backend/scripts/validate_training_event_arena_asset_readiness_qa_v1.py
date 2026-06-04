#!/usr/bin/env python3
# Validator: PROJECT-TRAINING-EVENT-ARENA-ASSET-READINESS-QA
# Pack: MEGA_RELEASE_ACCELERATION_18_v69
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
QA = "data/design/qa/training_event_arena_asset_readiness_qa_matrix_v1.json"
REPORT = "data/design/release_acceleration/alpha_readiness_progress_report_v13.json"

REPORT_EXP = {
    "training_combat_onboarding": "preview_ready_v69",
    "event_arena_alpha_gate": "design_ready_v69",
    "hero_asset_dryrun_manifest": "readiness_ready_v69",
    "story_alpha_slice": "preview_ready_v68",
    "boss_alpha_loop": "preview_ready_v68",
    "tower_alpha_loop": "preview_ready_v68",
    "reward_grant": False,
    "permanent_progress": False,
    "db_writes": 0,
    "battle_engine_runtime": False,
    "real_asset_import": False,
    "file_copy_enabled": False,
    "fake_pass": False,
    "validator_weakening": False,
}

REQ_NEXT = {
    "event_arena_first_alpha_slice_super_pack",
    "hero_asset_staging_import_and_resolver_super_pack_only_after_asset_pack_supplied",
    "first_session_onboarding_super_pack",
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
    if len(cases) < 18:
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
    print("PROJECT-TRAINING-EVENT-ARENA-ASSET-READINESS-QA: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
