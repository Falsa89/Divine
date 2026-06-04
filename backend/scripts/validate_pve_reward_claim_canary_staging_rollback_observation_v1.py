#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v79 Track E — Staging Rollback Drill + Observation + Wave2."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e:
        ERR.append(f"unreadable:{p}:{e}")
        return None

def main():
    drill = _load(ROOT / "data/design/economy/pve_reward_claim_canary_staging_rollback_drill_result_v1.json")
    obs = _load(ROOT / "data/design/economy/pve_reward_claim_canary_staging_observation_result_v1.json")
    wave2 = _load(ROOT / "data/design/economy/pve_reward_claim_canary_staging_wave2_gate_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_canary_staging_rollback_observation_marker_v1.json")
    for name, obj in (("drill", drill), ("obs", obs), ("wave2", wave2), ("marker", marker)):
        if obj is None:
            ERR.append(f"missing:{name}")
    if drill:
        if drill.get("db_rollback") is not False:
            ERR.append("drill.db_rollback_not_false")
        if drill.get("db_writes", 1) != 0:
            ERR.append("drill.db_writes_nonzero")
    if obs:
        m = obs.get("metrics", {})
        if m.get("db_write_total") != 0:
            ERR.append("obs.db_write_total_nonzero")
        if m.get("live_reward_grant_total") != 0:
            ERR.append("obs.live_reward_grant_total_nonzero")
        if m.get("premium_reward_reject_total", 0) < 1:
            ERR.append("obs.premium_reward_reject_total_lt_1")
        if m.get("error_total", 0) != 0:
            ERR.append("obs.error_total_nonzero")
        if obs.get("observation_pass") is not True:
            ERR.append("obs.observation_pass_not_true")
    if wave2:
        if wave2.get("wave2_gate_ready") is not True:
            ERR.append("wave2.gate_ready_not_true")
        if wave2.get("db_writes", 1) != 0:
            ERR.append("wave2.db_writes_nonzero")
    if ERR:
        print("FAIL pve_reward_claim_canary_staging_rollback_observation:", "; ".join(ERR))
        return 1
    print("PASS pve_reward_claim_canary_staging_rollback_observation")
    return 0

if __name__ == "__main__":
    sys.exit(main())
