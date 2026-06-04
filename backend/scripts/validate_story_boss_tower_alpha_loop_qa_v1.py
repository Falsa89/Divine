#!/usr/bin/env python3
# Validator: PROJECT-STORY-BOSS-TOWER-ALPHA-LOOP-QA
# Pack: MEGA_RELEASE_ACCELERATION_17_v68
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
QA = "data/design/qa/story_boss_tower_alpha_loop_qa_matrix_v1.json"
REPORT = "data/design/release_acceleration/alpha_loop_progress_report_v12.json"


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
    expected = {
        "story_first_playable_alpha_slice": "preview_ready_v68",
        "boss_alpha_loop": "preview_ready_v68",
        "tower_alpha_loop": "preview_ready_v68",
        "reward_grant": False,
        "permanent_progress": False,
        "db_writes": 0,
        "battle_engine_runtime": False,
        "fake_pass": False,
        "validator_weakening": False,
    }
    for k, v in expected.items():
        if rep.get(k) != v:
            errors.append(f"REPORT_BAD: {k}={rep.get(k)!r} expected {v!r}")
    nodes = rep.get("story_alpha_nodes_ready") or []
    for n in ("story_alpha_node_001", "story_alpha_node_002", "story_alpha_node_003"):
        if n not in nodes:
            errors.append(f"REPORT_MISSING_NODE: {n}")
    nxt = rep.get("next_recommended") or []
    for n in (
        "training_combat_onboarding_super_pack",
        "event_arena_alpha_gate_super_pack",
        "hero_asset_dryrun_manifest_super_pack",
    ):
        if n not in nxt:
            errors.append(f"REPORT_MISSING_NEXT: {n}")

    if errors:
        for e in errors:
            print(e)
        return 1

    print("PROJECT-STORY-BOSS-TOWER-ALPHA-LOOP-QA: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
