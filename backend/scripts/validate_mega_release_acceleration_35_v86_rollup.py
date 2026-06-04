#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v86 Rollup — MEGA_RELEASE_ACCELERATION_35 v86."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    rollup = _load(ROOT / "data/design/release_acceleration/mega_release_acceleration_35_v86_rollup_marker_v1.json")
    if rollup is None:
        ERR.append("missing:rollup_marker")
        print("FAIL mega_release_acceleration_35_v86_rollup:", "; ".join(ERR)); return 1
    expected = "MEGA_RELEASE_ACCELERATION_35_PLAYABLE_MODE_VISUAL_BATTLE_ROUTING_AND_RAID_BOSS_PLACEHOLDER_SCHEMA_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    if rollup.get("verdict") != expected: ERR.append("rollup.verdict_invalid")
    if rollup.get("db_writes") != 0: ERR.append("rollup.db_writes_not_0")
    if rollup.get("reward_live") is not False: ERR.append("rollup.reward_live_not_false")
    if rollup.get("endpoint_live") is not False: ERR.append("rollup.endpoint_live_not_false")
    if rollup.get("battle_engine_authoritative") is not False:
        ERR.append("rollup.battle_engine_authoritative_not_false")
    if rollup.get("applied_to_live") is not False: ERR.append("rollup.applied_to_live_not_false")
    if rollup.get("playable_routing_ready") is not True: ERR.append("rollup.playable_routing_ready_not_true")
    if rollup.get("raid_boss_schema_design_only") is not True: ERR.append("rollup.raid_boss_schema_design_only_not_true")
    for f in (
        "data/design/playable_mode_visual_battle_routing/v86_current_preview_audit_v1.json",
        "data/design/playable_mode_visual_battle_routing/v86_visual_battle_payload_training_v1.json",
        "data/design/playable_mode_visual_battle_routing/v86_visual_battle_payload_story_v1.json",
        "data/design/playable_mode_visual_battle_routing/v86_visual_battle_payload_boss_v1.json",
        "data/design/playable_mode_visual_battle_routing/v86_visual_battle_payload_tower_v1.json",
        "data/design/playable_mode_visual_battle_routing/v86_visual_battle_payload_event_v1.json",
        "data/design/playable_mode_visual_battle_routing/v86_visual_battle_payload_arena_v1.json",
        "data/design/raid_bosses/raid_boss_playable_schema_v1.json",
        "data/design/raid_bosses/raid_boss_placeholder_catalog_v1.json",
        "frontend/app/playable-mode-battle-preview.tsx",
        "docs/divine/86_PLAYABLE_MODE_VISUAL_BATTLE_ROUTING_AUDIT.md",
        "docs/divine/86_RAID_BOSS_PLAYABLE_PLACEHOLDER_SCHEMA.md",
    ):
        if not (ROOT / f).exists(): ERR.append(f"missing_artifact:{f}")
    if ERR:
        print("FAIL mega_release_acceleration_35_v86_rollup:", "; ".join(ERR)); return 1
    print("PASS mega_release_acceleration_35_v86_rollup"); return 0

if __name__ == "__main__": sys.exit(main())
