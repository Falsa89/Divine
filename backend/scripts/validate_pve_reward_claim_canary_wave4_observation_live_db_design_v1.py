#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v82 Track E — Wave4 Observation + Rollback Drill + Live-DB Readiness DESIGN Gate."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    obs = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave4_observation_result_v1.json")
    drill = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave4_rollback_drill_result_v1.json")
    live_gate = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_readiness_design_gate_v1.json")
    live_marker = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_readiness_design_marker_v1.json")
    for name, obj in (("obs", obs), ("drill", drill), ("live_gate", live_gate), ("live_marker", live_marker)):
        if obj is None: ERR.append(f"missing:{name}")
    if obs:
        m = obs.get("metrics", {})
        if m.get("db_write_total") != 0: ERR.append("obs.db_write_total_nonzero")
        if m.get("live_reward_grant_total") != 0: ERR.append("obs.live_reward_grant_total_nonzero")
        if m.get("premium_reward_reject_total", 0) < 1: ERR.append("obs.premium_reject_lt_1")
        if m.get("non_allowlisted_reject_total", 0) < 1: ERR.append("obs.non_allowlisted_reject_lt_1")
        if m.get("over_cap_reject_total", 0) < 1: ERR.append("obs.over_cap_reject_lt_1")
        if m.get("malformed_route_reject_total", 0) < 1: ERR.append("obs.malformed_route_reject_lt_1")
        if m.get("event_arena_ranking_reward_reject_total", 0) < 1:
            ERR.append("obs.event_arena_ranking_reward_reject_lt_1")
        if m.get("error_total", 0) != 0: ERR.append("obs.error_total_nonzero")
        if obs.get("observation_pass") is not True: ERR.append("obs.observation_pass_not_true")
    if drill:
        if drill.get("db_rollback") is not False: ERR.append("drill.db_rollback_not_false")
        if drill.get("db_writes", 1) != 0: ERR.append("drill.db_writes_nonzero")
        if drill.get("drill_executed") is not True: ERR.append("drill.not_executed")
        if drill.get("policy") != "sample_two_canary_tx": ERR.append("drill.policy_invalid")
    if live_gate:
        if live_gate.get("design_only") is not True: ERR.append("live_gate.design_only_not_true")
        if live_gate.get("live_db_apply_allowed") is not False:
            ERR.append("live_gate.live_db_apply_allowed_not_false")
        if live_gate.get("future_dedicated_pack_required") is not True:
            ERR.append("live_gate.future_dedicated_pack_required_not_true")
        if live_gate.get("db_writes", 1) != 0: ERR.append("live_gate.db_writes_nonzero")
        if live_gate.get("live_reward_grant") is not False:
            ERR.append("live_gate.live_reward_grant_not_false")
        required_items = ["db_transaction_policy", "real_account_allowlist", "auth_guard",
                          "endpoint_contract", "rollback_script", "observation_sink",
                          "hard_kill_switch", "manual_approval_and_checksum"]
        for it in required_items:
            if it not in live_gate.get("required_for_future_live_db_pack", []):
                ERR.append(f"live_gate.missing_required:{it}")
    if ERR:
        print("FAIL pve_reward_claim_canary_wave4_observation_live_db_design:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_canary_wave4_observation_live_db_design"); return 0

if __name__ == "__main__": sys.exit(main())
