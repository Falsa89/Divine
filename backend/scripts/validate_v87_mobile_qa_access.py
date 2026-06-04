#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v87 — Mobile QA Access Route (preview-only, deeplink-shortcut)."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def main():
    qa = ROOT / "frontend/app/mobile-qa-battle-preview.tsx"
    if not qa.exists():
        ERR.append("missing:mobile-qa-battle-preview.tsx")
        print("FAIL v87_mobile_qa_access:", "; ".join(ERR)); return 1
    src = qa.read_text(encoding="utf-8")
    # Required labels
    for lab in ("QA ACCESS", "PREVIEW ONLY", "LOCAL PAYLOAD", "NO LIVE REWARD", "NON AUTHORITATIVE"):
        if lab not in src: ERR.append(f"qa.missing_label:{lab}")
    # All 6 modes referenced
    for m in ("training", "story", "boss", "tower", "event", "arena"):
        if f'mode: "{m}"' not in src and f"'{m}'" not in src and f'"{m}"' not in src:
            ERR.append(f"qa.missing_mode:{m}")
    # Route target present
    if "/playable-mode-battle-preview" not in src:
        ERR.append("qa.missing_route_target")
    # Forbidden patterns
    forbidden_patterns = [
        (r"['\"]/api/[^'\"]+['\"]", "api_endpoint"),
        (r"\bfetch\s*\(", "fetch_call"),
        (r"AsyncStorage", "asyncstorage"),
        (r"\bfrom\s+['\"][^'\"]*battle_engine[^'\"]*['\"]", "battle_engine_import"),
        (r"import\s+.*from\s+['\"]\./combat['\"]", "combat_import"),
        (r"import\s+.*from\s+['\"]\./story['\"]", "story_import"),
        (r"premium_currency\s*:", "premium_currency_field"),
        (r"\bmmr_apply\b", "mmr_apply_ref"),
    ]
    for pat, label in forbidden_patterns:
        if re.search(pat, src):
            ERR.append(f"qa.forbidden:{label}")
    # Touch target friendly (minHeight 64)
    if "minHeight: 64" not in src and "minHeight:64" not in src:
        ERR.append("qa.touch_target_min_height_missing")
    if ERR:
        print("FAIL v87_mobile_qa_access:", "; ".join(ERR)); return 1
    print("PASS v87_mobile_qa_access"); return 0

if __name__ == "__main__": sys.exit(main())
