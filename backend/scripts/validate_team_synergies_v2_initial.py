#!/usr/bin/env python3
"""
RM1.23-B validator for data/design/team_synergies_v2_initial_10.json.

Read-only.
Validates:
- JSON syntax
- unique IDs
- no greek_borea / legacy borea
- canonical hero IDs exist in backend/data/character_bible.py when available
- basic schema fields
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / "data" / "design" / "team_synergies_v2_initial_10.json"

REQUIRED_TOP_FIELDS = {
    "id",
    "version",
    "type",
    "display_name",
    "required_hero_ids",
    "min_required",
    "max_members",
    "activation_scope",
    "effects",
    "is_enabled",
}

FORBIDDEN_HERO_IDS = {"greek_borea", "borea"}


def load_character_bible_ids() -> set[str]:
    sys.path.insert(0, str(ROOT / "backend"))
    try:
        from data.character_bible import CHARACTER_BIBLE_BY_ID  # type: ignore
        return set(CHARACTER_BIBLE_BY_ID.keys())
    except Exception as exc:
        print(f"WARNING: Could not import Character Bible; ID existence check skipped: {exc}")
        return set()


def main() -> int:
    if not JSON_PATH.exists():
        print(f"FAIL: Missing file: {JSON_PATH}")
        return 2

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    synergies = data.get("synergies", [])
    if not isinstance(synergies, list):
        print("FAIL: `synergies` must be a list")
        return 2

    bible_ids = load_character_bible_ids()
    errors: list[str] = []
    seen_ids: set[str] = set()
    referenced_ids: set[str] = set()

    for idx, syn in enumerate(synergies):
        if not isinstance(syn, dict):
            errors.append(f"entry[{idx}] is not an object")
            continue

        sid = syn.get("id")
        if not sid:
            errors.append(f"entry[{idx}] missing id")
        elif sid in seen_ids:
            errors.append(f"duplicate synergy id: {sid}")
        else:
            seen_ids.add(sid)

        missing = REQUIRED_TOP_FIELDS - set(syn.keys())
        if missing:
            errors.append(f"{sid}: missing required fields {sorted(missing)}")

        if syn.get("type") != "team_synergy":
            errors.append(f"{sid}: type must be team_synergy")

        req = syn.get("required_hero_ids", [])
        if not isinstance(req, list) or not req:
            errors.append(f"{sid}: required_hero_ids must be non-empty list")
            continue

        for hid in req:
            if hid in FORBIDDEN_HERO_IDS:
                errors.append(f"{sid}: forbidden hero id referenced: {hid}")
            referenced_ids.add(hid)
            if bible_ids and hid not in bible_ids:
                errors.append(f"{sid}: unknown Character Bible hero id: {hid}")

        effects = syn.get("effects", [])
        if not isinstance(effects, list) or not effects:
            errors.append(f"{sid}: effects must be non-empty list")
        else:
            for eidx, eff in enumerate(effects):
                for field in ("stat", "mode", "value", "target"):
                    if field not in eff:
                        errors.append(f"{sid}: effect[{eidx}] missing {field}")

    if len(synergies) != 10:
        errors.append(f"expected 10 synergies, found {len(synergies)}")

    print("RM1.23-B Team Synergies V2 Initial Validator")
    print(f"Synergies: {len(synergies)}")
    print(f"Unique synergy IDs: {len(seen_ids)}")
    print(f"Referenced hero IDs: {len(referenced_ids)}")
    print(f"Character Bible check: {'enabled' if bible_ids else 'skipped'}")
    print(f"Forbidden IDs referenced: {sorted(referenced_ids & FORBIDDEN_HERO_IDS)}")

    if errors:
        print("\nFAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("\nPASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
