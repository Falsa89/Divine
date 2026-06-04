#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v89 — No Asset Final Import + No Character Bible Link."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def main():
    tsx = ROOT / "frontend/app/playable-mode-battle-preview.tsx"
    if not tsx.exists():
        ERR.append("missing:tsx"); print("FAIL v89_no_asset_final_import_no_character_bible:", "; ".join(ERR)); return 1
    src = tsx.read_text(encoding="utf-8")
    # Tutte le require devono puntare a /assets/backgrounds o /assets/placeholders/heroes
    requires = re.findall(r"require\(\s*['\"]([^'\"]+)['\"]\s*\)", src)
    for r in requires:
        if "/assets/backgrounds/" not in r and "/assets/placeholders/heroes/" not in r:
            ERR.append(f"tsx.require_outside_allowed_roots:{r}")
    # Forbidden references
    forbidden_substrings = [
        "final_numbers",
        "character_bible",
        "hero_roster",
        "/assets/heroes/",  # NON usare heroes finali, solo placeholders
        "battle_engine",
    ]
    for s in forbidden_substrings:
        if s in src and s == "battle_engine" and "battle_engine_attached" in src:
            # battle_engine_attached è un campo del payload (consentito)
            # Filtra solo riferimenti veri al modulo battle_engine
            if re.search(r"\bbattle_engine\.py\b|from\s+['\"][^'\"]*battle_engine[^'\"]*['\"]", src):
                ERR.append("tsx.forbidden_substring:battle_engine_real")
            continue
        if s in src:
            ERR.append(f"tsx.forbidden_substring:{s}")
    if ERR:
        print("FAIL v89_no_asset_final_import_no_character_bible:", "; ".join(ERR)); return 1
    print("PASS v89_no_asset_final_import_no_character_bible"); return 0

if __name__ == "__main__": sys.exit(main())
