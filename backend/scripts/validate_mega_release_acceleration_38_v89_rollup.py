#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v89 Rollup — MEGA_RELEASE_ACCELERATION_38 v89."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    rollup = _load(ROOT / "data/design/release_acceleration/mega_release_acceleration_38_v89_rollup_marker_v1.json")
    if rollup is None:
        ERR.append("missing:rollup_marker")
        print("FAIL mega_release_acceleration_38_v89_rollup:", "; ".join(ERR)); return 1
    expected = "MEGA_RELEASE_ACCELERATION_38_REAL_BATTLEFIELD_PREVIEW_RESCUE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    if rollup.get("verdict") != expected: ERR.append("rollup.verdict_invalid")
    if rollup.get("db_writes") != 0: ERR.append("rollup.db_writes_not_0")
    if rollup.get("reward_live") is not False: ERR.append("rollup.reward_live_not_false")
    if rollup.get("endpoint_live") is not False: ERR.append("rollup.endpoint_live_not_false")
    if rollup.get("battle_engine_authoritative") is not False:
        ERR.append("rollup.battle_engine_authoritative_not_false")
    if rollup.get("applied_to_live") is not False: ERR.append("rollup.applied_to_live_not_false")
    if rollup.get("real_battlefield_applied") is not True: ERR.append("rollup.real_battlefield_applied_not_true")
    if rollup.get("home_battle_flow_audit_done") is not True: ERR.append("rollup.home_battle_flow_audit_done_not_true")
    if rollup.get("asset_reuse_only") is not True: ERR.append("rollup.asset_reuse_only_not_true")
    for f in (
        "frontend/app/playable-mode-battle-preview.tsx",
        "data/design/playable_mode_visual_battle_routing/v89_home_battle_flow_audit_v1.json",
        "data/design/playable_mode_visual_battle_routing/v89_real_battlefield_player_team_mapping_v1.json",
        "data/design/playable_mode_visual_battle_routing/v89_real_battlefield_enemy_team_mapping_v1.json",
        "docs/divine/89_HOME_BATTLE_FLOW_AND_REAL_BATTLEFIELD_PREVIEW_AUDIT.md",
    ):
        if not (ROOT / f).exists(): ERR.append(f"missing_artifact:{f}")
    if ERR:
        print("FAIL mega_release_acceleration_38_v89_rollup:", "; ".join(ERR)); return 1
    print("PASS mega_release_acceleration_38_v89_rollup"); return 0

if __name__ == "__main__": sys.exit(main())
