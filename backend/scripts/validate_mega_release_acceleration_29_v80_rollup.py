#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v80 Track G — MEGA_RELEASE_ACCELERATION_29 v80 Rollup."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    rollup = _load(ROOT / "data/design/release_acceleration/mega_release_acceleration_29_v80_rollup_marker_v1.json")
    if rollup is None: ERR.append("missing:rollup_marker")
    else:
        accepted_verdicts = {
            "MEGA_RELEASE_ACCELERATION_29_PVE_REWARD_CLAIM_CANARY_WAVE2_OBSERVED_SAFE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING",
            "MEGA_RELEASE_ACCELERATION_29_PVE_REWARD_CLAIM_CANARY_WAVE2_BLOCKED_SAFE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING",
        }
        if rollup.get("verdict") not in accepted_verdicts: ERR.append("rollup.verdict_invalid")
        if rollup.get("applied_to_live") is not False: ERR.append("rollup.applied_to_live_not_false")
        if rollup.get("db_writes", 1) != 0: ERR.append("rollup.db_writes_nonzero")
        if rollup.get("tag") != "PUBLIC_SYNC_TAG_v80_MEGA_RELEASE_ACCELERATION_29_PVE_REWARD_CLAIM_CANARY_WAVE2":
            ERR.append("rollup.tag_invalid")
    docs_dir = ROOT / "docs/divine"
    for d in ("492_PVE_REWARD_CLAIM_CANARY_WAVE2_SCOPE.md",
              "493_PVE_REWARD_CLAIM_CANARY_WAVE2_FILES.md",
              "494_PVE_REWARD_CLAIM_CANARY_RUNNER_WAVE2.md",
              "495_PVE_REWARD_CLAIM_CANARY_WAVE2_APPLY_REPLAY.md",
              "496_PVE_REWARD_CLAIM_CANARY_WAVE2_OBSERVATION_ROLLBACK.md",
              "497_REWARD_CLAIM_UI_SUMMARY_GATED_DESIGN.md",
              "498_MEGA_RELEASE_ACCELERATION_29_PVE_REWARD_CLAIM_CANARY_WAVE2_v80.md"):
        if not (docs_dir / d).exists(): ERR.append(f"missing_doc:{d}")
    if ERR:
        print("FAIL mega_release_acceleration_29_v80_rollup:", "; ".join(ERR)); return 1
    print("PASS mega_release_acceleration_29_v80_rollup"); return 0

if __name__ == "__main__": sys.exit(main())
