#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v84 Track E — Transaction / Auth / Endpoint / Kill-Switch Dry-Run."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    tx = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_dry_run_transaction_policy_result_v1.json")
    auth = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_dry_run_auth_guard_result_v1.json")
    ec = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_dry_run_endpoint_contract_result_v1.json")
    ks = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_dry_run_kill_switch_result_v1.json")

    for name, obj in (("tx", tx), ("auth", auth), ("ec", ec), ("ks", ks)):
        if obj is None: ERR.append(f"missing:{name}")

    if tx:
        if tx.get("db_writes") != 0: ERR.append("tx.db_writes_not_0")
        if tx.get("live_reward_grant") is not False: ERR.append("tx.live_reward_grant_not_false")
        if tx.get("endpoint_implemented") is not False: ERR.append("tx.endpoint_implemented_not_false")
        if tx.get("dry_run_only") is not True: ERR.append("tx.dry_run_only_not_true")
        if tx.get("applied_count", 0) < 1: ERR.append("tx.applied_count_zero")

    if auth:
        if auth.get("all_negative_cases_rejected") is not True: ERR.append("auth.negatives_not_all_rejected")
        if auth.get("happy_case_accepted") is not True: ERR.append("auth.happy_not_accepted")
        if auth.get("db_writes") != 0: ERR.append("auth.db_writes_not_0")
        if auth.get("endpoint_implemented") is not False: ERR.append("auth.endpoint_implemented_not_false")

    if ec:
        if ec.get("endpoint_contract_status") != "DESIGN_ONLY_NOT_IMPLEMENTED":
            ERR.append("ec.status_not_design_only")
        if ec.get("status_is_design_only") is not True: ERR.append("ec.status_is_design_only_not_true")
        if ec.get("route_present_in_server_py") is not False:
            ERR.append("ec.route_present_in_server_py_not_false")
        if ec.get("endpoint_implemented") is not False: ERR.append("ec.endpoint_implemented_not_false")
        if ec.get("all_reason_codes_covered_by_dry_run") is not True:
            ERR.append("ec.reason_codes_not_all_covered")
        if ec.get("db_writes") != 0: ERR.append("ec.db_writes_not_0")

    if ks:
        if ks.get("all_engage_cases_reject_all") is not True: ERR.append("ks.engage_not_reject_all")
        if ks.get("dual_approval_to_disengage_enforced") is not True:
            ERR.append("ks.dual_approval_disengage_not_enforced")
        if ks.get("db_writes") != 0: ERR.append("ks.db_writes_not_0")
        if ks.get("endpoint_implemented") is not False: ERR.append("ks.endpoint_implemented_not_false")

    if ERR:
        print("FAIL pve_reward_claim_live_db_dry_run_contract:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_live_db_dry_run_contract"); return 0

if __name__ == "__main__": sys.exit(main())
