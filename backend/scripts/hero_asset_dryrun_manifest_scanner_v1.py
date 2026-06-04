#!/usr/bin/env python3
# Hero Asset Dry-run Manifest Scanner v1
# Pack: MEGA_RELEASE_ACCELERATION_18_v69
#
# Read-only scanner. Non scrive su DB. Non copia file. Non importa asset.
# Non modifica Character Bible. Non tocca asset runtime resolver.
# Se asset_source_path e' assente o non valido, produce un readiness report
# placeholder con scan_executed=false.
#
# Uso:
#   python3 backend/scripts/hero_asset_dryrun_manifest_scanner_v1.py [--path /path/to/assets]
import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List

REQUIRED_FILES = [
    "splash.png",
    "no_background.png",
    "combat_base.png",
    "idle.png",
    "attack.png",
    "skill.png",
    "hit.png",
    "death.png",
]
OPTIONAL_FILES = ["chibi_home.png"]
HERO_ID_RE = re.compile(r"^[a-z0-9_]+$")


def build_placeholder_report() -> Dict[str, Any]:
    return {
        "report_version": "hero_asset_dryrun_manifest_scanner_v1",
        "scan_executed": False,
        "asset_source_path": None,
        "heroes_scanned": 0,
        "ready_heroes": [],
        "missing_assets_by_hero": {},
        "naming_issues_list": [],
        "duplicate_hero_id_warnings": [],
        "db_writes": 0,
        "real_asset_import": False,
        "file_copy_enabled": False,
        "asset_runtime_resolver_changed": False,
        "character_bible_changed": False,
        "notes": "Placeholder: nessun asset source path fornito. Scanner read-only.",
    }


def scan(path: str) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "report_version": "hero_asset_dryrun_manifest_scanner_v1",
        "scan_executed": True,
        "asset_source_path": path,
        "heroes_scanned": 0,
        "ready_heroes": [],
        "missing_assets_by_hero": {},
        "naming_issues_list": [],
        "duplicate_hero_id_warnings": [],
        "db_writes": 0,
        "real_asset_import": False,
        "file_copy_enabled": False,
        "asset_runtime_resolver_changed": False,
        "character_bible_changed": False,
    }
    if not os.path.isdir(path):
        report["scan_executed"] = False
        report["notes"] = f"Path non e' una directory valida: {path}"
        return report

    seen_lower: Dict[str, List[str]] = {}
    entries = [e for e in os.listdir(path) if os.path.isdir(os.path.join(path, e))]
    for hero_id in sorted(entries):
        report["heroes_scanned"] += 1
        lower = hero_id.lower()
        seen_lower.setdefault(lower, []).append(hero_id)
        if not HERO_ID_RE.match(hero_id):
            report["naming_issues_list"].append({
                "hero_id": hero_id,
                "issue": "hero_id non conforme al pattern ^[a-z0-9_]+$",
            })
        hero_dir = os.path.join(path, hero_id)
        files = set(os.listdir(hero_dir))
        missing: List[str] = [f for f in REQUIRED_FILES if f not in files]
        if missing:
            report["missing_assets_by_hero"][hero_id] = missing
        else:
            report["ready_heroes"].append(hero_id)

    for lower, ids in seen_lower.items():
        if len(ids) > 1:
            report["duplicate_hero_id_warnings"].append({
                "lowered_id": lower,
                "duplicates": ids,
            })

    report["notes"] = "Dry-run completato. Nessun import, nessuna copia, nessuna mutazione."
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Hero asset dry-run manifest scanner v1 (read-only)")
    parser.add_argument("--path", default=None, help="Asset source path (optional)")
    args = parser.parse_args()

    if not args.path:
        report = build_placeholder_report()
    else:
        report = scan(args.path)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
