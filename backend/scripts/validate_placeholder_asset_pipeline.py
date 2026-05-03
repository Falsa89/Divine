#!/usr/bin/env python3
"""
RM1.22-A — Validate Placeholder Asset & Contract Readiness Pipeline

Read-only validator for:
- data/design/placeholder_asset_profiles.json
- data/design/official_hero_asset_readiness_manifest.json
- data/design/heroes_master.json

No DB access.
No runtime changes.
No file writes except optional console output.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]

PROFILES_PATH = ROOT / "data/design/placeholder_asset_profiles.json"
MANIFEST_PATH = ROOT / "data/design/official_hero_asset_readiness_manifest.json"
HEROES_MASTER_PATH = ROOT / "data/design/heroes_master.json"

EXPECTED_TOTAL = 101


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_role(role: str) -> str:
    return role.lower().replace("/", " ").replace("-", " ").replace("  ", " ").strip().replace(" ", "_")


def main() -> int:
    issues: List[str] = []

    profiles_doc = load_json(PROFILES_PATH)
    manifest_doc = load_json(MANIFEST_PATH)
    heroes_master = load_json(HEROES_MASTER_PATH)

    profiles = profiles_doc.get("profiles")
    manifest = manifest_doc.get("heroes")
    master_heroes = heroes_master.get("heroes")

    if not isinstance(profiles, dict):
        issues.append("placeholder_asset_profiles.json missing profiles object")
        profiles = {}
    if not isinstance(manifest, list):
        issues.append("official_hero_asset_readiness_manifest.json missing heroes list")
        manifest = []
    if not isinstance(master_heroes, list):
        issues.append("heroes_master.json missing heroes list")
        master_heroes = []

    master_by_id = {h.get("id"): h for h in master_heroes if isinstance(h, dict) and h.get("id")}
    manifest_by_id = {h.get("hero_id"): h for h in manifest if isinstance(h, dict) and h.get("hero_id")}

    if len(master_by_id) != EXPECTED_TOTAL:
        issues.append(f"heroes_master expected {EXPECTED_TOTAL}, found {len(master_by_id)}")
    if len(manifest_by_id) != EXPECTED_TOTAL:
        issues.append(f"manifest expected {EXPECTED_TOTAL}, found {len(manifest_by_id)}")

    missing = sorted(set(master_by_id) - set(manifest_by_id))
    unknown = sorted(set(manifest_by_id) - set(master_by_id))
    duplicates = [item for item, count in Counter([h.get("hero_id") for h in manifest if isinstance(h, dict)]).items() if item and count > 1]

    if missing:
        issues.append(f"missing manifest entries: {missing}")
    if unknown:
        issues.append(f"unknown manifest entries: {unknown}")
    if duplicates:
        issues.append(f"duplicate manifest entries: {duplicates}")

    for hero_id, entry in manifest_by_id.items():
        master = master_by_id.get(hero_id)
        if not master:
            continue
        role = normalize_role(str(master.get("role", "")))
        if entry.get("role") != role:
            issues.append(f"{hero_id}: role mismatch manifest={entry.get('role')} master={role}")

        if entry.get("native_rarity") != master.get("native_rarity"):
            issues.append(f"{hero_id}: native_rarity mismatch")
        if entry.get("max_stars") != master.get("max_stars"):
            issues.append(f"{hero_id}: max_stars mismatch")
        if entry.get("release_group") != master.get("release_group"):
            issues.append(f"{hero_id}: release_group mismatch")

        profile = entry.get("placeholder_profile")
        if profile not in profiles:
            issues.append(f"{hero_id}: unknown placeholder_profile {profile}")

        paths = entry.get("canonical_paths", {})
        required_path_keys = ["hero_root", "splash", "transparent", "combat_base", "runtime_metadata", "runtime_sheets"]
        for key in required_path_keys:
            if key not in paths:
                issues.append(f"{hero_id}: missing canonical_paths.{key}")
        runtime_sheets = paths.get("runtime_sheets", {})
        if isinstance(runtime_sheets, dict):
            for state in ["idle", "attack", "skill", "hit", "death"]:
                if state not in runtime_sheets:
                    issues.append(f"{hero_id}: missing runtime_sheets.{state}")
        else:
            issues.append(f"{hero_id}: runtime_sheets is not object")

        gates = entry.get("activation_gates", {})
        required_gates = [
            "placeholder_assets_copied",
            "asset_contract_created",
            "ui_contract_created",
            "battle_contract_created",
            "preload_assets_registered",
            "combat_qa_lab_passed",
            "mobile_ui_passed",
            "ready_for_catalog",
            "ready_for_summon",
            "ready_for_starter_pool",
        ]
        for gate in required_gates:
            if gate not in gates:
                issues.append(f"{hero_id}: missing activation_gates.{gate}")

    coverage = manifest_doc.get("coverage", {})
    if coverage.get("entries") != EXPECTED_TOTAL:
        issues.append(f"manifest coverage.entries expected {EXPECTED_TOTAL}, found {coverage.get('entries')}")

    print("=== RM1.22-A Placeholder Asset Pipeline Validation ===")
    print(f"Profiles: {len(profiles)}")
    print(f"Heroes master: {len(master_by_id)}")
    print(f"Manifest entries: {len(manifest_by_id)}")
    print(f"Missing: {len(missing)} | Unknown: {len(unknown)} | Duplicates: {len(duplicates)}")
    print(f"Issues: {len(issues)}")

    if issues:
        print("\nIssues:")
        for issue in issues[:100]:
            print(f"- {issue}")
        print("\nPLACEHOLDER ASSET PIPELINE: FAIL")
        return 1

    profile_counts = Counter(entry.get("placeholder_profile") for entry in manifest_by_id.values())
    print("\nProfile counts:")
    for profile, count in sorted(profile_counts.items()):
        print(f"- {profile}: {count}")

    print("\nPLACEHOLDER ASSET PIPELINE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
