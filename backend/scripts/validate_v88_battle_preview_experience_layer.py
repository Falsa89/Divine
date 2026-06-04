#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v88 — Battle Preview Experience Layer (autoplay/pause/speed/AI hints/toasts/end summary)."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def main():
    tsx = ROOT / "frontend/app/playable-mode-battle-preview.tsx"
    if not tsx.exists():
        ERR.append("missing:playable-mode-battle-preview.tsx")
        print("FAIL v88_battle_preview_experience_layer:", "; ".join(ERR)); return 1
    src = tsx.read_text(encoding="utf-8")
    required_tokens = [
        "setAutoplay",
        "autoplay",
        "speed",
        "aiHintFor",
        "floatingToast",
        "endSummaryCard",
        "NON AUTHORITATIVE \u00b7 NO REWARD APPLIED",
        "setSpeed",
        "clearTimeout",
        "useEffect",
    ]
    for t in required_tokens:
        if t not in src: ERR.append(f"experience.missing_token:{t}")
    # Preview labels still present
    for lab in ("PREVIEW", "LOCAL", "NOT LIVE REWARD", "NON AUTHORITATIVE"):
        if lab not in src: ERR.append(f"experience.missing_label:{lab}")
    # No forbidden patterns
    forbidden_patterns = [
        (r"\bfetch\s*\(", "fetch_call"),
        (r"AsyncStorage", "asyncstorage"),
        (r"['\"]/api/[^'\"]+['\"]", "api_endpoint"),
        (r"\bfrom\s+['\"][^'\"]*battle_engine[^'\"]*['\"]", "battle_engine_import"),
        (r"import\s+.*from\s+['\"]\./combat['\"]", "combat_import"),
        (r"import\s+.*from\s+['\"]\./story['\"]", "story_import"),
        (r"premium_currency\s*:", "premium_currency_field"),
        (r"\bmmr_apply\b", "mmr_apply_ref"),
        (r"\btower_completion_apply\b", "tower_completion_ref"),
        (r"\bstory_progress_apply\b", "story_progress_ref"),
    ]
    for pat, label in forbidden_patterns:
        if re.search(pat, src):
            ERR.append(f"experience.forbidden:{label}")
    if ERR:
        print("FAIL v88_battle_preview_experience_layer:", "; ".join(ERR)); return 1
    print("PASS v88_battle_preview_experience_layer"); return 0

if __name__ == "__main__": sys.exit(main())
