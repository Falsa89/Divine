#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v81 Track G — MEGA_RELEASE_ACCELERATION_30 v81 Rollup."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    rollup = _load(ROOT / "data/design/release_acceleration/mega_release_acceleration_30_v81_rollup_marker_v1.json")
    progress = _load(ROOT / "data/design/release_acceleration/alpha_readiness_progress_report_v25.json")
    qa = _load(ROOT / "data/design/qa/pve_reward_claim_canary_wave3_ui_preview_qa_matrix_v1.json")
    readiness = _load(ROOT / "data/design/release_acceleration/v81_to_v82_readiness_report_v1.json")
    if rollup is None: ERR.append("missing:rollup_marker")
    else:
        if rollup.get("verdict") != "MEGA_RELEASE_ACCELERATION_30_PVE_REWARD_CLAIM_CANARY_WAVE3_AND_UI_SUMMARY_PREVIEW_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING":
            ERR.append("rollup.verdict_invalid")
        if rollup.get("applied_to_live") is not False: ERR.append("rollup.applied_to_live_not_false")
        if rollup.get("db_writes", 1) != 0: ERR.append("rollup.db_writes_nonzero")
        if rollup.get("tag") != "PUBLIC_SYNC_TAG_v81_MEGA_RELEASE_ACCELERATION_30_PVE_REWARD_CLAIM_CANARY_WAVE3_UI":
            ERR.append("rollup.tag_invalid")
        if rollup.get("live_staging_gate_ready") is not True:
            ERR.append("rollup.live_staging_gate_ready_not_true")
    if progress:
        if progress.get("v81_canonical") != "pve_reward_claim_canary_wave3_and_ui_summary_preview":
            ERR.append("progress.v81_canonical_invalid")
        if progress.get("db_writes", 1) != 0: ERR.append("progress.db_writes_nonzero")
        if progress.get("production_ui_exposure") is not False:
            ERR.append("progress.production_ui_exposure_not_false")
        if progress.get("live_reward_grant") is not False:
            ERR.append("progress.live_reward_grant_not_false")
    if qa:
        if len(qa.get("matrix", [])) < 15: ERR.append("qa.matrix_too_few")
        for row in qa.get("matrix", []):
            if row.get("actual") != "PASS": ERR.append(f"qa.row_not_pass:{row.get('id')}")
        if qa.get("db_writes", 1) != 0: ERR.append("qa.db_writes_nonzero")
    if readiness:
        if readiness.get("applied_to_live") is not False:
            ERR.append("readiness.applied_to_live_not_false")
    docs_dir = ROOT / "docs/divine"
    for d in ("499_PVE_REWARD_CLAIM_CANARY_WAVE3_SCOPE.md",
              "500_PVE_REWARD_CLAIM_CANARY_WAVE3_FILES.md",
              "501_PVE_REWARD_CLAIM_CANARY_RUNNER_WAVE3.md",
              "502_PVE_REWARD_CLAIM_CANARY_WAVE3_APPLY_REPLAY.md",
              "503_PVE_REWARD_CLAIM_CANARY_WAVE3_OBSERVATION_LIVE_STAGING_GATE.md",
              "504_REWARD_CLAIM_UI_SUMMARY_PREVIEW_SHELL.md",
              "505_MEGA_RELEASE_ACCELERATION_30_PVE_REWARD_CLAIM_CANARY_WAVE3_UI_v81.md"):
        if not (docs_dir / d).exists(): ERR.append(f"missing_doc:{d}")
    if ERR:
        print("FAIL mega_release_acceleration_30_v81_rollup:", "; ".join(ERR)); return 1
    print("PASS mega_release_acceleration_30_v81_rollup"); return 0

if __name__ == "__main__": sys.exit(main())
