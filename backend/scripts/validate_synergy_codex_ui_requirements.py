#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQ_PATH = ROOT / "data" / "design" / "synergy_codex_ui_requirements.json"

REQUIRED_TOP_KEYS = {
    "version", "task", "title", "scope", "navigation", "codex_screen",
    "hero_detail_palette", "upgrade_philosophy", "backend", "borea_policy",
    "acceptance_criteria",
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
    sections = data.get("codex_screen", {}).get("sections", [])
    section_ids = {s.get("id") for s in sections if isinstance(s, dict)}
    for required in {"team_synergies_v2", "formation_synergies", "element_synergies", "collection_synergies"}:
        if required not in section_ids:
            errors.append(f"missing codex section: {required}")
    tabs = data.get("hero_detail_palette", {}).get("tabs", [])
    tab_ids = {t.get("id") for t in tabs if isinstance(t, dict)}
    for required in {"in_team", "active", "inactive"}:
        if required not in tab_ids:
            errors.append(f"missing hero detail tab: {required}")
    criteria = data.get("acceptance_criteria", [])
    if not isinstance(criteria, list) or len(criteria) < 5:
        errors.append("acceptance_criteria must contain at least 5 items")

    print("RM1.23-C Synergy Codex UI Requirements Validator")
    print(f"Task: {data.get('task')}")
    print(f"Codex sections: {sorted(section_ids)}")
    print(f"Hero detail tabs: {sorted(tab_ids)}")
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
