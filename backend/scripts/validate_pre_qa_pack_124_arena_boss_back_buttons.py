#!/usr/bin/env python3
"""
Pack 124 — Validator: arena/boss preview hubs hanno back button.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TARGETS = [
    "frontend/app/arena-preview.tsx",
    "frontend/app/boss-raid-preview.tsx",
]

REQUIRED = [
    ("router.back()", "router.back call"),
    ("router.canGoBack", "canGoBack guard"),
    ("router.replace('/(tabs)/home'", "fallback to home"),
    ("Indietro", "back button label"),
    ("accessibilityLabel=\"Torna indietro\"", "a11y label"),
]


def main() -> int:
    errors: list[str] = []
    for rel in TARGETS:
        fpath = REPO_ROOT / rel
        if not fpath.exists():
            errors.append(f"missing: {rel}")
            continue
        src = fpath.read_text(encoding="utf-8")
        for pat, desc in REQUIRED:
            if pat not in src:
                errors.append(f"{rel}: missing `{pat}` ({desc})")
            else:
                print(f"OK    {rel}: {desc}")
    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print("\n" + "="*72)
    print("Pack 124 — arena/boss back buttons")
    print("="*72)
    report = {"pack": "PRE_QA_PACK_124_ARENA_BOSS_BACK_BUTTONS",
              "status": "PASS" if not errors else "FAIL", "errors": errors}
    out = REPO_ROOT / "backend" / "scripts" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack_124_arena_boss_back_buttons_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        for e in errors: print(f"  FAIL  {e}")
        return 1
    print("PASS  arena/boss back buttons + fallback safe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
