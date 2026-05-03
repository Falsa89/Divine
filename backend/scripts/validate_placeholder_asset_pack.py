#!/usr/bin/env python3
"""
RM1.22-B — Validate Placeholder Asset Pack Standard

Read-only validator for shared placeholder asset profiles.

No DB access.
No runtime changes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ASSET_ROOT = ROOT / "frontend/assets/placeholders/heroes"
MANIFEST_PATH = ASSET_ROOT / "placeholder_asset_pack_manifest.json"

EXPECTED_PROFILES = [
    "tank_standard_v1",
    "dps_melee_standard_v1",
    "dps_ranged_standard_v1",
    "mage_aoe_standard_v1",
    "assassin_burst_standard_v1",
    "support_buffer_standard_v1",
    "healer_standard_v1",
    "control_debuff_standard_v1",
    "hybrid_special_standard_v1",
]

REQUIRED_FILES = [
    "splash.jpg",
    "splash.png",
    "transparent.png",
    "card.png",
    "detail.png",
    "fullscreen.png",
    "combat_base.png",
    "runtime/idle_sheet.png",
    "runtime/attack_sheet.png",
    "runtime/skill_sheet.png",
    "runtime/hit_sheet.png",
    "runtime/death_sheet.png",
    "runtime/battle_animations.json",
    "README_PLACEHOLDER.md",
]


def image_info(path: Path):
    with Image.open(path) as img:
        return img.mode, img.size


def main() -> int:
    issues: List[str] = []

    if not MANIFEST_PATH.exists():
        issues.append(f"Missing manifest: {MANIFEST_PATH.relative_to(ROOT)}")
        manifest = {}
    else:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    profiles = manifest.get("profiles", {}) if isinstance(manifest, dict) else {}
    if set(profiles.keys()) != set(EXPECTED_PROFILES):
        issues.append(f"Profile set mismatch expected={EXPECTED_PROFILES} found={sorted(profiles.keys())}")

    for profile in EXPECTED_PROFILES:
        root = ASSET_ROOT / profile
        if not root.exists():
            issues.append(f"{profile}: missing folder")
            continue

        for rel in REQUIRED_FILES:
            path = root / rel
            if not path.exists():
                issues.append(f"{profile}: missing {rel}")

        # Validate key image dimensions / transparency expectations.
        runtime_json = root / "runtime/battle_animations.json"
        if runtime_json.exists():
            data = json.loads(runtime_json.read_text(encoding="utf-8"))
            if data.get("frameWidth") != 640 or data.get("frameHeight") != 768:
                issues.append(f"{profile}: runtime frame size mismatch")
            anims = data.get("animations", {})
            for state in ["idle", "attack", "skill", "hit", "death"]:
                if state not in anims:
                    issues.append(f"{profile}: missing animation metadata {state}")

        expected_dims = {
            "runtime/idle_sheet.png": (3840, 768),
            "runtime/attack_sheet.png": (3200, 768),
            "runtime/skill_sheet.png": (3840, 768),
            "runtime/hit_sheet.png": (3200, 768),
            "runtime/death_sheet.png": (3840, 768),
            "combat_base.png": (640, 768),
        }

        for rel, expected_size in expected_dims.items():
            path = root / rel
            if not path.exists():
                continue
            mode, size = image_info(path)
            if size != expected_size:
                issues.append(f"{profile}: {rel} size {size} != {expected_size}")
            if mode != "RGBA":
                issues.append(f"{profile}: {rel} mode {mode} != RGBA")
            with Image.open(path) as img:
                alpha = img.getchannel("A")
                if alpha.getbbox() is None:
                    issues.append(f"{profile}: {rel} appears fully transparent")

    print("=== RM1.22-B Placeholder Asset Pack Validation ===")
    print(f"Expected profiles: {len(EXPECTED_PROFILES)}")
    print(f"Manifest profiles: {len(profiles)}")
    print(f"Issues: {len(issues)}")

    if issues:
        print("\nIssues:")
        for issue in issues[:100]:
            print(f"- {issue}")
        print("\nPLACEHOLDER ASSET PACK: FAIL")
        return 1

    print("\nPLACEHOLDER ASSET PACK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
