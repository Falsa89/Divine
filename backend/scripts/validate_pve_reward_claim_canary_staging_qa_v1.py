#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v79 Track F — QA Matrix + Progress + Readiness."""
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
    qa = _load(ROOT / "data/design/qa/pve_reward_claim_canary_staging_qa_matrix_v1.json")
    progress = _load(ROOT / "data/design/release_acceleration/alpha_readiness_progress_report_v23.json")
    readiness = _load(ROOT / "data/design/release_acceleration/v79_to_v80_readiness_report_v1.json")
    marker = _load(ROOT / "data/design/qa/pve_reward_claim_canary_staging_qa_marker_v1.json")
    for name, obj in (("qa", qa), ("progress", progress), ("readiness", readiness), ("marker", marker)):
        if obj is None:
            ERR.append(f"missing:{name}")
    if qa:
        matrix = qa.get("matrix", [])
        if len(matrix) < 10:
            ERR.append("qa.matrix_too_few")
        if qa.get("db_writes", 1) != 0:
            ERR.append("qa.db_writes_nonzero")
        for row in matrix:
            if row.get("actual") != "PASS":
                ERR.append(f"qa.row_not_pass:{row.get('id')}")
    if progress:
        if progress.get("v79_canonical") != "pve_reward_claim_canary_staging_setup":
            ERR.append("progress.v79_canonical_invalid")
        if progress.get("db_writes", 1) != 0:
            ERR.append("progress.db_writes_nonzero")
        if progress.get("live_reward_grant") is not False:
            ERR.append("progress.live_reward_grant_not_false")
    if readiness:
        if readiness.get("applied_to_live") is not False:
            ERR.append("readiness.applied_to_live_not_false")
        if readiness.get("db_writes", 1) != 0:
            ERR.append("readiness.db_writes_nonzero")
    if ERR:
        print("FAIL pve_reward_claim_canary_staging_qa:", "; ".join(ERR))
        return 1
    print("PASS pve_reward_claim_canary_staging_qa")
    return 0

if __name__ == "__main__":
    sys.exit(main())
