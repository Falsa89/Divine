#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v89 — Home Battle Flow Audit + Mapping integrity."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []
BASE = ROOT / "data/design/playable_mode_visual_battle_routing"

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    audit = _load(BASE / "v89_home_battle_flow_audit_v1.json")
    pmap = _load(BASE / "v89_real_battlefield_player_team_mapping_v1.json")
    emap = _load(BASE / "v89_real_battlefield_enemy_team_mapping_v1.json")
    for name, obj in (("audit", audit), ("pmap", pmap), ("emap", emap)):
        if obj is None: ERR.append(f"missing:{name}")
    if audit:
        for k in ("sources_inspected_read_only", "old_home_battle_visual_traits",
                  "v88_screen_traits_missing", "v89_rescue_strategy"):
            if not audit.get(k): ERR.append(f"audit.missing:{k}")
        if audit.get("db_writes") != 0: ERR.append("audit.db_writes_not_0")
        for k in ("reward_live", "endpoint_live", "battle_engine_authoritative"):
            if audit.get(k) is not False: ERR.append(f"audit.{k}_not_false")
    if pmap:
        if pmap.get("asset_reuse_only") is not True: ERR.append("pmap.asset_reuse_only_not_true")
        if pmap.get("db_writes") != 0: ERR.append("pmap.db_writes_not_0")
        if not pmap.get("role_to_sprite"): ERR.append("pmap.role_to_sprite_missing")
        required_roles = {"tank", "dps_melee", "dps_ranged", "healer", "support", "mage", "assassin", "control", "hybrid"}
        if not required_roles.issubset(set(pmap.get("role_to_sprite", {}).keys())):
            ERR.append("pmap.roles_incomplete")
        overrides = pmap.get("alias_to_role_overrides", {})
        if len(overrides) < 12: ERR.append("pmap.overrides_too_few")
    if emap:
        if emap.get("asset_reuse_only") is not True: ERR.append("emap.asset_reuse_only_not_true")
        if emap.get("db_writes") != 0: ERR.append("emap.db_writes_not_0")
        m2b = emap.get("mode_to_background", {})
        for m in ("training", "story", "boss", "tower", "event", "arena"):
            if m not in m2b: ERR.append(f"emap.mode_to_background.missing:{m}")
            else:
                bg = ROOT / "frontend/assets/backgrounds" / m2b[m]
                if not bg.exists(): ERR.append(f"emap.background_not_found:{m2b[m]}")
        layout = emap.get("battlefield_layout", {})
        if layout.get("player_side") != "left": ERR.append("emap.player_side_not_left")
        if layout.get("enemy_side") != "right": ERR.append("emap.enemy_side_not_right")
    if ERR:
        print("FAIL v89_home_battle_flow_audit:", "; ".join(ERR)); return 1
    print("PASS v89_home_battle_flow_audit"); return 0

if __name__ == "__main__": sys.exit(main())
