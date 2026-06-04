#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v78 Track F — QA Matrix."""
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
    qa = _load(ROOT / "data/design/qa/pve_reward_claim_canary_qa_matrix_v1.json")
    progress = _load(ROOT / "data/design/release_acceleration/alpha_readiness_progress_report_v22_corrected.json")
    readiness = _load(ROOT / "data/design/release_acceleration/v78_to_v79_readiness_report_v1.json")
    marker = _load(ROOT / "data/design/qa/pve_reward_claim_canary_qa_marker_v1.json")
    for name, obj in (("qa", qa), ("progress", progress), ("readiness", readiness), ("marker", marker)):
        if obj is None:
            ERR.append(f"missing:{name}")
    if qa:
        if not qa.get("matrix"):
            ERR.append("qa.matrix_empty")
        if len(qa.get("matrix", [])) < 10:
            ERR.append("qa.matrix_too_few")
        if qa.get("db_writes", 1) != 0:
            ERR.append("qa.db_writes_nonzero")
    if progress:
        if progress.get("v78_canonical") != "pve_reward_claim_canary":
            ERR.append("progress.v78_canonical_invalid")
        if progress.get("roadmap_realigned") is not True:
            ERR.append("progress.roadmap_realigned_not_true")
        if progress.get("feedback_staging_pack") != "deferred":
            ERR.append("progress.feedback_staging_not_deferred")
        if progress.get("db_writes", 1) != 0:
            ERR.append("progress.db_writes_nonzero")
    if readiness:
        if readiness.get("applied") is not False:
            ERR.append("readiness.applied_not_false")
        if readiness.get("db_writes", 1) != 0:
            ERR.append("readiness.db_writes_nonzero")
    if ERR:
        print("FAIL pve_reward_claim_canary_qa:", "; ".join(ERR))
        return 1
    print("PASS pve_reward_claim_canary_qa")
    return 0

if __name__ == "__main__":
    sys.exit(main())
