#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v83 Track A — Wave5 Scope Lock + Live-DB Design-Only Boundary."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    scope = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave5_scope_lock_v1.json")
    plan = _load(ROOT / "data/canary_staging/wave5_plan_v1.json")
    forb = _load(ROOT / "data/design/economy/pve_reward_claim_wave5_forbidden_scope_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave5_scope_marker_v1.json")
    for name, obj in (("scope", scope), ("plan", plan), ("forb", forb), ("marker", marker)):
        if obj is None: ERR.append(f"missing:{name}")
    if scope:
        if scope.get("wave5_mode") != "local_file_based": ERR.append("scope.mode_invalid")
        if scope.get("max_wave5_users") != 12: ERR.append("scope.max_users_not_12")
        if scope.get("max_wave5_claims_total") != 12: ERR.append("scope.max_claims_total_not_12")
        if scope.get("live_staging_design_only") is not True: ERR.append("scope.live_staging_design_only_not_true")
        if scope.get("live_staging_db_apply_allowed") is not False: ERR.append("scope.live_staging_db_apply_allowed_not_false")
        for k in ("no_live_db", "no_real_reward_grant", "no_account_mutation",
                  "no_backend_route", "no_premium_currency", "no_real_claim_button",
                  "no_arena_ranking_reward", "no_real_account_id",
                  "allowlist_alias_only", "rollback_required",
                  "observation_required", "kill_switch_required"):
            if scope.get(k) is not True: ERR.append(f"scope.{k}_not_true")
        for k in ("mongo_url_used", "pymongo_used", "motor_used", "redis_used", "production_ui_exposure"):
            if scope.get(k) is not False: ERR.append(f"scope.{k}_not_false")
    if plan:
        if len(plan.get("plan", [])) != 12: ERR.append("plan.entries_not_12")
        if "real_account_id_reject" not in plan.get("negative_tests", []):
            ERR.append("plan.missing_real_account_id_test")
        if "event_arena_ranking_reward_reject" not in plan.get("negative_tests", []):
            ERR.append("plan.missing_event_arena_ranking_test")
    if forb:
        forbidden = set(forb.get("forbidden_in_wave5", []))
        for k in ("live_db_writes", "mongo_url_use", "pymongo_import", "motor_import", "redis_use",
                  "backend_route_registration", "endpoint_implementation",
                  "premium_currency", "arena_ranking_reward",
                  "production_ui_exposure", "real_claim_button",
                  "real_account_id", "env_mutation", "fake_pass"):
            if k not in forbidden: ERR.append(f"forb.missing:{k}")
    if ERR:
        print("FAIL pve_reward_claim_canary_wave5_scope:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_canary_wave5_scope"); return 0

if __name__ == "__main__": sys.exit(main())
