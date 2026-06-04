#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v82 Track A — Wave4 Scope Lock + Live-Staging Boundary."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    scope = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave4_scope_lock_v1.json")
    plan = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave4_plan_v1.json")
    boundary = _load(ROOT / "data/design/economy/pve_reward_claim_live_staging_design_boundary_v1.json")
    forb = _load(ROOT / "data/design/economy/pve_reward_claim_wave4_forbidden_scope_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave4_scope_marker_v1.json")
    for name, obj in (("scope", scope), ("plan", plan), ("boundary", boundary), ("forb", forb), ("marker", marker)):
        if obj is None: ERR.append(f"missing:{name}")
    if scope:
        if scope.get("wave4_mode") != "local_file_based": ERR.append("scope.mode_invalid")
        if scope.get("max_wave4_users") != 8: ERR.append("scope.max_users_not_8")
        if scope.get("max_wave4_claims_total") != 8: ERR.append("scope.max_claims_total_not_8")
        if scope.get("live_staging_design_only") is not True: ERR.append("scope.live_staging_design_only_not_true")
        if scope.get("live_staging_db_apply_allowed") is not False: ERR.append("scope.live_staging_db_apply_allowed_not_false")
        for k in ("no_live_db", "no_real_reward_grant", "no_account_mutation",
                  "no_backend_route", "no_premium_currency", "no_real_claim_button",
                  "no_arena_ranking_reward", "allowlist_alias_only",
                  "rollback_required", "observation_required", "kill_switch_required"):
            if scope.get(k) is not True: ERR.append(f"scope.{k}_not_true")
        for k in ("mongo_url_used", "pymongo_used", "motor_used", "redis_used", "production_ui_exposure"):
            if scope.get(k) is not False: ERR.append(f"scope.{k}_not_false")
    if plan:
        if len(plan.get("plan", [])) != 8: ERR.append("plan.entries_not_8")
        if "event_arena_ranking_reward_reject" not in plan.get("negative_tests", []):
            ERR.append("plan.missing_event_arena_ranking_test")
    if boundary:
        if boundary.get("design_only") is not True: ERR.append("boundary.design_only_not_true")
        if boundary.get("live_db_apply_allowed") is not False: ERR.append("boundary.live_db_apply_allowed_not_false")
        if boundary.get("future_dedicated_pack_required") is not True:
            ERR.append("boundary.future_dedicated_pack_required_not_true")
    if forb:
        forbidden = set(forb.get("forbidden_in_wave4", []))
        for k in ("live_db_writes", "mongo_url_use", "pymongo_import", "redis_use",
                  "backend_route_registration", "premium_currency",
                  "arena_ranking_reward", "production_ui_exposure",
                  "real_claim_button", "env_mutation", "fake_pass"):
            if k not in forbidden: ERR.append(f"forb.missing:{k}")
    if ERR:
        print("FAIL pve_reward_claim_canary_wave4_scope:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_canary_wave4_scope"); return 0

if __name__ == "__main__": sys.exit(main())
