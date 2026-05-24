#!/usr/bin/env python3
"""
PROJECT_A Track G validator (read-only).

Verifica che il DoD tracker esista, abbia 7 rows, struttura consistente,
closed_items e pending_items popolati per ogni row, justification fields
presenti per progress/readiness estimates.

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

TRACKER = Path("/app/data/design/project_management/project_completion_dod_tracker_v1.json")
EXPECTED_AREAS = {"SLC/SLC-H", "AF2-N", "combat/skill/status", "economy/battle pass/shop",
                  "gacha/summon", "housing MVP", "QA/mobile/release"}


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not TRACKER.exists():
        fail(f"missing tracker: {TRACKER}")
    m = json.loads(TRACKER.read_text(encoding="utf-8"))

    if m.get("verdict") != "TRACK_G_QA_RELEASE_DOD_TRACKER_READY":
        fail(f"unexpected verdict: {m.get('verdict')}")

    rows = m.get("dod_rows", [])
    if len(rows) != 7:
        fail(f"expected 7 DoD rows, got {len(rows)}")

    areas = {r.get("area") for r in rows}
    if areas != EXPECTED_AREAS:
        fail(f"DoD rows areas mismatch: got {areas}, expected {EXPECTED_AREAS}")

    for r in rows:
        if not r.get("current_band"):
            fail(f"row '{r.get('area')}' missing current_band")
        if not r.get("target_band_for_ga"):
            fail(f"row '{r.get('area')}' missing target_band_for_ga")
        if not isinstance(r.get("closed_items"), list) or len(r.get("closed_items")) == 0:
            fail(f"row '{r.get('area')}' must have non-empty closed_items list")
        if not isinstance(r.get("pending_items"), list):
            fail(f"row '{r.get('area')}' must have pending_items list")
        if not r.get("next_apply_pack_candidate"):
            fail(f"row '{r.get('area')}' missing next_apply_pack_candidate")

    prog = m.get("global_progress_estimate", {})
    if not prog.get("justification"):
        fail("global_progress_estimate.justification missing")
    if not isinstance(prog.get("pre_project_a"), int) or not isinstance(prog.get("post_project_a"), int):
        fail("progress estimate must have integer pre/post values")

    rdy = m.get("slc_h_readiness_estimate", {})
    if not rdy.get("justification"):
        fail("slc_h_readiness_estimate.justification missing")

    print("[PASS] PROJECT_A Track G DoD tracker OK (7 rows, closed/pending items + justified estimates)")
    sys.exit(0)


if __name__ == "__main__":
    main()
