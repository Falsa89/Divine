#!/usr/bin/env python3
"""PROJECT_D Track D validator (read-only).

Valida archiviazione DRIFT_DOC_3 (obsolete_pity_counter_format).
Exit 0 PASS / 1 FAIL.
"""
import json, sys
from pathlib import Path

MARKER = Path("/app/data/design/system_safety/project_d_drift_doc_3_archive_v1.json")
UPSTREAM_PLAN = Path("/app/data/design/system_safety/project_a_gacha_summon_drift_cleanup_plan_v1.json")


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_D_DRIFT_DOC_3_ARCHIVE_READY":
        fail(f"verdict mismatch: {m.get('verdict')}")
    if m.get("db_writes_executed") != 0: fail("db_writes_executed must be 0")
    if m.get("summon_behavior_mutated") is not False: fail("summon_behavior_mutated must be False")
    if m.get("gacha_behavior_mutated") is not False: fail("gacha_behavior_mutated must be False")
    if m.get("runtime_patch_applied") is not False: fail("runtime_patch_applied must be False")
    t = m.get("target_drift_doc", {})
    if t.get("id") != "DRIFT_DOC_3": fail("target id must be DRIFT_DOC_3")
    if t.get("class") != "obsolete_pity_counter_format": fail("target class mismatch")
    if t.get("action_per_v_a_plan") != "freeze_read_only": fail("action must be freeze_read_only per V_A plan")
    if t.get("data_mutation_required") is not False: fail("data_mutation_required must be False")
    arch = m.get("archive_action", {})
    if arch.get("status_after_project_d") != "KNOWN_NONBLOCKING_FROZEN_READ_ONLY_V1":
        fail("status_after_project_d mismatch")
    if arch.get("type") != "DOC_AUDIT_FREEZE_READ_ONLY":
        fail("archive_action.type must be DOC_AUDIT_FREEZE_READ_ONLY")
    res = m.get("residual_drift_docs_after_project_d", {})
    if res.get("total_drift_docs") != 7: fail("residual.total_drift_docs must be 7")
    if res.get("archived_count_after_project_d") != 3: fail("residual.archived_count_after_project_d must be 3")
    forb = m.get("forbidden_in_track_d_respected", {})
    for k in ("db_cleanup", "gacha_summon_behavior_change", "roster_mutation", "borea_activation", "banner_rate_pity_pool_change"):
        if forb.get(k) is not False: fail(f"forbidden_in_track_d.{k} must be False")
    if not UPSTREAM_PLAN.exists(): fail("upstream V_A plan missing")
    print("[PASS] PROJECT_D Track D DRIFT_DOC_3 freeze_read_only OK: 3/7 archived, no DB write, gacha/summon behavior intact")
    sys.exit(0)

if __name__ == "__main__": main()
