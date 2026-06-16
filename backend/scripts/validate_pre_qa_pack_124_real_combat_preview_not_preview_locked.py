#!/usr/bin/env python3
"""
Pack 124 — Validator: real combat preview NOT preview_locked.

Fallisce se `combat.tsx` lascia il path PREVIEW termina in `phase='preview_locked'`
senza popolare teamA/teamB e procedere al renderer reale. Verifica che:
  1. `buildPreviewCombatSnapshot` sia importato in combat.tsx.
  2. PREVIEW path chiami setTeamA/setTeamB con snapshot locale.
  3. PREVIEW path setti phase='preparing' e successivamente phase='fighting'.
  4. PREVIEW path NON chiami `/api/battle/simulate` dopo aver costruito lo snapshot.

NO runtime mutation.

Exit code: 0 = pass, 1 = fail.
"""
from __future__ import annotations
import json, sys, re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / "frontend" / "app" / "combat.tsx"

REQUIRED = [
    ("buildPreviewCombatSnapshot", "import buildPreviewCombatSnapshot"),
    ("PREVIEW_COMBAT_REAL", "pack 124 preview combat REAL marker"),
    ("setTeamA(snap.teamA", "setTeamA from snapshot"),
    ("setTeamB(snap.teamB", "setTeamB from snapshot"),
    ("setPhase('preparing')", "phase preparing"),
    ("setPhase('fighting')", "phase fighting"),
]


def main() -> int:
    errors: list[str] = []
    if not TARGET.exists():
        errors.append(f"missing: {TARGET}")
        return _emit(errors)
    src = TARGET.read_text(encoding="utf-8")
    for pat, desc in REQUIRED:
        if pat not in src:
            errors.append(f"missing `{pat}`: {desc}")
        else:
            print(f"OK    {desc}")
    # PREVIEW path must NOT terminate solely in preview_locked: cerca il blocco
    # `if (PREVIEW_REWARD_LOCK_ACTIVE)` e verifica che dopo ci sia setPhase('preparing').
    # NB: estraiamo SOLO la PREVIEW branch fino al primo `return;` di chiusura.
    m = re.search(r"if\s*\(\s*PREVIEW_REWARD_LOCK_ACTIVE\s*\)\s*\{(.*?)\n\s{4}\}\n", src, re.S)
    if not m:
        errors.append("PREVIEW_REWARD_LOCK_ACTIVE branch not found in startBattle")
    else:
        body = m.group(1)
        if "setPhase('preparing')" not in body:
            errors.append("PREVIEW path does not setPhase('preparing') (combat would stay preview_locked)")
        if "setPhase('fighting')" not in body:
            errors.append("PREVIEW path does not setPhase('fighting')")
        if "/api/battle/simulate" in body:
            errors.append("PREVIEW path STILL calls /api/battle/simulate (FORBIDDEN mutant)")
    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print("\n" + "="*72)
    print("Pack 124 — real combat preview NOT preview_locked")
    print("="*72)
    report = {"pack": "PRE_QA_PACK_124_REAL_COMBAT_PREVIEW_NOT_PREVIEW_LOCKED",
              "status": "PASS" if not errors else "FAIL", "errors": errors}
    out = REPO_ROOT / "backend" / "scripts" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack_124_real_combat_preview_not_preview_locked_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        for e in errors: print(f"  FAIL  {e}")
        return 1
    print("PASS  combat preview enters real renderer (phase preparing/fighting)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
