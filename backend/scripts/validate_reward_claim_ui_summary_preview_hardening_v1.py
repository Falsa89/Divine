#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v82 Track F — Reward Claim UI Summary Preview Hardening."""
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    tsx = ROOT / "frontend/app/reward-claim-summary-preview.tsx"
    alpha_menu = ROOT / "frontend/app/alpha-menu-preview.tsx"
    static_data = _load(ROOT / "data/design/economy/reward_claim_ui_summary_preview_hardening_static_data_v1.json")
    result = _load(ROOT / "data/design/economy/reward_claim_ui_summary_preview_hardening_result_v1.json")
    marker = _load(ROOT / "data/design/economy/reward_claim_ui_summary_preview_hardening_marker_v1.json")
    if not tsx.exists():
        ERR.append("missing:reward-claim-summary-preview.tsx")
    else:
        src = tsx.read_text(encoding="utf-8")
        # Vietato import
        forbidden_imports = [
            (r"^\s*import\s+.*\bbattle_engine\b", "battle_engine"),
            (r"from\s+['\"]\.\./story['\"]", "../story"),
            (r"from\s+['\"]\.\./combat['\"]", "../combat"),
            (r"from\s+['\"]\./story['\"]", "./story"),
            (r"from\s+['\"]\./combat['\"]", "./combat"),
        ]
        for pat, label in forbidden_imports:
            if re.search(pat, src, flags=re.MULTILINE):
                ERR.append(f"tsx.forbidden_import:{label}")
        # Static check
        real_lines = [ln for ln in src.splitlines() if not ln.strip().startswith("//") and not ln.strip().startswith("*")]
        joined = "\n".join(real_lines)
        if re.search(r"\bfetch\(", joined): ERR.append("tsx.real_fetch_call")
        if re.search(r"\bAsyncStorage\.", joined): ERR.append("tsx.asyncstorage_call")
        if re.search(r"\baxios\.", joined): ERR.append("tsx.axios_call")
        if re.search(r"['\"]/api/", joined): ERR.append("tsx.api_path_literal")
        if re.search(r"process\.env\.", joined): ERR.append("tsx.process_env_use")
        # Labels v82 hardening
        for label in ("PREVIEW", "STAGING", "CANARY_LOCAL", "NOT LIVE REWARD", "DB_WRITES_0", "LOCAL_FILE_ONLY"):
            if label not in src:
                ERR.append(f"tsx.missing_label:{label}")
        # Hardening tokens
        for needle in ("status_snapshot", "local_file_writes", "observation_pass",
                       "live_db_readiness_design_gate", "v82 hardened",
                       "kvValueGood", "kvValueWarn", "StatusChip"):
            if needle not in src:
                ERR.append(f"tsx.missing_hardening_token:{needle}")
        # No duplicates: single StyleSheet.create, single export default
        if src.count("StyleSheet.create") != 1: ERR.append("tsx.stylesheet_create_count_not_1")
        if src.count("export default") != 1: ERR.append("tsx.export_default_count_not_1")
    if alpha_menu.exists():
        am_src = alpha_menu.read_text(encoding="utf-8")
        if "reward-claim-summary-preview" not in am_src:
            ERR.append("alpha_menu.missing_route_entry")
        if "v82 hardened" not in am_src:
            ERR.append("alpha_menu.missing_v82_label")
        for needle in ("local_file_writes_separate_counter", "live_db_readiness_design_only_no_apply",
                       "DB_WRITES_0", "LOCAL_FILE_ONLY"):
            if needle not in am_src:
                ERR.append(f"alpha_menu.missing_guardrail:{needle}")
    else:
        ERR.append("missing:alpha-menu-preview.tsx")
    if result:
        if result.get("typescript_pass") is not True: ERR.append("result.tsc_not_pass")
        if result.get("static_forbidden_check_pass") is not True:
            ERR.append("result.static_check_not_pass")
        if result.get("db_writes", 1) != 0: ERR.append("result.db_writes_nonzero")
    if static_data is None: ERR.append("missing:static_data")
    if marker is None: ERR.append("missing:marker")
    if ERR:
        print("FAIL reward_claim_ui_summary_preview_hardening:", "; ".join(ERR)); return 1
    print("PASS reward_claim_ui_summary_preview_hardening"); return 0

if __name__ == "__main__": sys.exit(main())
