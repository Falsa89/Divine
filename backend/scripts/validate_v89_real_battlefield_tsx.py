#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v89 — Real Battlefield TSX (background + 2 sides + sprite)."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def main():
    tsx = ROOT / "frontend/app/playable-mode-battle-preview.tsx"
    if not tsx.exists():
        ERR.append("missing:tsx"); print("FAIL v89_real_battlefield_tsx:", "; ".join(ERR)); return 1
    src = tsx.read_text(encoding="utf-8")
    required_tokens = [
        "ImageBackground",
        "BACKGROUND_BY_MODE",
        "SPRITE_BY_ALIAS",
        "SPRITE_BY_ROLE",
        "spriteFor",
        "battlefield",
        "battlefieldRow",
        "battlefieldSide",
        "battlefieldUnitPlayer",
        "battlefieldUnitEnemy",
        "battlefieldSprite",
        "ALLEATI",
        "NEMICI",
    ]
    for t in required_tokens:
        if t not in src: ERR.append(f"tsx.missing_token:{t}")
    # Backgrounds referenced must exist
    for bg in ("nordic_bg_01.png", "celtic_bg_01.png", "egypt_bg_02.png",
               "japanese_bg_01.png", "greek_bg_01.png", "nordic_bg_02.png"):
        if bg not in src: ERR.append(f"tsx.missing_background_ref:{bg}")
        if not (ROOT / "frontend/assets/backgrounds" / bg).exists():
            ERR.append(f"tsx.background_file_missing:{bg}")
    # Required sprite roots present
    for role_dir in ("tank_standard_v1", "dps_melee_standard_v1", "healer_standard_v1",
                     "support_buffer_standard_v1", "dps_ranged_standard_v1",
                     "mage_aoe_standard_v1", "assassin_burst_standard_v1",
                     "control_debuff_standard_v1", "hybrid_special_standard_v1"):
        if not (ROOT / "frontend/assets/placeholders/heroes" / role_dir / "combat_base.png").exists():
            ERR.append(f"tsx.sprite_file_missing:{role_dir}")
    # Forbidden patterns
    forbidden_patterns = [
        (r"\bfetch\s*\(", "fetch_call"),
        (r"AsyncStorage", "asyncstorage"),
        (r"['\"]/api/[^'\"]+['\"]", "api_endpoint"),
        (r"\bfrom\s+['\"][^'\"]*battle_engine[^'\"]*['\"]", "battle_engine_import"),
        (r"import\s+.*from\s+['\"]\./combat['\"]", "combat_import"),
        (r"import\s+.*from\s+['\"]\./story['\"]", "story_import"),
    ]
    for pat, label in forbidden_patterns:
        if re.search(pat, src):
            ERR.append(f"tsx.forbidden:{label}")
    # Preserved v87/v88 features
    for feature in ("renderHpBar", "aiHintFor", "floatingToast", "endSummaryCard", "setAutoplay", "setSpeed"):
        if feature not in src: ERR.append(f"tsx.missing_preserved_feature:{feature}")
    if ERR:
        print("FAIL v89_real_battlefield_tsx:", "; ".join(ERR)); return 1
    print("PASS v89_real_battlefield_tsx"); return 0

if __name__ == "__main__": sys.exit(main())
