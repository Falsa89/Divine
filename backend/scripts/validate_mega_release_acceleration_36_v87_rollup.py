#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v87 Rollup — MEGA_RELEASE_ACCELERATION_36 v87."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    rollup = _load(ROOT / "data/design/release_acceleration/mega_release_acceleration_36_v87_rollup_marker_v1.json")
    if rollup is None:
        ERR.append("missing:rollup_marker")
        print("FAIL mega_release_acceleration_36_v87_rollup:", "; ".join(ERR)); return 1
    expected = "MEGA_RELEASE_ACCELERATION_36_MOBILE_QA_ACCESS_AND_BATTLE_PREVIEW_VISUAL_LAYER_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    if rollup.get("verdict") != expected: ERR.append("rollup.verdict_invalid")
    if rollup.get("db_writes") != 0: ERR.append("rollup.db_writes_not_0")
    if rollup.get("reward_live") is not False: ERR.append("rollup.reward_live_not_false")
    if rollup.get("endpoint_live") is not False: ERR.append("rollup.endpoint_live_not_false")
    if rollup.get("battle_engine_authoritative") is not False: ERR.append("rollup.battle_engine_authoritative_not_false")
    if rollup.get("applied_to_live") is not False: ERR.append("rollup.applied_to_live_not_false")
    if rollup.get("mobile_qa_access_route_ready") is not True: ERR.append("rollup.mobile_qa_access_route_ready_not_true")
    if rollup.get("battle_preview_visual_layer_applied") is not True: ERR.append("rollup.battle_preview_visual_layer_applied_not_true")
    for f in (
        "frontend/app/mobile-qa-battle-preview.tsx",
        "frontend/app/playable-mode-battle-preview.tsx",
        "data/design/playable_mode_visual_battle_routing/v87_preview_portrait_placeholder_catalog_v1.json",
        "docs/divine/87_MOBILE_QA_ACCESS_AND_BATTLE_PREVIEW_VISUAL_LAYER.md",
    ):
        if not (ROOT / f).exists(): ERR.append(f"missing_artifact:{f}")
    if ERR:
        print("FAIL mega_release_acceleration_36_v87_rollup:", "; ".join(ERR)); return 1
    print("PASS mega_release_acceleration_36_v87_rollup"); return 0

if __name__ == "__main__": sys.exit(main())
