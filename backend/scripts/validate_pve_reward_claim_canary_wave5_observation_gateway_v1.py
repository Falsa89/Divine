#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v83 Track E — Wave5 Observation + Rollback Drill + Go/No-Go v84."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    obs = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave5_observation_result_v1.json")
    drill = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave5_rollback_drill_result_v1.json")
    gateway = _load(ROOT / "data/design/economy/pve_reward_claim_v84_go_no_go_gateway_v1.json")

    for name, obj in (("obs", obs), ("drill", drill), ("gateway", gateway)):
        if obj is None: ERR.append(f"missing:{name}")

    if obs:
        if obs.get("observation_pass") is not True: ERR.append("obs.observation_pass_not_true")
        pc = obs.get("pass_criteria", {})
        for k in ("db_write_total_zero", "live_reward_grant_total_zero",
                  "premium_reward_reject_at_least_one",
                  "non_allowlisted_reject_at_least_one",
                  "over_cap_reject_at_least_one",
                  "malformed_route_reject_at_least_one",
                  "event_arena_ranking_reward_reject_at_least_one",
                  "real_account_id_reject_at_least_one",
                  "no_critical_errors"):
            if pc.get(k) is not True: ERR.append(f"obs.pc.{k}_not_true")
        if obs.get("metrics", {}).get("db_write_total", -1) != 0:
            ERR.append("obs.metrics.db_write_total_not_0")
        if obs.get("metrics", {}).get("live_reward_grant_total", -1) != 0:
            ERR.append("obs.metrics.live_reward_grant_total_not_0")

    if drill:
        if drill.get("db_rollback") is not False: ERR.append("drill.db_rollback_not_false")
        if drill.get("db_writes") != 0: ERR.append("drill.db_writes_not_0")
        if drill.get("drill_executed") is not True: ERR.append("drill.drill_executed_not_true")
        if drill.get("policy") != "sample_three_canary_tx": ERR.append("drill.policy_invalid")
        if drill.get("rolled_back_count", 0) < 1: ERR.append("drill.rolled_back_count_zero")

    if gateway:
        if gateway.get("live_db_apply_allowed") is not False:
            ERR.append("gateway.live_db_apply_allowed_not_false")
        if gateway.get("endpoint_implemented") is not False:
            ERR.append("gateway.endpoint_implemented_not_false")
        if gateway.get("db_writes") != 0: ERR.append("gateway.db_writes_not_0")
        if gateway.get("manual_approval_required_for_future_apply") is not True:
            ERR.append("gateway.manual_approval_required_not_true")
        if not gateway.get("v84_recommendation"):
            ERR.append("gateway.v84_recommendation_missing")

    if ERR:
        print("FAIL pve_reward_claim_canary_wave5_observation_gateway:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_canary_wave5_observation_gateway"); return 0

if __name__ == "__main__": sys.exit(main())
