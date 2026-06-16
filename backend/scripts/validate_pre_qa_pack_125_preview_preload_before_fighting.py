#!/usr/bin/env python3
"""
Pack 125 — Validator: preview preload PRIMA di phase='fighting'.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COMBAT = REPO_ROOT / "frontend" / "app" / "combat.tsx"


def main() -> int:
    errors: list[str] = []
    if not COMBAT.exists():
        errors.append(f"missing: {COMBAT}")
        return _emit(errors)
    src = COMBAT.read_text(encoding="utf-8")
    m = re.search(r"if\s*\(\s*PREVIEW_REWARD_LOCK_ACTIVE\s*\)\s*\{(.*?)\n\s{4}\}\n", src, re.S)
    if not m:
        errors.append("PREVIEW branch not found")
        return _emit(errors)
    body = m.group(1)
    required = [
        ("preloadAssets", "preloadAssets array constructed"),
        ("preloadBattleAsset", "preloadBattleAsset called"),
        ("Promise.race", "preload race with timeout"),
        ("setPhase('preparing')", "phase preparing after preload"),
        ("setPhase('fighting')", "phase fighting after preparing"),
        ("getHeroBattlePreloadAssets", "hero sprite preload"),
    ]
    for pat, desc in required:
        if pat not in body:
            errors.append(f"missing in preview branch: `{pat}` ({desc})")
        else:
            print(f"OK    {desc}")
    # Verifica ordine: setPhase('fighting') deve venire DOPO Promise.race / preload.
    idx_race = body.find("Promise.race")
    idx_fighting = body.find("setPhase('fighting')")
    if idx_race == -1 or idx_fighting == -1:
        pass
    elif idx_fighting < idx_race:
        errors.append("setPhase('fighting') called BEFORE preload (ordine errato)")
    else:
        print("OK    fighting phase set AFTER preload completion")
    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print("\n" + "="*72)
    print("Pack 125 — preview preload before fighting")
    print("="*72)
    report = {"pack": "PRE_QA_PACK_125_PREVIEW_PRELOAD_BEFORE_FIGHTING",
              "status": "PASS" if not errors else "FAIL", "errors": errors}
    out = REPO_ROOT / "backend" / "scripts" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack_125_preview_preload_before_fighting_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        for e in errors: print(f"  FAIL  {e}")
        return 1
    print("PASS  preview preload runs before phase='fighting'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
