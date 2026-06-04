#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v84 Track F — Rollback + Observation Sink Dry-Run + v85 Gate."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    rb = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_dry_run_rollback_result_v1.json")
    obs = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_dry_run_observation_sink_result_v1.json")
    gate = _load(ROOT / "data/design/economy/pve_reward_claim_v85_gate_v1.json")

    for name, obj in (("rb", rb), ("obs", obs), ("gate", gate)):
        if obj is None: ERR.append(f"missing:{name}")

    if rb:
        if rb.get("db_rollback") is not False: ERR.append("rb.db_rollback_not_false")
        if rb.get("db_writes") != 0: ERR.append("rb.db_writes_not_0")
        if rb.get("endpoint_implemented") is not False: ERR.append("rb.endpoint_implemented_not_false")
        if rb.get("dry_run_only") is not True: ERR.append("rb.dry_run_only_not_true")
        if rb.get("sampled_count", 0) < 1: ERR.append("rb.sampled_count_zero")
        if rb.get("requires_admin_dual_approval") is not True:
            ERR.append("rb.requires_admin_dual_approval_not_true")

    if obs:
        if obs.get("all_required_metrics_covered") is not True:
            ERR.append("obs.all_required_metrics_covered_not_true")
        if obs.get("redact_pii_enforced") is not True:
            ERR.append("obs.redact_pii_enforced_not_true")
        if obs.get("db_writes") != 0: ERR.append("obs.db_writes_not_0")
        if obs.get("endpoint_implemented") is not False:
            ERR.append("obs.endpoint_implemented_not_false")
        if obs.get("dry_run_only") is not True: ERR.append("obs.dry_run_only_not_true")

    if gate:
        if gate.get("dry_run_pass") is not True: ERR.append("gate.dry_run_pass_not_true")
        if gate.get("live_db_apply_allowed") is not False: ERR.append("gate.live_db_apply_allowed_not_false")
        if gate.get("endpoint_implemented") is not False: ERR.append("gate.endpoint_implemented_not_false")
        if gate.get("db_writes") != 0: ERR.append("gate.db_writes_not_0")
        if gate.get("manual_approval_required_for_future_apply") is not True:
            ERR.append("gate.manual_approval_required_not_true")
        if gate.get("checksum_required_for_future_apply") is not True:
            ERR.append("gate.checksum_required_not_true")
        if not gate.get("v85_recommendation"):
            ERR.append("gate.v85_recommendation_missing")

    if ERR:
        print("FAIL pve_reward_claim_live_db_dry_run_rollback_observation:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_live_db_dry_run_rollback_observation"); return 0

if __name__ == "__main__": sys.exit(main())
