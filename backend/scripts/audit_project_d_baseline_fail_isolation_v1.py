#!/usr/bin/env python3
"""PROJECT_D Track F audit (read-only).

Valida il marker baseline fail isolation:
- classifica un cluster monocausale di 8 fail (2 DEPRECATED + 6 TRANSITIVE_DEPRECATED)
- non indebolisce alcun validator
- non nasconde failures
- mantiene `required=false` per tutti i fail (OPTIONAL)
- conferma che gli 8 script falliti esistano ancora nella suite OPTIONAL
- valida topologia cluster (1 ROOT + 1 PROPAGATOR + 6 DOWNSTREAM)
Exit 0 PASS / 1 FAIL.
"""
import json, sys
from pathlib import Path

MARKER = Path("/app/data/design/system_safety/project_d_baseline_fail_isolation_v1.json")
SUITE_RUNNER = Path("/app/backend/scripts/run_hero_skill_kit_validator_suite.py")

EXPECTED_TASKS = {
    "SLC-C-REPO-PREFLIGHT", "SLC-C-COMBO",
    "SLC-D-PREFLIGHT", "SLC-D-COMBO",
    "SLC-BE-PREFLIGHT", "SLC-BE-COMBO",
    "SLC-F-PREFLIGHT", "SLC-F-COMBO",
}
EXPECTED_SCRIPT_NAMES = (
    "audit_slc_c_repo_multishard_preflight.py",
    "validate_slc_c_combo_v1.py",
    "validate_slc_d_preflight_v1.py",
    "validate_slc_d_merge_tooling_combo_v1.py",
    "validate_slc_be_preflight_v1.py",
    "validate_slc_be_server_profile_selection_combo.py",
    "validate_slc_f_preflight_v1.py",
    "validate_slc_f_route_patch_dryrun_combo_v1.py",
)


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_F_BASELINE_FAIL_ISOLATION_READY":
        fail("verdict mismatch")
    if m.get("validator_weakening") is not False: fail("validator_weakening must be False")
    if m.get("hidden_failures") is not False: fail("hidden_failures must be False")
    if m.get("required_section_changed") is not False: fail("required_section_changed must be False")
    if m.get("fake_pass_marked") is not False: fail("fake_pass_marked must be False")

    fails = m.get("known_baseline_failures", [])
    if len(fails) != 8: fail(f"expected 8 baseline failures, got {len(fails)}")
    ids = {x.get("task_id") for x in fails}
    if ids != EXPECTED_TASKS:
        fail(f"unexpected fail set: {ids}")
    for x in fails:
        if x.get("required") is not False: fail(f"{x.get('task_id')} required must be False (OPTIONAL)")
        cl = x.get("classification")
        if cl not in ("DEPRECATED_VALIDATOR", "TRANSITIVE_DEPRECATED_VALIDATOR"):
            fail(f"{x.get('task_id')} classification must be DEPRECATED_VALIDATOR or TRANSITIVE_DEPRECATED_VALIDATOR")
        if x.get("impact_runtime") != "NONE":
            fail(f"{x.get('task_id')} impact_runtime must be NONE")
        if x.get("cluster_role") not in ("ROOT", "PROPAGATOR", "DOWNSTREAM"):
            fail(f"{x.get('task_id')} cluster_role invalid: {x.get('cluster_role')}")

    sm = m.get("summary_classification", {})
    if sm.get("DEPRECATED_VALIDATOR") != 2: fail("summary DEPRECATED_VALIDATOR must be 2")
    if sm.get("TRANSITIVE_DEPRECATED_VALIDATOR") != 6: fail("summary TRANSITIVE_DEPRECATED_VALIDATOR must be 6")
    if sm.get("NEEDS_FIX") != 0: fail("summary NEEDS_FIX must be 0")
    if sm.get("BLOCKER") != 0: fail("summary BLOCKER must be 0")
    if sm.get("SAFE_TO_REBASELINE") != 0: fail("summary SAFE_TO_REBASELINE must be 0")

    topo = m.get("cluster_topology", {})
    if topo.get("ROOT") != ["SLC-C-REPO-PREFLIGHT"]: fail("cluster_topology.ROOT must be [SLC-C-REPO-PREFLIGHT]")
    if topo.get("PROPAGATOR") != ["SLC-C-COMBO"]: fail("cluster_topology.PROPAGATOR must be [SLC-C-COMBO]")
    if len(topo.get("DOWNSTREAM", [])) != 6: fail("cluster_topology.DOWNSTREAM must have 6 entries")

    plan = m.get("rebaseline_plan", {})
    for ph in ("phase_1_v_d", "phase_2_v_e", "phase_3_v_f", "phase_4_v_g"):
        if ph not in plan: fail(f"rebaseline_plan missing {ph}")

    # Tutti gli script devono essere ancora REGISTRATI nella suite OPTIONAL (no-hiding).
    if not SUITE_RUNNER.exists(): fail("suite runner missing")
    src = SUITE_RUNNER.read_text()
    for script_name in EXPECTED_SCRIPT_NAMES:
        if script_name not in src:
            fail(f"baseline fail script {script_name} REMOVED from suite — violates non-hiding invariant")

    print("[PASS] PROJECT_D Track F baseline fail isolation OK: 8 fail in cluster monocausale (2 DEPRECATED + 6 TRANSITIVE); not hidden; 4-phase rebaseline plan defined")
    sys.exit(0)

if __name__ == "__main__": main()
