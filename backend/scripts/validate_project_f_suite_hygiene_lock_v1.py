#!/usr/bin/env python3
"""PROJECT_F Track G validator — suite hygiene lock & regression guard.

Structural checks only (does not re-run the full suite to avoid recursion):
  * marker present with verdict ready
  * SUPERSEDED_AFTER_PROJECT_E_V2 cluster declared in the suite runner
  * 8 v2 successors present on disk
  * 8 PROJECT-E-TRACK-* entries present in OPTIONAL
  * 8 PROJECT-F-TRACK-* entries present in OPTIONAL (once registered)
  * no fake_pass / no hiding_failures policies asserted in marker
"""
import json, re, sys
from pathlib import Path

SUITE = Path('/app/backend/scripts/run_hero_skill_kit_validator_suite.py')
MARKER = Path('/app/data/design/system_safety/project_f_suite_hygiene_lock_v1.json')
V2_SUCCESSORS = (
    'validate_slc_c_repo_multishard_post_g_invariant_v2.py',
    'validate_slc_c_combo_v2.py',
    'validate_slc_d_preflight_v2.py',
    'validate_slc_d_merge_tooling_combo_v2.py',
    'validate_slc_be_preflight_v2.py',
    'validate_slc_be_server_profile_selection_combo_v2.py',
    'validate_slc_f_preflight_v2.py',
    'validate_slc_f_route_patch_dryrun_combo_v2.py',
)
PROJECT_E_OPTIONAL_TASKS = (
    'PROJECT-E-TRACK-A-SLC-V2-ZERO-FAIL-RECOVERY',
    'PROJECT-E-TRACK-B-HOUSING-PHASE3-INTEGRATION-DESIGN',
    'PROJECT-E-TRACK-C-STATUS-EFFECT-NON-RUNTIME-UT',
    'PROJECT-E-TRACK-D-DRIFT-DOC-4-ARCHIVE',
    'PROJECT-E-TRACK-E-QA-LOGIN-DRYRUN-SAFETY',
    'PROJECT-E-TRACK-F-AF2N-DASHBOARD-PROVISIONING-DRILL',
    'PROJECT-E-TRACK-G-ARTIFACT-BONUS-RESOLVER-NON-RUNTIME-UT',
    'PROJECT-E-TRACK-H-PROJECT-COMPLETION-DOD-RECALIBRATION',
)
PROJECT_F_OPTIONAL_TASKS = (
    'PROJECT-F-TRACK-A-SERVER-PROFILES-READ-ONLY-PREVIEW-HARDENING',
    'PROJECT-F-TRACK-B-HOUSING-READ-ONLY-PREVIEW-CONTRACT',
    'PROJECT-F-TRACK-C-STATUS-EFFECT-ADAPTER-PHASE2-TESTS',
    'PROJECT-F-TRACK-D-DRIFT-DOC-5-ARCHIVE',
    'PROJECT-F-TRACK-E-QA-CREDENTIALS-SAFE-DRYRUN',
    'PROJECT-F-TRACK-F-AF2N-DASHBOARD-PROVISIONING-PHASE3-DRYRUN',
    'PROJECT-F-TRACK-G-SUITE-HYGIENE-LOCK',
    'PROJECT-F-TRACK-H-ARTIFACT-BIBLE-IMPORT-PLAN-APPROVAL-GATE',
)


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not SUITE.exists(): fail('suite runner missing')
    body = SUITE.read_text()
    if 'SUPERSEDED_AFTER_PROJECT_E_V2' not in body: fail('suite missing SUPERSEDED_AFTER_PROJECT_E_V2 cluster')
    scripts_dir = Path('/app/backend/scripts')
    for v2 in V2_SUCCESSORS:
        if not (scripts_dir / v2).exists(): fail(f'v2 successor missing: {v2}')
    for t in PROJECT_E_OPTIONAL_TASKS:
        if t not in body: fail(f'PROJECT_E OPTIONAL task missing in suite: {t}')
    for t in PROJECT_F_OPTIONAL_TASKS:
        if t not in body: fail(f'PROJECT_F OPTIONAL task missing in suite: {t}')
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_G_SUITE_HYGIENE_LOCK_READY': fail('verdict mismatch')
    if m.get('baseline_fail') != 0: fail('baseline_fail must be 0')
    if m.get('baseline_miss') != 0: fail('baseline_miss must be 0')
    if m.get('required_validators_unchanged') is not True: fail('required_validators_unchanged must be True')
    forb = m.get('forbidden_in_track_g_respected', {})
    for k in ('fake_pass', 'hiding_failures', 'required_weakening'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_g.{k} must be False')
    print('[PASS] PROJECT_F Track G suite hygiene lock READY: SUPERSEDED gate present; 8 v2 successors on disk; PROJECT_E+F tasks registered; no required weakening')
    sys.exit(0)

if __name__ == '__main__': main()
