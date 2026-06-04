#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v80 Track F — Reward Claim UI Summary Gated Design."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    contract = _load(ROOT / "data/design/economy/reward_claim_ui_summary_gated_contract_v1.json")
    data_c = _load(ROOT / "data/design/economy/reward_claim_ui_summary_preview_data_contract_v1.json")
    forb = _load(ROOT / "data/design/economy/reward_claim_ui_summary_forbidden_scope_v1.json")
    marker = _load(ROOT / "data/design/economy/reward_claim_ui_summary_gated_marker_v1.json")
    for name, obj in (("contract", contract), ("data", data_c), ("forb", forb), ("marker", marker)):
        if obj is None: ERR.append(f"missing:{name}")
    if contract:
        if contract.get("design_only") is not True: ERR.append("contract.design_only_not_true")
        if contract.get("production_ui_exposure") is not False: ERR.append("contract.production_ui_exposure_not_false")
        if contract.get("no_real_reward_claim_button") is not True: ERR.append("contract.no_button_not_true")
        if contract.get("no_account_mutation") is not True: ERR.append("contract.no_account_mutation_not_true")
        if contract.get("no_db") is not True: ERR.append("contract.no_db_not_true")
        must_dist = contract.get("must_distinguish", {})
        if must_dist.get("preview_staging_reward_vs_live_reward") is not True:
            ERR.append("contract.must_distinguish_preview_vs_live_not_true")
    if data_c:
        if data_c.get("design_only") is not True: ERR.append("data.design_only_not_true")
        forbidden = set(data_c.get("forbidden_keys_in_preview", []))
        for k in ("premium_currency", "gacha_currency", "event_currency",
                  "arena_points", "vip_points", "battle_pass_xp"):
            if k not in forbidden: ERR.append(f"data.forbidden_missing:{k}")
    if forb:
        forbidden = set(forb.get("forbidden_in_ui_summary", []))
        for k in ("production_ui_exposure", "real_reward_claim_button",
                  "account_mutation_trigger", "db_write_trigger",
                  "premium_currency_display_as_grantable"):
            if k not in forbidden: ERR.append(f"forb.missing:{k}")
    if ERR:
        print("FAIL reward_claim_ui_summary_gated_design:", "; ".join(ERR)); return 1
    print("PASS reward_claim_ui_summary_gated_design"); return 0

if __name__ == "__main__": sys.exit(main())
