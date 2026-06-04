#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v78 Track E — Rollback + Observation + Kill Switch."""
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
    rb = _load(ROOT / "data/design/economy/pve_reward_claim_canary_rollback_plan_v1.json")
    obs = _load(ROOT / "data/design/economy/pve_reward_claim_canary_observation_plan_v1.json")
    ks = _load(ROOT / "data/design/economy/pve_reward_claim_canary_kill_switch_policy_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_rollback_observation_marker_v1.json")
    for name, obj in (("rb", rb), ("obs", obs), ("ks", ks), ("marker", marker)):
        if obj is None:
            ERR.append(f"missing:{name}")
    if rb:
        if rb.get("rollback_token_required") is not True:
            ERR.append("rb.token_not_required")
        if rb.get("broad_rollback_allowed") is not False:
            ERR.append("rb.broad_allowed")
    if obs:
        if obs.get("observation_window_minutes") != 60:
            ERR.append("obs.window_not_60")
        metrics = set(obs.get("metrics", []))
        required_metrics = {"claim_attempts_total", "claim_success_total", "claim_reject_total",
                            "idempotent_replay_total", "duplicate_conflict_total",
                            "non_allowlisted_reject_total", "over_cap_reject_total",
                            "premium_reward_reject_total", "db_write_total",
                            "rollback_required_total", "error_total"}
        missing = required_metrics - metrics
        if missing:
            ERR.append(f"obs.missing_metrics:{sorted(missing)}")
    if ks:
        p0 = set(ks.get("p0_conditions", []))
        required_p0 = {"premium_reward_granted", "db_write_outside_allowlist",
                       "account_persistence_outside_canary", "duplicate_grant_conflict"}
        missing_p0 = required_p0 - p0
        if missing_p0:
            ERR.append(f"ks.missing_p0:{sorted(missing_p0)}")
    if ERR:
        print("FAIL pve_reward_claim_rollback_observation:", "; ".join(ERR))
        return 1
    print("PASS pve_reward_claim_rollback_observation")
    return 0

if __name__ == "__main__":
    sys.exit(main())
