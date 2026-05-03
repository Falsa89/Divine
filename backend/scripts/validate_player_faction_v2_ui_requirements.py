#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQ_PATH = ROOT / "data" / "design" / "player_faction_v2_ui_requirements.json"

REQUIRED_TOP_KEYS = {
    "version", "task", "title", "scope", "source_of_truth", "ui",
    "selection_rules", "backend", "borea_policy", "acceptance_criteria",
}

def main() -> int:
    if not REQ_PATH.exists():
        print(f"FAIL: missing {REQ_PATH}")
        return 2
    data = json.loads(REQ_PATH.read_text(encoding="utf-8"))
    errors = []
    missing = REQUIRED_TOP_KEYS - set(data.keys())
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")

    if data.get("task") != "RM1.24-A":
        errors.append("task must be RM1.24-A")

    entry_points = data.get("ui", {}).get("entry_points", [])
    if not isinstance(entry_points, list) or len(entry_points) < 1:
        errors.append("ui.entry_points must contain at least one entry")

    readonly = data.get("backend", {}).get("readonly_endpoints", [])
    if not isinstance(readonly, list) or len(readonly) < 1:
        errors.append("backend.readonly_endpoints must contain at least one endpoint")

    criteria = data.get("acceptance_criteria", [])
    if not isinstance(criteria, list) or len(criteria) < 5:
        errors.append("acceptance_criteria must contain at least 5 items")

    print("RM1.24-A Player Faction V2 UI Requirements Validator")
    print(f"Task: {data.get('task')}")
    print(f"Entry points: {len(entry_points) if isinstance(entry_points, list) else 0}")
    print(f"Read-only endpoints: {readonly}")
    print(f"Acceptance criteria: {len(criteria) if isinstance(criteria, list) else 0}")

    if errors:
        print("\nFAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("\nPASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
