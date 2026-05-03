#!/usr/bin/env python3
"""
RM1.22-G-BULK — Validate Placeholder Assignment for Remaining Pending Official Heroes

Read-only validator.
Checks that placeholder assets were copied into canonical hero folders.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "data/design/placeholder_assignment_remaining_manifest.json"

EXPECTED_RUNTIME_DIMS = {
    "runtime/idle_sheet.png": (3840, 768),
    "runtime/attack_sheet.png": (3200, 768),
    "runtime/skill_sheet.png": (3840, 768),
    "runtime/hit_sheet.png": (3200, 768),
    "runtime/death_sheet.png": (3840, 768),
    "combat_base.png": (640, 768),
}


def load_manifest() -> Dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def image_info(path: Path):
    with Image.open(path) as img:
        return img.mode, img.size, img.getchannel("A").getbbox() if img.mode == "RGBA" else True


def main() -> int:
    manifest = load_manifest()
    targets: List[Dict[str, Any]] = manifest["targets"]
    required_files: List[str] = manifest["required_files"]

    issues: List[str] = []
    total_files = 0

    for target in targets:
        hero_id = target["hero_id"]
        profile = target["placeholder_profile"]
        root = ROOT / target["destination_root"]

        if not root.exists():
            issues.append(f"{hero_id}: missing destination root {root.relative_to(ROOT)}")
            continue

        for rel in required_files:
            path = root / rel
            if not path.exists():
                issues.append(f"{hero_id}: missing {rel}")
            else:
                total_files += 1

        status_path = root / "placeholder_status.json"
        if not status_path.exists():
            issues.append(f"{hero_id}: missing placeholder_status.json")
        else:
            status = json.loads(status_path.read_text(encoding="utf-8"))
            if status.get("asset_status") != "placeholder_dev":
                issues.append(f"{hero_id}: placeholder_status asset_status mismatch")
            if status.get("placeholder_profile") != profile:
                issues.append(f"{hero_id}: placeholder_status profile mismatch")
            if status.get("assigned_by") != "RM1.22-G-BULK":
                issues.append(f"{hero_id}: placeholder_status assigned_by mismatch")

        battle_path = root / "runtime/battle_animations.json"
        if battle_path.exists():
            meta = json.loads(battle_path.read_text(encoding="utf-8"))
            if meta.get("heroId") != hero_id:
                issues.append(f"{hero_id}: battle_animations heroId mismatch")
            if meta.get("placeholderProfile") != profile:
                issues.append(f"{hero_id}: battle_animations placeholderProfile mismatch")
            if meta.get("assetStatus") != "placeholder_dev":
                issues.append(f"{hero_id}: battle_animations assetStatus mismatch")
            if meta.get("frameWidth") != 640 or meta.get("frameHeight") != 768:
                issues.append(f"{hero_id}: battle_animations frame size mismatch")

        for rel, expected_size in EXPECTED_RUNTIME_DIMS.items():
            path = root / rel
            if not path.exists():
                continue
            mode, size, bbox = image_info(path)
            if size != expected_size:
                issues.append(f"{hero_id}: {rel} size {size} != {expected_size}")
            if mode != "RGBA":
                issues.append(f"{hero_id}: {rel} mode {mode} != RGBA")
            if bbox is None:
                issues.append(f"{hero_id}: {rel} fully transparent")

    print("=== RM1.22-G-BULK Placeholder Assignment Remaining Validation ===")
    print(f"Targets: {len(targets)}")
    print(f"Required copied files found: {total_files}/{len(targets) * len(required_files)}")
    print(f"Expected status files: {len(targets)}")
    print(f"Issues: {len(issues)}")

    if issues:
        print("\nIssues:")
        for issue in issues[:160]:
            print(f"- {issue}")
        print("\nPLACEHOLDER ASSIGNMENT REMAINING VALIDATION: FAIL")
        return 1

    print("\nPLACEHOLDER ASSIGNMENT REMAINING VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
