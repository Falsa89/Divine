#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v85 Track D — Runbook (design-only)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    rb = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_canary_apply_runbook_v1.json")
    if rb is None:
        ERR.append("missing:runbook"); print("FAIL pve_reward_claim_live_db_canary_apply_runbook:", "; ".join(ERR)); return 1
    if rb.get("design_only") is not True: ERR.append("rb.design_only_not_true")
    if rb.get("environment") != "design_only_dry_run": ERR.append("rb.environment_invalid")
    if rb.get("db_writes") != 0: ERR.append("rb.db_writes_not_0")
    if rb.get("endpoint_implemented") is not False: ERR.append("rb.endpoint_implemented_not_false")
    if rb.get("applies_to_live") is not False: ERR.append("rb.applies_to_live_not_false")
    if rb.get("live_reward_grant") is not False: ERR.append("rb.live_reward_grant_not_false")
    if rb.get("target_population_max_users", 99) > 5: ERR.append("rb.target_population_max_users_gt_5")
    if rb.get("target_population_max_claims_total", 99) > 5: ERR.append("rb.target_population_max_claims_total_gt_5")
    phases = {p.get("phase") for p in rb.get("phases", [])}
    for req in ("P0_preflight", "P1_approval", "P2_observation_window_open",
                "P3_canary_design_apply", "P4_observe", "P5_decision",
                "P6_rollback_or_finalize"):
        if req not in phases: ERR.append(f"rb.missing_phase:{req}")
    halts = set(rb.get("halt_conditions", []))
    for req in ("any_md5_drift", "suite_required_fail_gt_0", "dry_run_regression",
                "kill_switch_engaged", "observation_metric_breach",
                "approval_window_expired", "checksum_mismatch_any_step",
                "endpoint_implementation_detected", "db_write_detected"):
        if req not in halts: ERR.append(f"rb.missing_halt:{req}")
    if ERR:
        print("FAIL pve_reward_claim_live_db_canary_apply_runbook:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_live_db_canary_apply_runbook"); return 0

if __name__ == "__main__": sys.exit(main())
