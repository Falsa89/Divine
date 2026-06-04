#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v83 Rollup — MEGA_RELEASE_ACCELERATION_32 v83."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    rollup = _load(ROOT / "data/design/release_acceleration/mega_release_acceleration_32_v83_rollup_marker_v1.json")
    if rollup is None: ERR.append("missing:rollup_marker"); print("FAIL mega_release_acceleration_32_v83_rollup:", "; ".join(ERR)); return 1

    expected_verdict = "MEGA_RELEASE_ACCELERATION_32_PVE_REWARD_CLAIM_WAVE5_AND_LIVE_DB_DESIGN_CONTRACT_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    if rollup.get("verdict") != expected_verdict:
        ERR.append("rollup.verdict_invalid")
    if rollup.get("wave5_clean") is not True: ERR.append("rollup.wave5_clean_not_true")
    if rollup.get("live_db_design_contract_complete") is not True:
        ERR.append("rollup.live_db_design_contract_complete_not_true")
    if rollup.get("v84_go_no_go_gateway_ready") is not True:
        ERR.append("rollup.v84_go_no_go_gateway_ready_not_true")
    if rollup.get("db_writes") != 0: ERR.append("rollup.db_writes_not_0")
    if rollup.get("applied_to_live") is not False: ERR.append("rollup.applied_to_live_not_false")
    if rollup.get("approval_checksum_sha256") != "ce17d00a3e365bd4bf5efcad9aea43e51ad92c36e6301336aaaddf6229ce2f0a":
        ERR.append("rollup.approval_checksum_invalid")

    # Cross-check con i marker dei track
    for f in (
        "data/design/economy/pve_reward_claim_canary_wave5_scope_marker_v1.json",
        "data/design/economy/pve_reward_claim_canary_wave5_files_marker_v1.json",
        "data/design/economy/pve_reward_claim_canary_runner_wave5_marker_v1.json",
        "data/design/economy/pve_reward_claim_canary_wave5_apply_marker_v1.json",
        "data/design/economy/pve_reward_claim_canary_wave5_observation_result_v1.json",
        "data/design/economy/pve_reward_claim_canary_wave5_rollback_drill_result_v1.json",
        "data/design/economy/pve_reward_claim_v84_go_no_go_gateway_v1.json",
        "data/design/economy/pve_reward_claim_live_db_design_contract_v1.json",
        "data/design/economy/pve_reward_claim_live_db_design_contract_marker_v1.json",
    ):
        if not (ROOT / f).exists(): ERR.append(f"missing_artifact:{f}")

    if ERR:
        print("FAIL mega_release_acceleration_32_v83_rollup:", "; ".join(ERR)); return 1
    print("PASS mega_release_acceleration_32_v83_rollup"); return 0

if __name__ == "__main__": sys.exit(main())
