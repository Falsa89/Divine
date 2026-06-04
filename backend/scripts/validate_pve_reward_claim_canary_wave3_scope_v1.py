#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v81 Track A — Wave3 Scope Lock + UI Preview Contract."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    scope = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave3_scope_lock_v1.json")
    plan = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave3_plan_v1.json")
    ui_c = _load(ROOT / "data/design/economy/reward_claim_ui_summary_preview_shell_contract_v1.json")
    forb = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave3_forbidden_scope_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave3_scope_marker_v1.json")
    for name, obj in (("scope", scope), ("plan", plan), ("ui_c", ui_c), ("forb", forb), ("marker", marker)):
        if obj is None: ERR.append(f"missing:{name}")
    if scope:
        if scope.get("wave3_mode") != "local_file_based": ERR.append("scope.mode_invalid")
        if scope.get("max_wave3_users") != 5: ERR.append("scope.max_users_not_5")
        if scope.get("max_wave3_claims_total") != 5: ERR.append("scope.max_claims_total_not_5")
        if scope.get("ui_preview_shell") != "deeplink_only": ERR.append("scope.ui_preview_shell_invalid")
        for k in ("no_live_db", "no_real_reward_grant", "no_account_mutation",
                  "no_backend_route", "no_premium_currency", "no_gacha_shop_vip_bp",
                  "no_event_currency", "no_arena_ranking_reward",
                  "allowlist_alias_only", "rollback_required", "observation_required",
                  "kill_switch_required", "no_real_claim_button", "no_live_claim_endpoint"):
            if scope.get(k) is not True: ERR.append(f"scope.{k}_not_true")
        for k in ("mongo_url_used", "pymongo_used", "motor_used", "redis_used", "production_ui_exposure"):
            if scope.get(k) is not False: ERR.append(f"scope.{k}_not_false")
    if plan:
        if len(plan.get("plan", [])) != 5: ERR.append("plan.entries_not_5")
        if plan.get("max_users") != 5: ERR.append("plan.max_users_not_5")
        if "malformed_route_reject" not in plan.get("negative_tests", []):
            ERR.append("plan.missing_malformed_route_test")
    if ui_c:
        if ui_c.get("deeplink_only") is not True: ERR.append("ui_c.deeplink_only_not_true")
        if ui_c.get("production_ui_exposure") is not False: ERR.append("ui_c.production_ui_exposure_not_false")
        for k in ("no_real_claim_button", "no_backend_fetch", "no_async_storage",
                  "no_account_mutation", "no_db", "no_battle_engine_import",
                  "no_story_combat_import", "typescript_pass_required"):
            if ui_c.get(k) is not True: ERR.append(f"ui_c.{k}_not_true")
        for label in ("PREVIEW", "STAGING", "CANARY_LOCAL", "NOT LIVE REWARD"):
            if label not in ui_c.get("required_labels", []):
                ERR.append(f"ui_c.required_label_missing:{label}")
    if forb:
        forbidden = set(forb.get("forbidden_in_wave3", []))
        for k in ("live_db_writes", "mongo_url_use", "pymongo_import", "motor_import",
                  "redis_use", "backend_route_registration", "premium_currency",
                  "production_ui_exposure", "real_claim_button", "live_claim_endpoint",
                  "env_mutation", "fake_pass"):
            if k not in forbidden: ERR.append(f"forb.missing:{k}")
    if ERR:
        print("FAIL pve_reward_claim_canary_wave3_scope:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_canary_wave3_scope"); return 0

if __name__ == "__main__": sys.exit(main())
