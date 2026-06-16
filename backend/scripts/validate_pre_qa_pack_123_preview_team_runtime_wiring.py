#!/usr/bin/env python3
"""
Pack 123 — Validator: preview team runtime wiring.

Verifica:
  1. `frontend/src/utils/previewBattleTeam.ts` esiste e contiene:
     - export `CANONICAL_PREVIEW_HERO_SLOTS` con almeno 6 slot.
     - export `buildPreviewLocalTeamSnapshot`.
     - export `buildPreviewCombatUrl` e `buildPreviewLobbyUrl`.
     - export `previewContextFromParams`.
     - export `PREVIEW_TEAM_BANNER_IT`.
     - fail-closed implementato (ritorna null se ctx non preview coerente).
  2. I file consumer cablano l'import:
     - `frontend/app/pre-battle-lobby.tsx`
     - `frontend/app/combat.tsx`
     - `frontend/app/tower-of-the-hells.tsx`
     - `frontend/app/hero-training.tsx`
     - `frontend/app/arena-preview.tsx`
     - `frontend/app/boss-raid-preview.tsx`

NESSUNA mutazione runtime. Solo analisi statica.

Exit code: 0 = pass, 1 = fail.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
UTIL_FILE = REPO_ROOT / "frontend" / "src" / "utils" / "previewBattleTeam.ts"

CONSUMERS = {
    "pre-battle-lobby.tsx": ["buildPreviewLocalTeamSnapshot", "previewContextFromParams"],
    "combat.tsx": ["buildPreviewLocalTeamSnapshot", "previewContextFromParams"],
    "tower-of-the-hells.tsx": ["buildPreviewLobbyUrl"],
    "hero-training.tsx": ["buildPreviewLobbyUrl"],
    "arena-preview.tsx": ["buildPreviewLobbyUrl"],
    "boss-raid-preview.tsx": ["buildPreviewLobbyUrl"],
}

REQUIRED_UTIL_EXPORTS = [
    "CANONICAL_PREVIEW_HERO_SLOTS",
    "CANONICAL_PREVIEW_HERO_IDS",
    "buildPreviewLocalTeamSnapshot",
    "buildPreviewCombatUrl",
    "buildPreviewLobbyUrl",
    "previewContextFromParams",
    "canUsePreviewTeamFallback",
    "PREVIEW_TEAM_BANNER_IT",
    "PREVIEW_ALLOWED_MODES",
]


def fail(msg: str) -> None:
    print(f"FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"OK    {msg}")


def main() -> int:
    errors: list[str] = []

    if not UTIL_FILE.exists():
        errors.append(f"missing util file: {UTIL_FILE}")
        return _emit(errors)

    util_src = UTIL_FILE.read_text(encoding="utf-8")
    for sym in REQUIRED_UTIL_EXPORTS:
        if sym not in util_src:
            errors.append(f"util missing export/symbol: {sym}")
        else:
            ok(f"util export present: {sym}")

    # fail-closed enforcement: buildPreviewLocalTeamSnapshot must return null
    # when canUsePreviewTeamFallback returns false.
    if "return null" not in util_src:
        errors.append("util missing fail-closed `return null` in buildPreviewLocalTeamSnapshot")
    else:
        ok("util fail-closed return null present")

    # At least 6 slots (6v6 battle system)
    slot_count = util_src.count("hero_id:")
    if slot_count < 6:
        errors.append(f"util has only {slot_count} preview hero slots (need >=6)")
    else:
        ok(f"util has {slot_count} preview hero slots (>=6)")

    # consumer wiring
    for fname, required_symbols in CONSUMERS.items():
        fpath = REPO_ROOT / "frontend" / "app" / fname
        if not fpath.exists():
            errors.append(f"consumer file missing: {fpath}")
            continue
        src = fpath.read_text(encoding="utf-8")
        if "previewBattleTeam" not in src:
            errors.append(f"{fname}: missing import from previewBattleTeam")
            continue
        for sym in required_symbols:
            if sym not in src:
                errors.append(f"{fname}: missing symbol usage `{sym}`")
        ok(f"consumer wired: {fname}")

    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print()
    print("=" * 72)
    print("Pack 123 — preview team runtime wiring")
    print("=" * 72)
    report = {
        "pack": "PRE_QA_PACK_123_PREVIEW_TEAM_FALLBACK_RUNTIME_WIRING",
        "validator": "validate_pre_qa_pack_123_preview_team_runtime_wiring",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    out_dir = REPO_ROOT / "backend" / "scripts" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pack_123_preview_team_runtime_wiring_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if errors:
        print(f"FAIL  {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS  all checks green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
