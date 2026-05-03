#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQ_PATH = ROOT / "data" / "design" / "player_faction_v2_safe_write_qa_requirements.json"

REQUIRED_KEYS = {
    "version",
    "task",
    "title",
    "decision",
    "scope",
    "approved_semantics",
    "required_checks",
    "allowed_user_fields",
    "acceptance_criteria",
}

def main() -> int:
    if not REQ_PATH.exists():
        print(f"FAIL: missing {REQ_PATH}")
        return 2

    data = json.loads(REQ_PATH.read_text(encoding="utf-8"))
    errors = []
    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")

    if data.get("task") != "RM1.24-B":
        errors.append("task must be RM1.24-B")

    decision = data.get("decision", {})
    if decision.get("initial_selection_consumes_token") is not False:
        errors.append("initial_selection_consumes_token must be false")

    allowed = set(data.get("allowed_user_fields", []))
    expected_allowed = {
        "player_faction_v2",
        "player_faction_v2_selected_at",
        "player_faction_v2_changed_at",
        "player_faction_v2_change_tokens",
    }
    if allowed != expected_allowed:
        errors.append(f"allowed_user_fields mismatch: {sorted(allowed)}")

    criteria = data.get("acceptance_criteria", [])
    if not isinstance(criteria, list) or len(criteria) < 5:
        errors.append("acceptance_criteria must contain at least 5 items")

    print("RM1.24-B Player Faction V2 Safe-Write QA Validator")
    print(f"Task: {data.get('task')}")
    print(f"Initial selection consumes token: {decision.get('initial_selection_consumes_token')}")
    print(f"Allowed user fields: {sorted(allowed)}")
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
