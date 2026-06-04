#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v86 — Playable Mode Route Safety (TSX preview-only)."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def main():
    tsx = ROOT / "frontend/app/playable-mode-battle-preview.tsx"
    menu = ROOT / "frontend/app/alpha-menu-preview.tsx"
    if not tsx.exists():
        ERR.append("missing:playable-mode-battle-preview.tsx")
        print("FAIL v86_playable_mode_route_safety:", "; ".join(ERR)); return 1
    src = tsx.read_text(encoding="utf-8")
    # Required preview labels
    for label in ("PREVIEW", "LOCAL", "NOT LIVE REWARD", "NON AUTHORITATIVE"):
        if label not in src: ERR.append(f"tsx.missing_label:{label}")
    # No forbidden patterns
    forbidden_patterns = [
        (r"['\"]/api/battle/simulate['\"]", "api_battle_simulate"),
        (r"['\"]/api/story/battle['\"]", "api_story_battle"),
        (r"\bfrom\s+['\"][^'\"]*battle_engine[^'\"]*['\"]", "battle_engine_import"),
        (r"\brequire\s*\(\s*['\"][^'\"]*battle_engine[^'\"]*['\"]", "battle_engine_require"),
        (r"AsyncStorage", "asyncstorage"),
        (r"['\"]/api/pve/reward/claim['\"]", "reward_claim_endpoint"),
        (r"premium_currency\s*:", "premium_currency_field"),
        (r"\bmmr_apply\b", "mmr_apply_ref"),
        (r"\btower_completion_apply\b", "tower_completion_ref"),
        (r"\bstory_progress_apply\b", "story_progress_ref"),
        (r"\bfetch\s*\(", "fetch_call"),
    ]
    for pat, label in forbidden_patterns:
        if re.search(pat, src):
            ERR.append(f"tsx.forbidden:{label}")
    # Must NOT import combat/story/battle_engine modules
    forbidden_imports = [
        r"import\s+.*from\s+['\"]\./combat['\"]",
        r"import\s+.*from\s+['\"]\./story['\"]",
        r"import\s+.*from\s+['\"][^'\"]*battle_engine[^'\"]*['\"]",
    ]
    for pat in forbidden_imports:
        if re.search(pat, src):
            ERR.append(f"tsx.forbidden_import:{pat}")
    # Avvia battaglia preview label present
    if "Avvia battaglia preview" not in src: ERR.append("tsx.missing_preview_button_label")
    # No real claim button labels
    for bad in ("Riscatta reward", "Reclama ricompensa", "Live claim"):
        if bad in src: ERR.append(f"tsx.has_real_claim_button:{bad}")
    # Alpha menu must include deeplink
    if menu.exists():
        msrc = menu.read_text(encoding="utf-8")
        if "playable-mode-battle-preview" not in msrc:
            ERR.append("alpha_menu.missing_deeplink")
    if ERR:
        print("FAIL v86_playable_mode_route_safety:", "; ".join(ERR)); return 1
    print("PASS v86_playable_mode_route_safety"); return 0

if __name__ == "__main__": sys.exit(main())
