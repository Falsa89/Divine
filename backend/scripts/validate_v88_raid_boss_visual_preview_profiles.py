#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v88 — Raid Boss Visual Preview Profiles (design-only, 5 boss)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []
REQUIRED_BOSSES = {"Jormungandr", "Fenrir", "Apophis", "Yamata no Orochi", "Crono"}

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    c = _load(ROOT / "data/design/raid_bosses/raid_boss_visual_preview_profiles_v1.json")
    if c is None:
        ERR.append("missing:profiles")
        print("FAIL v88_raid_boss_visual_preview_profiles:", "; ".join(ERR)); return 1
    for k, want in (("design_only", True), ("runtime_attached", False),
                    ("reward_grant_attached", False), ("obtainable", False),
                    ("show_in_summon", False), ("reward_live", False),
                    ("endpoint_live", False)):
        if c.get(k) is not want: ERR.append(f"profiles.{k}_not_{want}")
    if c.get("db_writes") != 0: ERR.append("profiles.db_writes_not_0")
    forbidden = set(c.get("forbidden", []))
    for k in ("final_asset_import", "character_bible_link", "hero_roster_link",
              "production_ui_exposure", "reward_grant_link", "summon_link",
              "inventory_link", "runtime_attachment", "battle_engine_authoritative"):
        if k not in forbidden: ERR.append(f"profiles.forbidden_missing:{k}")
    profiles = c.get("profiles", [])
    if len(profiles) != 5: ERR.append("profiles.count_not_5")
    got_names = set()
    for p in profiles:
        got_names.add(p.get("display_name", ""))
        if p.get("placeholder") is not True:
            ERR.append(f"profiles.{p.get('boss_id')}.placeholder_not_true")
        pf = p.get("playable_form_design", {})
        if pf.get("unlocked") is not False:
            ERR.append(f"profiles.{p.get('boss_id')}.playable_form_unlocked_not_false")
        if pf.get("design_only") is not True:
            ERR.append(f"profiles.{p.get('boss_id')}.playable_form_design_only_not_true")
        fm = p.get("fragment_model_design", {})
        if fm.get("grant_allowed") is not False:
            ERR.append(f"profiles.{p.get('boss_id')}.fragment_grant_allowed_not_false")
        if fm.get("show_in_inventory") is not False:
            ERR.append(f"profiles.{p.get('boss_id')}.fragment_show_in_inventory_not_false")
        if not p.get("phases_design") or len(p["phases_design"]) < 2:
            ERR.append(f"profiles.{p.get('boss_id')}.phases_design_too_few")
        if not p.get("intent_hints_design") or len(p["intent_hints_design"]) < 2:
            ERR.append(f"profiles.{p.get('boss_id')}.intent_hints_too_few")
    missing = REQUIRED_BOSSES - got_names
    for m in sorted(missing): ERR.append(f"profiles.missing_boss:{m}")
    if ERR:
        print("FAIL v88_raid_boss_visual_preview_profiles:", "; ".join(ERR)); return 1
    print("PASS v88_raid_boss_visual_preview_profiles"); return 0

if __name__ == "__main__": sys.exit(main())
