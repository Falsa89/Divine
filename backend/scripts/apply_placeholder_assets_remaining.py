#!/usr/bin/env python3
"""
RM1.22-G-BULK — Apply Placeholder Assets to Remaining Pending Official Hero Folders

Targets:
- 79 remaining pending official heroes
- native 3★/4★/5★/6★ + Borea extra
- excludes already-active custom heroes: greek_hoplite, norse_berserker

Default is DRY-RUN.
Use --apply to write files.

Safety:
- no DB access;
- no runtime code changes;
- no show_in_* changes;
- no hero activation;
- no overwrites unless --force is explicitly used.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "data/design/placeholder_assignment_remaining_manifest.json"
REPORTS_DIR = ROOT / "backend/reports"

PROTECTED_EXISTING_HERO_IDS = {"greek_hoplite", "norse_berserker"}


def load_manifest() -> Dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def patch_battle_metadata(path: Path, hero_id: str, profile: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["heroId"] = hero_id
    data["placeholderProfile"] = profile
    data["assetStatus"] = "placeholder_dev"
    data["version"] = max(int(data.get("version", 1)), 1)
    data["source"] = "RM1.22-G-BULK placeholder assignment"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_status_file(dest_root: Path, target: Dict[str, Any]) -> None:
    status = {
        "hero_id": target["hero_id"],
        "placeholder_profile": target["placeholder_profile"],
        "asset_status": "placeholder_dev",
        "final_art_ready": False,
        "assigned_by": "RM1.22-G-BULK",
        "assigned_at": datetime.now(timezone.utc).isoformat(),
        "note": "Development placeholder assets only. Do not mark as final."
    }
    (dest_root / "placeholder_status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Actually copy files. Default is dry-run.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting existing destination files. Avoid unless explicitly requested.")
    args = parser.parse_args()

    manifest = load_manifest()
    required_files: List[str] = manifest["required_files"]
    targets: List[Dict[str, Any]] = manifest["targets"]

    planned = []
    issues = []

    for target in targets:
        hero_id = target["hero_id"]
        profile = target["placeholder_profile"]

        if hero_id in PROTECTED_EXISTING_HERO_IDS and not args.force:
            issues.append(f"{hero_id}: protected existing hero folder would require --force; refusing overwrite")
            continue

        src_root = ROOT / target["source_root"]
        dest_root = ROOT / target["destination_root"]

        if not src_root.exists():
            issues.append(f"{hero_id}: missing source root {src_root.relative_to(ROOT)}")
            continue

        for rel in required_files:
            src = src_root / rel
            dest = dest_root / rel
            if not src.exists():
                issues.append(f"{hero_id}: missing source file {src.relative_to(ROOT)}")
                continue
            if dest.exists() and not args.force:
                issues.append(f"{hero_id}: destination exists, refusing overwrite without --force: {dest.relative_to(ROOT)}")
                continue
            planned.append({
                "hero_id": hero_id,
                "profile": profile,
                "src": str(src.relative_to(ROOT)),
                "dest": str(dest.relative_to(ROOT)),
            })

    print("=== RM1.22-G-BULK Placeholder Assignment Remaining ===")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"Targets: {len(targets)}")
    print(f"Required files per hero: {len(required_files)}")
    print(f"Planned file copies: {len(planned)}")
    print(f"Issues: {len(issues)}")

    if issues:
        print("\nIssues:")
        for issue in issues[:160]:
            print(f"- {issue}")
        print("\nPLACEHOLDER ASSIGNMENT REMAINING: FAIL")
        return 1

    if args.apply:
        for item in planned:
            src = ROOT / item["src"]
            dest = ROOT / item["dest"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

        for target in targets:
            dest_root = ROOT / target["destination_root"]
            battle_json = dest_root / "runtime/battle_animations.json"
            patch_battle_metadata(battle_json, target["hero_id"], target["placeholder_profile"])
            write_status_file(dest_root, target)

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        report_path = REPORTS_DIR / f"placeholder_assignment_remaining_APPLIED_{ts}.json"
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "task": "RM1.22-G-BULK",
            "mode": "apply",
            "targets": len(targets),
            "files_copied": len(planned),
            "placeholder_status_files_written": len(targets),
            "db_writes": False,
            "runtime_code_changes": False,
            "show_in_flags_changed": False,
            "heroes_activated": False,
            "items": planned,
        }
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nApplied. Report: {report_path.relative_to(ROOT)}")
    else:
        print("\nDry-run only. Re-run with --apply to copy files.")

    print("\nPLACEHOLDER ASSIGNMENT REMAINING: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
