#!/usr/bin/env python3
import json
from pathlib import Path

REQ_PATH = Path("/app/data/design/hero_skill_kits/hero_skill_kits_browser_ui_requirements_v1.json")

def main():
    if not REQ_PATH.exists():
        raise SystemExit(f"ERROR: missing requirements file: {REQ_PATH}")

    data = json.loads(REQ_PATH.read_text(encoding="utf-8"))

    assert data.get("task_id") == "RM1.26-D", "task_id must be RM1.26-D"
    assert data.get("title") == "Hero Skill Kit Browser UI Extension", "unexpected title"

    endpoints = data.get("source_endpoints", [])
    assert len(endpoints) == 5, f"expected 5 source endpoints, got {len(endpoints)}"
    assert all(ep.startswith("GET ") for ep in endpoints), "all endpoints must be GET"

    sections = data.get("ui_sections", [])
    section_ids = {s.get("id") for s in sections}
    expected_sections = {"summary", "five_star", "six_star", "by_hero", "schema"}
    missing = expected_sections - section_ids
    assert not missing, f"missing ui sections: {sorted(missing)}"

    expected_counts = data.get("expected_counts", {})
    assert expected_counts.get("five_star_entries_count") == 20, "expected 20 5★ entries"
    assert expected_counts.get("six_star_launch_base_entries_count") == 12, "expected 12 launch_base 6★"
    assert expected_counts.get("six_star_extra_premium_entries_count") == 1, "expected 1 extra premium 6★"
    assert expected_counts.get("total_catalog_entries_count") == 33, "expected total 33 catalog entries"

    flags = data.get("runtime_flags_expected", {})
    for key in ["runtime_attached", "battle_runtime_attached", "ui_runtime_attached", "hp_bar_runtime_attached", "balance_values_finalized"]:
        assert flags.get(key) is False, f"{key} must be false"
    assert flags.get("do_not_treat_as_live_kit") is True, "do_not_treat_as_live_kit must be true"

    absolute_rules = data.get("absolute_rules", [])
    assert len(absolute_rules) >= 15, "expected at least 15 absolute rules"
    forbidden = " ".join(absolute_rules).lower()
    for needle in ["no db writes", "no migrations", "no battle_engine.py changes", "do not activate borea"]:
        assert needle in forbidden, f"missing safety rule containing: {needle}"

    criteria = data.get("acceptance_criteria", [])
    assert len(criteria) >= 12, "expected at least 12 acceptance criteria"

    print("PASS: RM1.26-D hero skill kit browser UI requirements validated")
    print(f"- endpoints: {len(endpoints)}")
    print(f"- sections: {len(sections)}")
    print(f"- expected total catalog entries: {expected_counts.get('total_catalog_entries_count')}")
    print(f"- absolute rules: {len(absolute_rules)}")
    print(f"- acceptance criteria: {len(criteria)}")

if __name__ == "__main__":
    main()
