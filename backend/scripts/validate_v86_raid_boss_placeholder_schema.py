#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v86 — Raid Boss Placeholder Schema (design-only)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    schema = _load(ROOT / "data/design/raid_bosses/raid_boss_playable_schema_v1.json")
    catalog = _load(ROOT / "data/design/raid_bosses/raid_boss_placeholder_catalog_v1.json")
    if schema is None: ERR.append("missing:schema")
    if catalog is None: ERR.append("missing:catalog")
    if schema:
        for k, want in (("design_only", True), ("runtime_attached", False),
                        ("reward_grant_attached", False), ("obtainable", False),
                        ("show_in_summon", False), ("reward_live", False),
                        ("endpoint_live", False)):
            if schema.get(k) is not want: ERR.append(f"schema.{k}_not_{want}")
        if schema.get("db_writes") != 0: ERR.append("schema.db_writes_not_0")
        forbidden_required = {"runtime_attachment", "reward_grant_attachment",
                              "obtainable_true", "show_in_summon_true",
                              "real_fragment_grant", "real_playable_boss_unlock",
                              "final_numbers", "production_ui_exposure"}
        if not forbidden_required.issubset(set(schema.get("forbidden", []))):
            ERR.append("schema.forbidden_missing_entries")
        for req_block in ("playable_form_block", "fragment_block", "phase_design_block"):
            if req_block not in schema: ERR.append(f"schema.missing_block:{req_block}")
    if catalog:
        for k, want in (("design_only", True), ("runtime_attached", False),
                        ("reward_grant_attached", False), ("obtainable", False),
                        ("show_in_summon", False), ("reward_live", False),
                        ("endpoint_live", False)):
            if catalog.get(k) is not want: ERR.append(f"catalog.{k}_not_{want}")
        if catalog.get("db_writes") != 0: ERR.append("catalog.db_writes_not_0")
        entries = catalog.get("entries", [])
        if len(entries) < 2: ERR.append("catalog.entries_too_few")
        for e in entries:
            if e.get("placeholder") is not True: ERR.append(f"catalog.entry_not_placeholder:{e.get('boss_id')}")
            pf = e.get("playable_form_design", {})
            if pf.get("unlocked") is not False:
                ERR.append(f"catalog.{e.get('boss_id')}.playable_form_unlocked_not_false")
            if pf.get("design_only") is not True:
                ERR.append(f"catalog.{e.get('boss_id')}.playable_form_design_only_not_true")
            fm = e.get("fragment_model_design", {})
            if fm.get("grant_allowed") is not False:
                ERR.append(f"catalog.{e.get('boss_id')}.fragment_grant_allowed_not_false")
            if fm.get("show_in_inventory") is not False:
                ERR.append(f"catalog.{e.get('boss_id')}.fragment_show_in_inventory_not_false")
    if ERR:
        print("FAIL v86_raid_boss_placeholder_schema:", "; ".join(ERR)); return 1
    print("PASS v86_raid_boss_placeholder_schema"); return 0

if __name__ == "__main__": sys.exit(main())
