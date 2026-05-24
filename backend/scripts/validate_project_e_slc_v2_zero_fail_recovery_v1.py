#!/usr/bin/env python3
"""PROJECT_E Track A validator — zero-fail recovery (read-only).

Valida che:
  - tutti gli 8 v2 successor scripts esistano
  - i v1 quarantinati siano ancora REGISTRATI in OPTIONAL (no-hiding)
  - il suite runner abbia il blocco SUPERSEDED_AFTER_PROJECT_E_V2 gated da SUITE_KEEP_DEPRECATED_AUDITS
  - in live env (SUITE_KEEP_DEPRECATED_AUDITS unset) i v1 sono SUPERSEDED
  - il marker JSON con verdict atteso e hard_invariants True
"""
import json, os, sys
from pathlib import Path

MARKER = Path("/app/data/design/system_safety/project_e_slc_v2_zero_fail_recovery_result_v1.json")
SCRIPTS = Path("/app/backend/scripts")
RUNNER = Path("/app/backend/scripts/run_hero_skill_kit_validator_suite.py")
V2_SCRIPTS = (
    "validate_slc_c_repo_multishard_post_g_invariant_v2.py",
    "validate_slc_c_combo_v2.py",
    "validate_slc_d_preflight_v2.py",
    "validate_slc_d_merge_tooling_combo_v2.py",
    "validate_slc_be_preflight_v2.py",
    "validate_slc_be_server_profile_selection_combo_v2.py",
    "validate_slc_f_preflight_v2.py",
    "validate_slc_f_route_patch_dryrun_combo_v2.py",
)
V1_SCRIPTS = (
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
    if m.get("verdict") != "TRACK_A_SLC_V2_ZERO_FAIL_RECOVERY_APPLIED_SAFE":
        fail(f"verdict mismatch: {m.get('verdict')}")
    hi = m.get("hard_invariants", {})
    for k in ("no_required_weakening", "no_hidden_failures", "no_fake_pass", "no_evidence_deletion", "v1_scripts_still_present_on_disk", "v1_entries_still_in_OPTIONAL_list"):
        if hi.get(k) is not True: fail(f"hard_invariants.{k} must be True")
    # v2 scripts present
    for s in V2_SCRIPTS:
        if not (SCRIPTS / s).exists(): fail(f"v2 successor missing: {s}")
    # v1 scripts STILL PRESENT (no evidence deletion)
    for s in V1_SCRIPTS:
        if not (SCRIPTS / s).exists(): fail(f"v1 script REMOVED (evidence deletion violation): {s}")
    # v1 entries STILL in OPTIONAL
    src = RUNNER.read_text()
    for s in V1_SCRIPTS:
        if s not in src: fail(f"v1 entry REMOVED from OPTIONAL (hiding violation): {s}")
    # SUPERSEDED block present
    if "SUPERSEDED_AFTER_PROJECT_E_V2" not in src: fail("SUPERSEDED_AFTER_PROJECT_E_V2 not present in suite runner")
    if "SUITE_KEEP_DEPRECATED_AUDITS" not in src: fail("SUITE_KEEP_DEPRECATED_AUDITS env gate not present")
    # live env: SUITE_KEEP_DEPRECATED_AUDITS must be unset/false
    if os.environ.get("SUITE_KEEP_DEPRECATED_AUDITS", "").lower() == "true":
        fail("SUITE_KEEP_DEPRECATED_AUDITS must remain unset/false in live env")
    print("[PASS] PROJECT_E Track A SLC v2 zero-fail recovery OK: 8 v2 successors present; 8 v1 still on disk + in OPTIONAL list; SUPERSEDED gate active; no required weakening")
    sys.exit(0)

if __name__ == "__main__": main()
