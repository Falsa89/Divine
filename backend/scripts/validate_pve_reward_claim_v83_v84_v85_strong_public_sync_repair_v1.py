#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v85 Track A — Strong Public Sync Repair v83/v84/v85."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    suite = ROOT / "backend/scripts/run_hero_skill_kit_validator_suite.py"
    if not suite.exists():
        ERR.append("missing:suite")
        print("FAIL pve_reward_claim_v83_v84_v85_strong_public_sync_repair:", "; ".join(ERR)); return 1
    src = suite.read_text(encoding="utf-8")
    required_tags = [
        "PUBLIC_SYNC_TAG_v82_MEGA_RELEASE_ACCELERATION_31_PVE_REWARD_CLAIM_WAVE4_LIVE_STAGING_UI",
        "PUBLIC_SYNC_TAG_v83_MEGA_RELEASE_ACCELERATION_32_PVE_REWARD_CLAIM_WAVE5_AND_LIVE_DB_DESIGN_CONTRACT",
        "PUBLIC_SYNC_TAG_v84_MEGA_RELEASE_ACCELERATION_33_PVE_REWARD_CLAIM_LIVE_DB_DRY_RUN_AND_PUBLIC_SYNC_REPAIR",
        "PUBLIC_SYNC_TAG_v85_MEGA_RELEASE_ACCELERATION_34_PVE_REWARD_CLAIM_LIVE_DB_CANARY_APPLY_DESIGN_AND_SYNC_REPAIR",
    ]
    sentinels = [
        "PUBLIC_SYNC_SENTINEL_v83_PRESENT=YES",
        "PUBLIC_SYNC_SENTINEL_v84_PRESENT=YES",
        "PUBLIC_SYNC_SENTINEL_v85_PRESENT=YES",
    ]
    for t in required_tags:
        if t not in src: ERR.append(f"suite.missing_tag:{t}")
    for s in sentinels:
        if s not in src: ERR.append(f"suite.missing_sentinel:{s}")
    required_tuples = [
        "MEGA-RELEASE-ACCELERATION-32-v83-ROLLUP",
        "MEGA-RELEASE-ACCELERATION-33-v84-ROLLUP",
        "MEGA-RELEASE-ACCELERATION-34-v85-ROLLUP",
        "PROJECT-PVE-REWARD-CLAIM-LIVE-DB-CANARY-APPLY-SCOPE",
        "PROJECT-PVE-REWARD-CLAIM-LIVE-DB-CANARY-APPLY-APPROVAL-WORKFLOW",
        "PROJECT-PVE-REWARD-CLAIM-LIVE-DB-CANARY-APPLY-RUNBOOK",
        "PROJECT-PVE-REWARD-CLAIM-LIVE-DB-CANARY-APPLY-STEP-UP-AUTH",
        "PROJECT-PVE-REWARD-CLAIM-LIVE-DB-CANARY-APPLY-DRILL",
    ]
    for t in required_tuples:
        if t not in src: ERR.append(f"suite.missing_tuple:{t}")
    repair_marker = _load(ROOT / "data/design/release_acceleration/v83_v84_v85_strong_public_sync_repair_marker_v1.json")
    if repair_marker is None: ERR.append("missing:repair_marker")
    else:
        if repair_marker.get("validator_weakening") is not False: ERR.append("repair.validator_weakening_not_false")
        if repair_marker.get("fake_pass") is not False: ERR.append("repair.fake_pass_not_false")
        if repair_marker.get("db_writes") != 0: ERR.append("repair.db_writes_not_0")
        for k, v in (("public_sync_tag_v82_present", True), ("public_sync_tag_v83_present", True),
                     ("public_sync_tag_v84_present", True), ("public_sync_tag_v85_present", True),
                     ("sentinel_v83_present", True), ("sentinel_v84_present", True), ("sentinel_v85_present", True)):
            if repair_marker.get(k) is not v: ERR.append(f"repair.{k}_not_{v}")
        if repair_marker.get("v84_commit_hash") != "3a56d734ed062698a6573f8751cd0162c1d74577":
            ERR.append("repair.v84_commit_hash_invalid")
    if ERR:
        print("FAIL pve_reward_claim_v83_v84_v85_strong_public_sync_repair:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_v83_v84_v85_strong_public_sync_repair"); return 0

if __name__ == "__main__": sys.exit(main())
