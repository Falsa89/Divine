#!/usr/bin/env python3
"""PROJECT_C Track D validator (read-only).

Valida l'archiviazione del DRIFT_DOC_2 (deprecated_banner_legacy_pool) come
KNOWN_NONBLOCKING_ARCHIVED_V2. Nessuna mutazione DB attesa, nessun cambio
behavior summon/gacha.

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

MARKER = Path("/app/data/design/system_safety/project_c_drift_doc_2_archive_v1.json")
UPSTREAM_V_B = Path("/app/data/design/system_safety/project_b_drift_doc_1_legacy_summon_rate_archive_v1.json")
UPSTREAM_PLAN = Path("/app/data/design/system_safety/project_a_gacha_summon_drift_cleanup_plan_v1.json")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not MARKER.exists():
        fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_D_DRIFT_DOC_2_ARCHIVE_READY":
        fail(f"verdict mismatch: {m.get('verdict')}")
    if m.get("db_writes_executed") != 0:
        fail("db_writes_executed must be 0")
    if m.get("summon_behavior_mutated") is not False:
        fail("summon_behavior_mutated must be False")
    if m.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be False")
    target = m.get("target_drift_doc", {})
    if target.get("id") != "DRIFT_DOC_2":
        fail("target_drift_doc.id must be DRIFT_DOC_2")
    if target.get("class") != "deprecated_banner_legacy_pool":
        fail("target_drift_doc.class mismatch")
    if target.get("data_mutation_required") is not False:
        fail("target.data_mutation_required must be False")
    if target.get("behavior_mutation_required") is not False:
        fail("target.behavior_mutation_required must be False")
    arch = m.get("archive_action", {})
    if arch.get("status_after_project_c") != "KNOWN_NONBLOCKING_ARCHIVED_V2":
        fail("archive_action.status_after_project_c mismatch")
    residual = m.get("residual_drift_docs_after_project_c", {})
    if residual.get("total_drift_docs") != 7:
        fail("residual.total_drift_docs must be 7")
    if residual.get("archived_count_after_project_c") != 2:
        fail("residual.archived_count_after_project_c must be 2 (V_B->1 + V_C->1)")
    forb = m.get("forbidden_in_track_d_respected", {})
    for k in ("db_cleanup", "gacha_summon_behavior_change", "roster_mutation", "borea_activation"):
        if forb.get(k) is not False:
            fail(f"forbidden_in_track_d.{k} must be False")
    # Upstream coerenza
    if not UPSTREAM_V_B.exists():
        fail("upstream V_B Track D archive missing")
    vb = json.loads(UPSTREAM_V_B.read_text())
    if vb.get("target_drift_doc", {}).get("id") != "DRIFT_DOC_1":
        fail("V_B upstream not DRIFT_DOC_1 (chain broken)")
    if not UPSTREAM_PLAN.exists():
        fail("upstream V_A Track F plan missing")
    print("[PASS] PROJECT_C Track D DRIFT_DOC_2 archive OK: 2/7 archived, no DB write, summon behavior intact")
    sys.exit(0)


if __name__ == "__main__":
    main()
