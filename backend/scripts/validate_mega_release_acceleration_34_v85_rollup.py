#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v85 Rollup — MEGA_RELEASE_ACCELERATION_34 v85."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    rollup = _load(ROOT / "data/design/release_acceleration/mega_release_acceleration_34_v85_rollup_marker_v1.json")
    if rollup is None:
        ERR.append("missing:rollup_marker")
        print("FAIL mega_release_acceleration_34_v85_rollup:", "; ".join(ERR)); return 1
    expected = "MEGA_RELEASE_ACCELERATION_34_PVE_REWARD_CLAIM_LIVE_DB_CANARY_APPLY_DESIGN_AND_SYNC_REPAIR_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    if rollup.get("verdict") != expected: ERR.append("rollup.verdict_invalid")
    if rollup.get("strong_public_sync_repair_done") is not True: ERR.append("rollup.strong_public_sync_repair_done_not_true")
    if rollup.get("canary_apply_design_complete") is not True: ERR.append("rollup.canary_apply_design_complete_not_true")
    if rollup.get("v86_gate_ready") is not True: ERR.append("rollup.v86_gate_ready_not_true")
    if rollup.get("db_writes") != 0: ERR.append("rollup.db_writes_not_0")
    if rollup.get("applied_to_live") is not False: ERR.append("rollup.applied_to_live_not_false")
    if rollup.get("endpoint_implemented") is not False: ERR.append("rollup.endpoint_implemented_not_false")
    if rollup.get("live_db_apply_allowed") is not False: ERR.append("rollup.live_db_apply_allowed_not_false")
    if rollup.get("approval_checksum_sha256") != "5fa9c8c25fb9ef177402163db663c625aa66125d8007d5864ff8adb74e0ef6b5":
        ERR.append("rollup.approval_checksum_invalid")
    for f in (
        "data/design/economy/pve_reward_claim_live_db_canary_apply_scope_lock_v1.json",
        "data/design/economy/pve_reward_claim_live_db_canary_apply_scope_marker_v1.json",
        "data/design/economy/pve_reward_claim_live_db_canary_apply_approval_workflow_v1.json",
        "data/design/economy/pve_reward_claim_live_db_canary_apply_checksum_sequence_v1.json",
        "data/design/economy/pve_reward_claim_live_db_canary_apply_runbook_v1.json",
        "data/design/economy/pve_reward_claim_live_db_canary_apply_step_up_auth_endpoint_stub_v1.json",
        "data/design/economy/pve_reward_claim_live_db_canary_apply_kill_switch_drill_result_v1.json",
        "data/design/economy/pve_reward_claim_live_db_canary_apply_rollback_chain_drill_result_v1.json",
        "data/design/economy/pve_reward_claim_live_db_canary_apply_drill_rollup_v1.json",
        "data/design/economy/pve_reward_claim_v86_gate_v1.json",
        "data/design/release_acceleration/v83_v84_v85_strong_public_sync_repair_marker_v1.json",
    ):
        if not (ROOT / f).exists(): ERR.append(f"missing_artifact:{f}")
    if ERR:
        print("FAIL mega_release_acceleration_34_v85_rollup:", "; ".join(ERR)); return 1
    print("PASS mega_release_acceleration_34_v85_rollup"); return 0

if __name__ == "__main__": sys.exit(main())
