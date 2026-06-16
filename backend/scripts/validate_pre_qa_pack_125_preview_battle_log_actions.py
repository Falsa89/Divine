#!/usr/bin/env python3
"""
Pack 125 — Validator: preview battle_log NON vuoto e azioni compatibili con playLog.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
UTIL = REPO_ROOT / "frontend" / "src" / "utils" / "previewBattleTeam.ts"
COMBAT = REPO_ROOT / "frontend" / "app" / "combat.tsx"


def main() -> int:
    errors: list[str] = []
    if not UTIL.exists():
        errors.append(f"missing util: {UTIL}")
        return _emit(errors)
    if not COMBAT.exists():
        errors.append(f"missing combat: {COMBAT}")
        return _emit(errors)
    util_src = UTIL.read_text(encoding="utf-8")
    combat_src = COMBAT.read_text(encoding="utf-8")

    # 1. buildPreviewBattleLog deve esistere ed essere esportata.
    if "export function buildPreviewBattleLog" not in util_src:
        errors.append("missing export `buildPreviewBattleLog` in previewBattleTeam.ts")
    else:
        print("OK    buildPreviewBattleLog export present")

    # 2. Il log deve avere almeno 3 turni (ricerca di `{ turn: 1`, `turn: 2`, `turn: 3`).
    if not all(f"turn: {i}" in util_src for i in (1, 2, 3)):
        errors.append("buildPreviewBattleLog does not produce at least 3 turns")
    else:
        print("OK    3 turns present in preview battle log")

    # 3. Azioni compatibili: deve contenere skill_type 'nad', 'sad', e type 'heal'.
    required_action_markers = ["'nad'", "'sad'", "'heal'", "'attack'"]
    for marker in required_action_markers:
        if marker not in util_src:
            errors.append(f"missing action marker `{marker}` in buildPreviewBattleLog")
        else:
            print(f"OK    action marker present: {marker}")

    # 4. combat.tsx PREVIEW branch deve chiamare buildPreviewBattleLog e playLog.
    m = re.search(r"if\s*\(\s*PREVIEW_REWARD_LOCK_ACTIVE\s*\)\s*\{(.*?)\n\s{4}\}\n", combat_src, re.S)
    if not m:
        errors.append("PREVIEW branch not found in combat.tsx")
    else:
        body = m.group(1)
        if "buildPreviewBattleLog" not in body:
            errors.append("PREVIEW branch does not call buildPreviewBattleLog")
        else:
            print("OK    PREVIEW branch calls buildPreviewBattleLog")
        if "playLog(" not in body:
            errors.append("PREVIEW branch does not call playLog (combat would stay idle)")
        else:
            print("OK    PREVIEW branch calls playLog")
        if "/api/battle/simulate" in body:
            errors.append("PREVIEW branch STILL calls /api/battle/simulate (mutant FORBIDDEN)")
        if "battle_log: previewLog" not in body:
            errors.append("PREVIEW branch result does not assign battle_log: previewLog")
        else:
            print("OK    PREVIEW result.battle_log = previewLog")

    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print("\n" + "="*72)
    print("Pack 125 — preview battle_log actions")
    print("="*72)
    report = {"pack": "PRE_QA_PACK_125_PREVIEW_BATTLE_LOG_ACTIONS",
              "status": "PASS" if not errors else "FAIL", "errors": errors}
    out = REPO_ROOT / "backend" / "scripts" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack_125_preview_battle_log_actions_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        for e in errors: print(f"  FAIL  {e}")
        return 1
    print("PASS  preview battle_log non-empty + compatible actions + no simulate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
