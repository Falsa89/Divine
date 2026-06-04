#!/usr/bin/env python3
# Validator: PROJECT-STORY-FIRST-PLAYABLE-ALPHA-SLICE-CONTRACT
# Pack: MEGA_RELEASE_ACCELERATION_17_v68
# Controlli reali su JSON contracts; OPTIONAL tier.
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

REQUIRED = [
    "data/design/story/story_first_playable_alpha_slice_contract_v1.json",
    "data/design/story/story_alpha_chapter_001_sequence_contract_v1.json",
    "data/design/story/story_alpha_slice_forbidden_scope_v1.json",
]

EXPECTED_CONTRACT = {
    "alpha_slice_preview": True,
    "authoritative_runtime": False,
    "backend_used": False,
    "battle_engine_runtime_used": False,
    "story_tsx_changed": False,
    "combat_tsx_changed": False,
    "db_writes": 0,
    "reward_grant_enabled": False,
    "permanent_progress_enabled": False,
    "result_authoritative": False,
    "local_preview_adapter": True,
    "chapter_id": "chapter_alpha",
}
EXPECTED_NODES = [
    "story_alpha_node_001",
    "story_alpha_node_002",
    "story_alpha_node_003",
]


def main() -> int:
    errors = []
    for rel in REQUIRED:
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p):
            errors.append(f"MISSING_FILE: {rel}")
    if errors:
        for e in errors:
            print(e)
        return 1

    contract = json.load(open(os.path.join(ROOT, REQUIRED[0]), "r", encoding="utf-8"))
    for k, v in EXPECTED_CONTRACT.items():
        if contract.get(k) != v:
            errors.append(f"CONTRACT_BAD_VALUE: {k}={contract.get(k)!r} expected {v!r}")
    if contract.get("node_sequence") != EXPECTED_NODES:
        errors.append("CONTRACT_BAD_NODE_SEQUENCE")

    sequence = json.load(open(os.path.join(ROOT, REQUIRED[1]), "r", encoding="utf-8"))
    if sequence.get("chapter_id") != "chapter_alpha":
        errors.append("SEQUENCE_BAD_CHAPTER_ID")
    if sequence.get("db_writes") != 0:
        errors.append("SEQUENCE_BAD_DB_WRITES")
    if not sequence.get("clear_sequence_preview_only"):
        errors.append("SEQUENCE_NOT_PREVIEW_ONLY")

    forbidden = json.load(open(os.path.join(ROOT, REQUIRED[2]), "r", encoding="utf-8"))
    for must in [
        "db_writes",
        "reward_grant",
        "permanent_progress",
        "import_from_story_tsx",
        "import_from_combat_tsx",
        "battle_engine_runtime",
    ]:
        if must not in (forbidden.get("forbidden") or []):
            errors.append(f"FORBIDDEN_MISSING: {must}")

    if errors:
        for e in errors:
            print(e)
        return 1

    print("PROJECT-STORY-FIRST-PLAYABLE-ALPHA-SLICE-CONTRACT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
