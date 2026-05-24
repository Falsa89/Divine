#!/usr/bin/env python3
"""PROJECT_E Track D validator: DRIFT_DOC_4 dedupe design freeze (read-only)."""
import json, sys
from pathlib import Path

MARKER = Path("/app/data/design/system_safety/project_e_drift_doc_4_archive_v1.json")


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_D_DRIFT_DOC_4_ARCHIVE_READY": fail("verdict mismatch")
    if m.get("db_writes_executed") != 0: fail("db_writes_executed must be 0")
    if m.get("summon_behavior_mutated") is not False: fail("summon_behavior_mutated must be False")
    t = m.get("target_drift_doc", {})
    if t.get("id") != "DRIFT_DOC_4": fail("target.id must be DRIFT_DOC_4")
    if t.get("class") != "duplicate_summon_log_format": fail("target.class mismatch")
    if t.get("action_per_v_a_plan") != "dedupe_design_required": fail("action mismatch")
    if t.get("data_mutation_executed_in_v_e") is not False: fail("data_mutation_executed_in_v_e must be False")
    arch = m.get("archive_action", {})
    if arch.get("status_after_project_e") != "KNOWN_NONBLOCKING_DEDUPE_DESIGN_FROZEN_V1": fail("archive status mismatch")
    steps = m.get("dedupe_design_steps", [])
    if len(steps) < 5: fail("dedupe_design_steps must have at least 5")
    res = m.get("residual_drift_docs_after_project_e", {})
    if res.get("total_drift_docs") != 7: fail("total_drift_docs must be 7")
    if res.get("archived_or_frozen_after_project_e") != 4: fail("archived_or_frozen_after_project_e must be 4")
    forb = m.get("forbidden_in_track_d_respected", {})
    for k in ("db_cleanup", "gacha_summon_behavior_change", "roster_mutation", "borea_activation", "banner_rate_pity_pool_change", "dedupe_execution"):
        if forb.get(k) is not False: fail(f"forbidden_in_track_d.{k} must be False")
    print("[PASS] PROJECT_E Track D DRIFT_DOC_4 dedupe design frozen OK: 4/7 processed; no DB cleanup; no dedupe execution")
    sys.exit(0)

if __name__ == "__main__": main()
