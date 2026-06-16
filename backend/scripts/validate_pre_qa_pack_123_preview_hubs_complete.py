#!/usr/bin/env python3
"""
Pack 123 — Validator: preview hubs (arena / boss / training trial) complete.

Verifica che:
  1. `frontend/app/arena-preview.tsx` esista e contenga almeno 3 opponent
     preview, banner preview-only, navigazione a /pre-battle-lobby?mode=arena.
  2. `frontend/app/boss-raid-preview.tsx` esista e contenga almeno 3 boss
     preview, banner preview-only, navigazione a /pre-battle-lobby?mode=boss.
  3. `frontend/app/hero-training.tsx` contenga la card "Training Preview
     Trial" con CTA verso /pre-battle-lobby?mode=training.

NO runtime mutation.

Exit code: 0 = pass, 1 = fail.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CHECKS = [
    {
        "file": "frontend/app/arena-preview.tsx",
        "patterns": [
            ("PREVIEW_OPPONENTS", "deterministic preview opponents list"),
            ("buildPreviewLobbyUrl", "uses canonical preview URL builder"),
            ("mode: 'arena'", "explicit mode arena"),
            ("preview-only", "preview-only banner copy"),
        ],
        "min_entries_pattern": r"preview_arena_\d+",
        "min_entries": 3,
    },
    {
        "file": "frontend/app/boss-raid-preview.tsx",
        "patterns": [
            ("PREVIEW_BOSSES", "deterministic preview bosses list"),
            ("buildPreviewLobbyUrl", "uses canonical preview URL builder"),
            ("mode: 'boss'", "explicit mode boss"),
            ("preview-only", "preview-only banner copy"),
        ],
        "min_entries_pattern": r"preview_boss_\d+",
        "min_entries": 3,
    },
    {
        "file": "frontend/app/hero-training.tsx",
        "patterns": [
            ("Training Preview Trial", "card title present"),
            ("buildPreviewLobbyUrl", "uses canonical preview URL builder"),
            ("mode: 'training'", "explicit mode training"),
            ("openTrainingPreviewTrial", "handler defined"),
            ("Avvia Preview Trial", "CTA label visible"),
        ],
        "min_entries_pattern": None,
        "min_entries": 0,
    },
]


def main() -> int:
    errors: list[str] = []

    for check in CHECKS:
        fpath = REPO_ROOT / check["file"]
        if not fpath.exists():
            errors.append(f"missing target file: {check['file']}")
            continue
        src = fpath.read_text(encoding="utf-8")
        for pat, desc in check["patterns"]:
            if pat not in src:
                errors.append(f"{check['file']}: missing `{pat}` ({desc})")
            else:
                print(f"OK    {check['file']}: {desc}")
        # Minimum entries
        if check["min_entries_pattern"]:
            matches = re.findall(check["min_entries_pattern"], src)
            uniq = set(matches)
            if len(uniq) < check["min_entries"]:
                errors.append(
                    f"{check['file']}: only {len(uniq)} entries (need >={check['min_entries']})"
                )
            else:
                print(
                    f"OK    {check['file']}: {len(uniq)} entries (>={check['min_entries']})"
                )

    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print()
    print("=" * 72)
    print("Pack 123 — preview hubs (arena / boss / training) complete")
    print("=" * 72)
    report = {
        "pack": "PRE_QA_PACK_123_PREVIEW_HUBS_COMPLETE",
        "validator": "validate_pre_qa_pack_123_preview_hubs_complete",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    out_dir = REPO_ROOT / "backend" / "scripts" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pack_123_preview_hubs_complete_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if errors:
        print(f"FAIL  {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS  arena/boss/training preview hubs complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
