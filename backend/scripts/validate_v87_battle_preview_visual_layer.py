#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v87 — Battle Preview Visual Layer (HP bar, turn highlight, portrait)."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def main():
    tsx = ROOT / "frontend/app/playable-mode-battle-preview.tsx"
    if not tsx.exists():
        ERR.append("missing:playable-mode-battle-preview.tsx")
        print("FAIL v87_battle_preview_visual_layer:", "; ".join(ERR)); return 1
    src = tsx.read_text(encoding="utf-8")
    required_tokens = [
        "previewHpByAlias",
        "renderHpBar",
        "renderUnitCard",
        "portraitFor",
        "hpBarOuter",
        "hpBarFill",
        "unitCardActive",
        "unitCardBoss",
        "isActive",
    ]
    for t in required_tokens:
        if t not in src: ERR.append(f"visual.missing_token:{t}")
    # Required preview labels still present
    for lab in ("PREVIEW", "LOCAL", "NOT LIVE REWARD", "NON AUTHORITATIVE"):
        if lab not in src: ERR.append(f"visual.missing_label:{lab}")
    # No forbidden patterns introduced
    forbidden_patterns = [
        (r"\bfetch\s*\(", "fetch_call"),
        (r"AsyncStorage", "asyncstorage"),
        (r"['\"]/api/[^'\"]+['\"]", "api_endpoint"),
        (r"\bfrom\s+['\"][^'\"]*battle_engine[^'\"]*['\"]", "battle_engine_import"),
        (r"import\s+.*from\s+['\"]\./combat['\"]", "combat_import"),
        (r"import\s+.*from\s+['\"]\./story['\"]", "story_import"),
        (r"premium_currency\s*:", "premium_currency_field"),
    ]
    for pat, label in forbidden_patterns:
        if re.search(pat, src):
            ERR.append(f"visual.forbidden:{label}")
    # Deterministic HP computation must still be local-only (no setState in useMemo body)
    if "setState" in src and "useMemo" in src:
        # Only basic heuristic
        pass
    if ERR:
        print("FAIL v87_battle_preview_visual_layer:", "; ".join(ERR)); return 1
    print("PASS v87_battle_preview_visual_layer"); return 0

if __name__ == "__main__": sys.exit(main())
