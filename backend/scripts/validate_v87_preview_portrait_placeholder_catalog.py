#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v87 — Preview Portrait Placeholder Catalog (design-only)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    c = _load(ROOT / "data/design/playable_mode_visual_battle_routing/v87_preview_portrait_placeholder_catalog_v1.json")
    if c is None:
        ERR.append("missing:catalog")
        print("FAIL v87_preview_portrait_placeholder_catalog:", "; ".join(ERR)); return 1
    for k, want in (("design_only", True), ("runtime_attached", False),
                    ("asset_final_import", False), ("production_ui_exposure", False),
                    ("reward_live", False), ("endpoint_live", False)):
        if c.get(k) is not want: ERR.append(f"catalog.{k}_not_{want}")
    if c.get("db_writes") != 0: ERR.append("catalog.db_writes_not_0")
    if c.get("render_strategy") != "local_letter_plus_accent_color":
        ERR.append("catalog.render_strategy_invalid")
    palette = c.get("accent_palette", [])
    if len(palette) < 6: ERR.append("catalog.palette_too_small")
    groups = c.get("alias_groups", {})
    for m in ("training", "story", "boss", "tower", "event", "arena"):
        if m not in groups or not isinstance(groups[m], list) or len(groups[m]) < 1:
            ERR.append(f"catalog.missing_alias_group:{m}")
    forbidden = set(c.get("forbidden", []))
    for k in ("final_asset_import", "character_bible_link", "hero_roster_link",
              "production_ui_exposure", "reward_grant_link", "summon_link", "inventory_link"):
        if k not in forbidden: ERR.append(f"catalog.forbidden_missing:{k}")
    if ERR:
        print("FAIL v87_preview_portrait_placeholder_catalog:", "; ".join(ERR)); return 1
    print("PASS v87_preview_portrait_placeholder_catalog"); return 0

if __name__ == "__main__": sys.exit(main())
