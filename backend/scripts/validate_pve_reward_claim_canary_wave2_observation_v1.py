#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v80 Track E — Wave2 Observation + Rollback Drill + Wave3 Gate."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    obs = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave2_observation_result_v1.json")
    drill = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave2_rollback_drill_result_v1.json")
    wave3 = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave3_gate_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave2_observation_marker_v1.json")
    for name, obj in (("obs", obs), ("drill", drill), ("wave3", wave3), ("marker", marker)):
        if obj is None: ERR.append(f"missing:{name}")
    if obs:
        m = obs.get("metrics", {})
        if m.get("db_write_total") != 0: ERR.append("obs.db_write_total_nonzero")
        if m.get("live_reward_grant_total") != 0: ERR.append("obs.live_reward_grant_total_nonzero")
        if m.get("premium_reward_reject_total", 0) < 1: ERR.append("obs.premium_reject_lt_1")
        if m.get("non_allowlisted_reject_total", 0) < 1: ERR.append("obs.non_allowlisted_reject_lt_1")
        if m.get("over_cap_reject_total", 0) < 1: ERR.append("obs.over_cap_reject_lt_1")
        if m.get("error_total", 0) != 0: ERR.append("obs.error_total_nonzero")
        if obs.get("observation_pass") is not True: ERR.append("obs.observation_pass_not_true")
    if drill:
        if drill.get("db_rollback") is not False: ERR.append("drill.db_rollback_not_false")
        if drill.get("db_writes", 1) != 0: ERR.append("drill.db_writes_nonzero")
        if drill.get("drill_executed") is not True: ERR.append("drill.not_executed")
    if wave3:
        if wave3.get("wave3_gate_ready") is not True: ERR.append("wave3.gate_ready_not_true")
        if wave3.get("db_writes", 1) != 0: ERR.append("wave3.db_writes_nonzero")
        if wave3.get("live_reward_grant") is not False: ERR.append("wave3.live_reward_grant_not_false")
    if ERR:
        print("FAIL pve_reward_claim_canary_wave2_observation:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_canary_wave2_observation"); return 0

if __name__ == "__main__": sys.exit(main())
