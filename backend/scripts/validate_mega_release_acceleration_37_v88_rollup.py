#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v88 Rollup — MEGA_RELEASE_ACCELERATION_37 v88."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    rollup = _load(ROOT / "data/design/release_acceleration/mega_release_acceleration_37_v88_rollup_marker_v1.json")
    if rollup is None:
        ERR.append("missing:rollup_marker")
        print("FAIL mega_release_acceleration_37_v88_rollup:", "; ".join(ERR)); return 1
    expected = "MEGA_RELEASE_ACCELERATION_37_PLAYABLE_MODE_REAL_UI_WIRING_AND_BATTLE_PREVIEW_EXPERIENCE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    if rollup.get("verdict") != expected: ERR.append("rollup.verdict_invalid")
    if rollup.get("db_writes") != 0: ERR.append("rollup.db_writes_not_0")
    if rollup.get("reward_live") is not False: ERR.append("rollup.reward_live_not_false")
    if rollup.get("endpoint_live") is not False: ERR.append("rollup.endpoint_live_not_false")
    if rollup.get("battle_engine_authoritative") is not False:
        ERR.append("rollup.battle_engine_authoritative_not_false")
    if rollup.get("applied_to_live") is not False: ERR.append("rollup.applied_to_live_not_false")
    if rollup.get("real_ui_wiring_done") is not True: ERR.append("rollup.real_ui_wiring_done_not_true")
    if rollup.get("experience_layer_applied") is not True: ERR.append("rollup.experience_layer_applied_not_true")
    if rollup.get("raid_boss_visual_preview_profiles_count") != 5:
        ERR.append("rollup.raid_boss_count_not_5")
    for f in (
        "frontend/app/(tabs)/menu.tsx",
        "frontend/app/playable-mode-battle-preview.tsx",
        "data/design/raid_bosses/raid_boss_visual_preview_profiles_v1.json",
        "docs/divine/88_PLAYABLE_MODE_REAL_UI_WIRING_AND_BATTLE_PREVIEW_EXPERIENCE.md",
    ):
        if not (ROOT / f).exists(): ERR.append(f"missing_artifact:{f}")
    if ERR:
        print("FAIL mega_release_acceleration_37_v88_rollup:", "; ".join(ERR)); return 1
    print("PASS mega_release_acceleration_37_v88_rollup"); return 0

if __name__ == "__main__": sys.exit(main())
