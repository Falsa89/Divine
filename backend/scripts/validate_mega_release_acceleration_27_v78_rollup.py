#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v78 Track G — MEGA_RELEASE_ACCELERATION_27 v78 Rollup."""
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
    rollup = _load(ROOT / "data/design/release_acceleration/mega_release_acceleration_27_v78_rollup_marker_v1.json")
    if rollup is None:
        ERR.append("missing:rollup_marker")
    else:
        if rollup.get("verdict") != "MEGA_RELEASE_ACCELERATION_27_PVE_REWARD_CLAIM_CANARY_BLOCKED_NOT_APPLIED_SAFE_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING":
            ERR.append("rollup.verdict_invalid")
        if rollup.get("applied") is not False:
            ERR.append("rollup.applied_not_false")
        if rollup.get("db_writes", 1) != 0:
            ERR.append("rollup.db_writes_nonzero")
        if rollup.get("tag") != "PUBLIC_SYNC_TAG_v78_MEGA_RELEASE_ACCELERATION_27_PVE_REWARD_CLAIM_CANARY":
            ERR.append("rollup.tag_invalid")
    # Verifica presenza docs essenziali
    docs_dir = ROOT / "docs/divine"
    for d in ("478_v78_ROADMAP_REALIGNMENT_PVE_REWARD_CLAIM_CANARY.md",
              "479_PVE_REWARD_CLAIM_CONTRACT_SCHEMA.md",
              "480_PVE_REWARD_CLAIM_IDEMPOTENCY_LEDGER.md",
              "481_PVE_REWARD_CLAIM_CANARY_RUNNER.md",
              "482_PVE_REWARD_CLAIM_ROLLBACK_OBSERVATION.md",
              "483_PVE_REWARD_CLAIM_CANARY_QA_v78.md",
              "484_MEGA_RELEASE_ACCELERATION_27_PVE_REWARD_CLAIM_CANARY_v78.md"):
        if not (docs_dir / d).exists():
            ERR.append(f"missing_doc:{d}")
    if ERR:
        print("FAIL mega_release_acceleration_27_v78_rollup:", "; ".join(ERR))
        return 1
    print("PASS mega_release_acceleration_27_v78_rollup")
    return 0

if __name__ == "__main__":
    sys.exit(main())
