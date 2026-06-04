#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v88 — Real UI Battle Preview Wiring (menu tab Battle Preview QA)."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def main():
    menu = ROOT / "frontend/app/(tabs)/menu.tsx"
    if not menu.exists():
        ERR.append("missing:tabs/menu.tsx")
        print("FAIL v88_real_ui_battle_preview_wiring:", "; ".join(ERR)); return 1
    src = menu.read_text(encoding="utf-8")
    # Category header must exist
    if "Battle Preview QA (v88)" not in src:
        ERR.append("menu.missing_category_header")
    # 5 deeplink entries (story/tower/arena/training/boss)
    required_routes = [
        "/playable-mode-battle-preview?mode=story",
        "/playable-mode-battle-preview?mode=tower",
        "/playable-mode-battle-preview?mode=arena",
        "/playable-mode-battle-preview?mode=training",
        "/playable-mode-battle-preview?mode=boss",
    ]
    for r in required_routes:
        if r not in src: ERR.append(f"menu.missing_route:{r}")
    # Labels visible
    for lab in ("Storia · Battle Preview", "Torre · Battle Preview",
                "Arena PvP · Battle Preview", "Addestramento · Battle Preview",
                "Raid · Battle Preview"):
        if lab not in src: ERR.append(f"menu.missing_label:{lab}")
    # Forbidden patterns in menu (AsyncStorage e fetch sono pre-esistenti nel menu legacy;
    # v88 verifica SOLO che il blocco "Battle Preview QA (v88)" non contenga riferimenti pericolosi.)
    cat_marker = "Battle Preview QA (v88)"
    if cat_marker in src:
        # Estrai la finestra dal marker fino alla fine dell'array (max ~2000 char)
        idx = src.index(cat_marker)
        window = src[idx: idx + 2000]
        if re.search(r"\bfetch\s*\(", window): ERR.append("menu.v88_block.has_fetch")
        if re.search(r"['\"]/api/[^'\"]+['\"]", window): ERR.append("menu.v88_block.has_api_endpoint")
        if re.search(r"\bAsyncStorage\b", window): ERR.append("menu.v88_block.has_asyncstorage")
        if re.search(r"\bfrom\s+['\"][^'\"]*battle_engine[^'\"]*['\"]", window):
            ERR.append("menu.v88_block.imports_battle_engine")
    if ERR:
        print("FAIL v88_real_ui_battle_preview_wiring:", "; ".join(ERR)); return 1
    print("PASS v88_real_ui_battle_preview_wiring"); return 0

if __name__ == "__main__": sys.exit(main())
