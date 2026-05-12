#!/usr/bin/env python3
"""Validate RM1.25-D Skill/Status/VFX catalog browser UI requirements."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQ_PATH = ROOT / "data" / "design" / "skill_status_vfx_browser_ui_requirements.json"

EXPECTED_ENDPOINTS = {
    "/api/skill-status-vfx/catalogs/summary",
    "/api/skill-status-vfx/catalogs/skill-progression",
    "/api/skill-status-vfx/catalogs/status-effects",
    "/api/skill-status-vfx/catalogs/status-icons",
    "/api/skill-status-vfx/catalogs/vfx",
    "/api/skill-status-vfx/catalogs/skill-examples",
}
EXPECTED_SECTIONS = {
    "summary",
    "skill_progression",
    "status_effects",
    "status_icons",
    "vfx",
    "skill_examples",
}
REQUIRED_RULE_SNIPPETS = [
    "No DB writes",
    "No battle_engine.py changes",
    "No live skill activation",
    "No live status activation",
    "No live VFX activation",
    "No status icon HP bar activation",
    "No frontend HP bar changes",
    "Do not activate Borea",
    "Do not connect catalogs to combat runtime",
]


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def main() -> None:
    if not REQ_PATH.exists():
        fail(f"missing requirements file: {REQ_PATH}")
    data = json.loads(REQ_PATH.read_text(encoding="utf-8"))

    if data.get("task_id") != "RM1.25-D":
        fail("task_id must be RM1.25-D")
    if data.get("mode") != "read_only_ui":
        fail("mode must be read_only_ui")

    endpoints = set(data.get("source_api_endpoints", []))
    if endpoints != EXPECTED_ENDPOINTS:
        fail(f"unexpected endpoints: {sorted(endpoints ^ EXPECTED_ENDPOINTS)}")

    sections = {s.get("id") for s in data.get("screen_sections", [])}
    if sections != EXPECTED_SECTIONS:
        fail(f"unexpected sections: {sorted(sections ^ EXPECTED_SECTIONS)}")

    frontend = data.get("frontend_target", {})
    if frontend.get("new_screen") != "/app/frontend/app/skill-status-vfx-catalogs.tsx":
        fail("frontend new_screen path mismatch")
    if frontend.get("route") != "/skill-status-vfx-catalogs":
        fail("frontend route mismatch")

    ui = data.get("ui_requirements", {})
    if not ui.get("no_post_put_delete"):
        fail("ui must explicitly prohibit non-GET write calls")
    if "endpoint" not in str(ui.get("no_runtime_json_import_frontend", "")).lower():
        fail("frontend must consume endpoints rather than static JSON imports")

    rules = data.get("absolute_rules", [])
    for snippet in REQUIRED_RULE_SNIPPETS:
        if snippet not in rules:
            fail(f"missing absolute rule: {snippet}")

    flags = data.get("expected_safety_flags", {})
    for key in ("battle_runtime_attached", "ui_runtime_attached", "vfx_runtime_attached"):
        if flags.get(key) is not False:
            fail(f"{key} must be false")

    acceptance = data.get("acceptance_criteria", [])
    if len(acceptance) < 12:
        fail("expected at least 12 acceptance criteria")

    print("PASS: RM1.25-D catalog browser UI requirements validated")
    print(f"- endpoints: {len(endpoints)}")
    print(f"- sections: {len(sections)}")
    print(f"- absolute rules: {len(rules)}")
    print(f"- acceptance criteria: {len(acceptance)}")


if __name__ == "__main__":
    main()
