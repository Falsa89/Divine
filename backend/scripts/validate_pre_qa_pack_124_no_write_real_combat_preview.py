#!/usr/bin/env python3
"""
Pack 124 — Validator: no reward / no EXP / no progress / no ranking / no DB write
nel path PREVIEW di combat.tsx.
"""
from __future__ import annotations
import json, sys, re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / "frontend" / "app" / "combat.tsx"

FORBIDDEN_IN_PREVIEW_BRANCH = [
    ("/api/battle/simulate", "simulate mutant"),
    ("/api/team/save", "team save mutant"),
    ("refreshUser()", "refreshUser inside preview branch"),
    ("grantAffinity(", "affinity grant inside preview branch"),
    ("/api/gacha/", "gacha mutant"),
    ("/api/shop/", "shop mutant"),
    ("/api/vip/", "vip mutant"),
]

REQUIRED_GUARDS = [
    ("!PREVIEW_REWARD_LOCK_ACTIVE", "reward/affinity grant gated by PREVIEW lock"),
    ("is_preview_local: true", "local preview result marker"),
]


def main() -> int:
    errors: list[str] = []
    if not TARGET.exists():
        errors.append(f"missing: {TARGET}")
        return _emit(errors)
    src = TARGET.read_text(encoding="utf-8")
    m = re.search(r"if\s*\(\s*PREVIEW_REWARD_LOCK_ACTIVE\s*\)\s*\{(.*?)\n\s{4}\}\n", src, re.S)
    if not m:
        errors.append("PREVIEW branch not found")
        return _emit(errors)
    body = m.group(1)
    for pat, desc in FORBIDDEN_IN_PREVIEW_BRANCH:
        if pat in body:
            errors.append(f"forbidden in preview branch: `{pat}` ({desc})")
        else:
            print(f"OK    no `{pat}` in preview branch")
    for pat, desc in REQUIRED_GUARDS:
        if pat not in src:
            errors.append(f"missing guard: `{pat}` ({desc})")
        else:
            print(f"OK    guard present: {desc}")
    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print("\n" + "="*72)
    print("Pack 124 — no-write real combat preview invariant")
    print("="*72)
    report = {"pack": "PRE_QA_PACK_124_NO_WRITE_REAL_COMBAT_PREVIEW",
              "status": "PASS" if not errors else "FAIL", "errors": errors}
    out = REPO_ROOT / "backend" / "scripts" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack_124_no_write_real_combat_preview_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        for e in errors: print(f"  FAIL  {e}")
        return 1
    print("PASS  no mutant calls in preview combat branch")
    return 0


if __name__ == "__main__":
    sys.exit(main())
