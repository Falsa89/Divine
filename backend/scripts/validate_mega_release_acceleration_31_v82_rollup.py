#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v82 Track G — MEGA_RELEASE_ACCELERATION_31 v82 Rollup."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    rollup = _load(ROOT / "data/design/release_acceleration/mega_release_acceleration_31_v82_rollup_marker_v1.json")
    progress = _load(ROOT / "data/design/release_acceleration/alpha_readiness_progress_report_v26.json")
    qa = _load(ROOT / "data/design/qa/pve_reward_claim_canary_wave4_live_staging_ui_hardening_qa_matrix_v1.json")
    readiness = _load(ROOT / "data/design/release_acceleration/v82_to_v83_readiness_report_v1.json")
    if rollup is None: ERR.append("missing:rollup_marker")
    else:
        if rollup.get("verdict") != "MEGA_RELEASE_ACCELERATION_31_PVE_REWARD_CLAIM_WAVE4_LIVE_STAGING_DESIGN_AND_UI_HARDENING_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING":
            ERR.append("rollup.verdict_invalid")
        if rollup.get("applied_to_live") is not False: ERR.append("rollup.applied_to_live_not_false")
        if rollup.get("db_writes", 1) != 0: ERR.append("rollup.db_writes_nonzero")
        if rollup.get("tag") != "PUBLIC_SYNC_TAG_v82_MEGA_RELEASE_ACCELERATION_31_PVE_REWARD_CLAIM_WAVE4_LIVE_STAGING_UI":
            ERR.append("rollup.tag_invalid")
        if rollup.get("live_db_readiness_design_ready") is not True:
            ERR.append("rollup.live_db_readiness_design_ready_not_true")
        if rollup.get("ui_preview_shell_hardened") is not True:
            ERR.append("rollup.ui_preview_shell_hardened_not_true")
    if progress:
        if progress.get("v82_canonical") != "pve_reward_claim_wave4_live_staging_design_and_ui_hardening":
            ERR.append("progress.v82_canonical_invalid")
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
        if readiness.get("live_db_apply_active") is not False:
            ERR.append("readiness.live_db_apply_active_not_false")
    docs_dir = ROOT / "docs/divine"
    for d in ("506_PVE_REWARD_CLAIM_CANARY_WAVE4_SCOPE.md",
              "507_PVE_REWARD_CLAIM_CANARY_WAVE4_FILES.md",
              "508_PVE_REWARD_CLAIM_CANARY_RUNNER_WAVE4.md",
              "509_PVE_REWARD_CLAIM_CANARY_WAVE4_APPLY_REPLAY.md",
              "510_PVE_REWARD_CLAIM_LIVE_DB_READINESS_DESIGN_GATE.md",
              "511_REWARD_CLAIM_UI_SUMMARY_PREVIEW_HARDENING.md",
              "512_MEGA_RELEASE_ACCELERATION_31_PVE_REWARD_CLAIM_WAVE4_LIVE_STAGING_UI_v82.md"):
        if not (docs_dir / d).exists(): ERR.append(f"missing_doc:{d}")
    if ERR:
        print("FAIL mega_release_acceleration_31_v82_rollup:", "; ".join(ERR)); return 1
    print("PASS mega_release_acceleration_31_v82_rollup"); return 0

if __name__ == "__main__": sys.exit(main())
