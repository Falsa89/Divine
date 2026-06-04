#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v79 Track G — MEGA_RELEASE_ACCELERATION_28 v79 Rollup."""
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
    rollup = _load(ROOT / "data/design/release_acceleration/mega_release_acceleration_28_v79_rollup_marker_v1.json")
    if rollup is None:
        ERR.append("missing:rollup_marker")
    else:
        accepted_verdicts = {
            "MEGA_RELEASE_ACCELERATION_28_PVE_REWARD_CLAIM_CANARY_LOCAL_STAGING_APPLIED_SAFE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING",
            "MEGA_RELEASE_ACCELERATION_28_PVE_REWARD_CLAIM_CANARY_STAGING_READY_BUT_APPLY_BLOCKED_SAFE_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING",
        }
        if rollup.get("verdict") not in accepted_verdicts:
            ERR.append("rollup.verdict_invalid")
        if rollup.get("applied_to_live") is not False:
            ERR.append("rollup.applied_to_live_not_false")
        if rollup.get("db_writes", 1) != 0:
            ERR.append("rollup.db_writes_nonzero")
        if rollup.get("tag") != "PUBLIC_SYNC_TAG_v79_MEGA_RELEASE_ACCELERATION_28_PVE_REWARD_CLAIM_CANARY_STAGING":
            ERR.append("rollup.tag_invalid")
    docs_dir = ROOT / "docs/divine"
    for d in ("485_PVE_REWARD_CLAIM_CANARY_STAGING_ENV.md",
              "486_PVE_REWARD_CLAIM_CANARY_STAGING_FILES.md",
              "487_PVE_REWARD_CLAIM_CANARY_RUNNER_LOCAL_STAGING.md",
              "488_PVE_REWARD_CLAIM_CANARY_LOCAL_APPLY.md",
              "489_PVE_REWARD_CLAIM_CANARY_STAGING_ROLLBACK_OBSERVATION.md",
              "490_PVE_REWARD_CLAIM_CANARY_STAGING_QA_v79.md",
              "491_MEGA_RELEASE_ACCELERATION_28_PVE_REWARD_CLAIM_CANARY_STAGING_v79.md"):
        if not (docs_dir / d).exists():
            ERR.append(f"missing_doc:{d}")
    if ERR:
        print("FAIL mega_release_acceleration_28_v79_rollup:", "; ".join(ERR))
        return 1
    print("PASS mega_release_acceleration_28_v79_rollup")
    return 0

if __name__ == "__main__":
    sys.exit(main())
