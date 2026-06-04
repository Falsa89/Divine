#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v81 Track F — Reward Claim UI Summary Preview Shell."""
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    tsx = ROOT / "frontend/app/reward-claim-summary-preview.tsx"
    contract = _load(ROOT / "data/design/economy/reward_claim_ui_summary_preview_shell_contract_v1.json")
    static_data = _load(ROOT / "data/design/economy/reward_claim_ui_summary_preview_shell_static_data_v1.json")
    result = _load(ROOT / "data/design/economy/reward_claim_ui_summary_preview_shell_result_v1.json")
    marker = _load(ROOT / "data/design/economy/reward_claim_ui_summary_preview_shell_marker_v1.json")
    if not tsx.exists():
        ERR.append("missing:reward-claim-summary-preview.tsx")
    else:
        src = tsx.read_text(encoding="utf-8")
        # Vietato: import battle_engine, story, combat
        forbidden_imports = [
            (r"^\s*import\s+.*\bbattle_engine\b", "battle_engine"),
            (r"^\s*import\s+.*\bstory\b\s+from", "story"),
            (r"^\s*import\s+.*\bcombat\b\s+from", "combat"),
            (r"from\s+['\"]\.\./story['\"]", "../story"),
            (r"from\s+['\"]\.\./combat['\"]", "../combat"),
            (r"from\s+['\"]\./story['\"]", "./story"),
            (r"from\s+['\"]\./combat['\"]", "./combat"),
        ]
        for pat, label in forbidden_imports:
            if re.search(pat, src, flags=re.MULTILINE):
                ERR.append(f"tsx.forbidden_import:{label}")
        # Vietato: fetch reale, AsyncStorage usage, axios, /api/
        # Verifica solo statement reali, non commenti
        real_lines = [ln for ln in src.splitlines() if not ln.strip().startswith("//") and not ln.strip().startswith("*")]
        joined = "\n".join(real_lines)
        if re.search(r"\bfetch\(", joined): ERR.append("tsx.real_fetch_call")
        if re.search(r"\bAsyncStorage\.", joined): ERR.append("tsx.asyncstorage_call")
        if re.search(r"\baxios\.", joined): ERR.append("tsx.axios_call")
        if re.search(r"['\"]/api/", joined): ERR.append("tsx.api_path_literal")
        if re.search(r"process\.env\.", joined): ERR.append("tsx.process_env_use")
        # Labels obbligatori presenti nel codice
        for label in ("PREVIEW", "STAGING", "CANARY_LOCAL", "NOT LIVE REWARD"):
            if label not in src:
                ERR.append(f"tsx.missing_label:{label}")
    if contract:
        if contract.get("deeplink_only") is not True: ERR.append("contract.deeplink_only_not_true")
        if contract.get("production_ui_exposure") is not False:
            ERR.append("contract.production_ui_exposure_not_false")
    if result:
        if result.get("typescript_pass") is not True: ERR.append("result.tsc_not_pass")
        if result.get("static_forbidden_check_pass") is not True:
            ERR.append("result.static_check_not_pass")
        if result.get("db_writes", 1) != 0: ERR.append("result.db_writes_nonzero")
    if static_data is None: ERR.append("missing:static_data")
    if marker is None: ERR.append("missing:marker")
    if ERR:
        print("FAIL reward_claim_ui_summary_preview_shell:", "; ".join(ERR)); return 1
    print("PASS reward_claim_ui_summary_preview_shell"); return 0

if __name__ == "__main__": sys.exit(main())
