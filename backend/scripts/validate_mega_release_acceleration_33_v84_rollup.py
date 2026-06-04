#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v84 Rollup — MEGA_RELEASE_ACCELERATION_33 v84."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    rollup = _load(ROOT / "data/design/release_acceleration/mega_release_acceleration_33_v84_rollup_marker_v1.json")
    if rollup is None:
        ERR.append("missing:rollup_marker")
        print("FAIL mega_release_acceleration_33_v84_rollup:", "; ".join(ERR)); return 1
    expected = "MEGA_RELEASE_ACCELERATION_33_PVE_REWARD_CLAIM_LIVE_DB_DRY_RUN_AND_PUBLIC_SYNC_REPAIR_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    if rollup.get("verdict") != expected: ERR.append("rollup.verdict_invalid")
    if rollup.get("v83_public_sync_repair_done") is not True: ERR.append("rollup.v83_public_sync_repair_done_not_true")
    if rollup.get("live_db_dry_run_pass") is not True: ERR.append("rollup.live_db_dry_run_pass_not_true")
    if rollup.get("v85_gate_ready") is not True: ERR.append("rollup.v85_gate_ready_not_true")
    if rollup.get("db_writes") != 0: ERR.append("rollup.db_writes_not_0")
    if rollup.get("applied_to_live") is not False: ERR.append("rollup.applied_to_live_not_false")
    if rollup.get("endpoint_implemented") is not False: ERR.append("rollup.endpoint_implemented_not_false")
    if rollup.get("approval_checksum_sha256") != "86efe1aac64e15f6350be77e627cc37be3c122480cf8f86b1173781b3f464d54":
        ERR.append("rollup.approval_checksum_invalid")
    for f in (
        "data/design/economy/pve_reward_claim_live_db_dry_run_scope_lock_v1.json",
        "data/design/economy/pve_reward_claim_live_db_dry_run_scope_marker_v1.json",
        "data/design/economy/pve_reward_claim_live_db_dry_run_result_v1.json",
        "data/design/economy/pve_reward_claim_live_db_dry_run_transaction_policy_result_v1.json",
        "data/design/economy/pve_reward_claim_live_db_dry_run_auth_guard_result_v1.json",
        "data/design/economy/pve_reward_claim_live_db_dry_run_endpoint_contract_result_v1.json",
        "data/design/economy/pve_reward_claim_live_db_dry_run_kill_switch_result_v1.json",
        "data/design/economy/pve_reward_claim_live_db_dry_run_rollback_result_v1.json",
        "data/design/economy/pve_reward_claim_live_db_dry_run_observation_sink_result_v1.json",
        "data/design/economy/pve_reward_claim_v85_gate_v1.json",
        "data/canary_staging/live_db_dry_run_fixtures_v1.json",
        "data/design/release_acceleration/v83_public_sync_repair_marker_v1.json",
    ):
        if not (ROOT / f).exists(): ERR.append(f"missing_artifact:{f}")
    if ERR:
        print("FAIL mega_release_acceleration_33_v84_rollup:", "; ".join(ERR)); return 1
    print("PASS mega_release_acceleration_33_v84_rollup"); return 0

if __name__ == "__main__": sys.exit(main())
