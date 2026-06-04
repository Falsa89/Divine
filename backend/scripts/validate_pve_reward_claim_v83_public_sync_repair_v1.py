#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v84 Track A — v83 Public Sync Repair."""
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
        ERR.append("missing:suite"); print("FAIL pve_reward_claim_v83_public_sync_repair:", "; ".join(ERR)); return 1
    src = suite.read_text(encoding="utf-8")
    required_tags = [
        "PUBLIC_SYNC_TAG_v82_MEGA_RELEASE_ACCELERATION_31_PVE_REWARD_CLAIM_WAVE4_LIVE_STAGING_UI",
        "PUBLIC_SYNC_TAG_v83_MEGA_RELEASE_ACCELERATION_32_PVE_REWARD_CLAIM_WAVE5_AND_LIVE_DB_DESIGN_CONTRACT",
        "PUBLIC_SYNC_TAG_v84_MEGA_RELEASE_ACCELERATION_33_PVE_REWARD_CLAIM_LIVE_DB_DRY_RUN_AND_PUBLIC_SYNC_REPAIR",
    ]
    for t in required_tags:
        if t not in src: ERR.append(f"suite.missing_tag:{t}")
    required_tuples = [
        "MEGA-RELEASE-ACCELERATION-31-v82-ROLLUP",
        "MEGA-RELEASE-ACCELERATION-32-v83-ROLLUP",
        "MEGA-RELEASE-ACCELERATION-33-v84-ROLLUP",
        "PROJECT-PVE-REWARD-CLAIM-CANARY-WAVE5-SCOPE",
        "PROJECT-PVE-REWARD-CLAIM-LIVE-DB-DESIGN-CONTRACT",
        "PROJECT-PVE-REWARD-CLAIM-LIVE-DB-DRY-RUN-SIMULATOR",
    ]
    for t in required_tuples:
        if t not in src: ERR.append(f"suite.missing_tuple:{t}")
    repair_marker = _load(ROOT / "data/design/release_acceleration/v83_public_sync_repair_marker_v1.json")
    if repair_marker is None: ERR.append("missing:repair_marker")
    else:
        if repair_marker.get("validator_weakening") is not False:
            ERR.append("repair_marker.validator_weakening_not_false")
        if repair_marker.get("db_writes") != 0: ERR.append("repair_marker.db_writes_not_0")
        if repair_marker.get("v83_commit_hash") != "1d58234691f84523d324ff4c62e65b9ce5f799e6":
            ERR.append("repair_marker.v83_commit_hash_invalid")
    if ERR:
        print("FAIL pve_reward_claim_v83_public_sync_repair:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_v83_public_sync_repair"); return 0

if __name__ == "__main__": sys.exit(main())
