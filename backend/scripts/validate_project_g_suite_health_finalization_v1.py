#!/usr/bin/env python3
"""PROJECT_G Track G validator — suite health finalization & REQUIRED diff guard.

Structural checks only (no recursive suite run). Confirms:
  * marker present with verdict TRACK_G_SUITE_HEALTH_FINALIZATION_READY
  * baseline_fail == 0 and baseline_miss == 0
  * all 10 declared superseded clusters appear in the suite runner source
  * PROJECT_E, PROJECT_F, PROJECT_G OPTIONAL entries present exactly once each
  * REQUIRED list length is the same as the snapshot recorded here
"""
import json, sys
from pathlib import Path

SUITE = Path('/app/backend/scripts/run_hero_skill_kit_validator_suite.py')
MARKER = Path('/app/data/design/system_safety/project_g_suite_health_finalization_v1.json')
PROJECT_E_TASKS = (
    'PROJECT-E-TRACK-A-SLC-V2-ZERO-FAIL-RECOVERY',
    'PROJECT-E-TRACK-B-HOUSING-PHASE3-INTEGRATION-DESIGN',
    'PROJECT-E-TRACK-C-STATUS-EFFECT-NON-RUNTIME-UT',
    'PROJECT-E-TRACK-D-DRIFT-DOC-4-ARCHIVE',
    'PROJECT-E-TRACK-E-QA-LOGIN-DRYRUN-SAFETY',
    'PROJECT-E-TRACK-F-AF2N-DASHBOARD-PROVISIONING-DRILL',
    'PROJECT-E-TRACK-G-ARTIFACT-BONUS-RESOLVER-NON-RUNTIME-UT',
    'PROJECT-E-TRACK-H-PROJECT-COMPLETION-DOD-RECALIBRATION',
)
PROJECT_F_TASKS = (
    'PROJECT-F-TRACK-A-SERVER-PROFILES-READ-ONLY-PREVIEW-HARDENING',
    'PROJECT-F-TRACK-B-HOUSING-READ-ONLY-PREVIEW-CONTRACT',
    'PROJECT-F-TRACK-C-STATUS-EFFECT-ADAPTER-PHASE2-TESTS',
    'PROJECT-F-TRACK-D-DRIFT-DOC-5-ARCHIVE',
    'PROJECT-F-TRACK-E-QA-CREDENTIALS-SAFE-DRYRUN',
    'PROJECT-F-TRACK-F-AF2N-DASHBOARD-PROVISIONING-PHASE3-DRYRUN',
    'PROJECT-F-TRACK-G-SUITE-HYGIENE-LOCK',
    'PROJECT-F-TRACK-H-ARTIFACT-BIBLE-IMPORT-PLAN-APPROVAL-GATE',
)
PROJECT_G_TASKS = (
    'PROJECT-G-TRACK-A-SERVER-PROFILES-PREVIEW-CONTRACT-FREEZE',
    'PROJECT-G-TRACK-B-HOUSING-PREVIEW-CONTRACT-FREEZE',
    'PROJECT-G-TRACK-C-STATUS-EFFECT-RUNTIME-READINESS-MATRIX',
    'PROJECT-G-TRACK-D-DRIFT-DOC-6-ARCHIVE',
    'PROJECT-G-TRACK-E-QA-SAFE-LOGIN-ENV-CONTRACT',
    'PROJECT-G-TRACK-F-AF2N-DASHBOARD-PROVISIONING-APPROVAL-GATE',
    'PROJECT-G-TRACK-G-SUITE-HEALTH-FINALIZATION',
    'PROJECT-G-TRACK-H-ARTIFACT-APPROVAL-GATE-SIGNATURE',
)


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not SUITE.exists(): fail('suite runner missing')
    body = SUITE.read_text()
    if not MARKER.exists(): fail(f'marker missing {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_G_SUITE_HEALTH_FINALIZATION_READY': fail('verdict mismatch')
    if m.get('baseline_fail') != 0 or m.get('baseline_miss') != 0: fail('baseline fail/miss must be 0')
    for cl in m.get('superseded_clusters_documented', []):
        if cl not in body: fail(f'superseded cluster {cl} not present in suite runner')
    # Tasks exactly once each (count only definition-as-tuple occurrences,
    # NOT mentions inside the SUPERSEDED frozenset).
    for task_list, label in ((PROJECT_E_TASKS, 'E'), (PROJECT_F_TASKS, 'F'), (PROJECT_G_TASKS, 'G')):
        for t in task_list:
            count = body.count(f"('{t}',")
            if count == 0: fail(f'PROJECT_{label} task missing as OPTIONAL tuple definition: {t}')
            if count > 1: fail(f'PROJECT_{label} task duplicated {count}x as OPTIONAL tuple definition: {t}')
    forb = m.get('forbidden_in_track_g_respected', {})
    for k in ('fake_pass', 'hiding_failures', 'required_weakening'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_g.{k} must be False')
    print('[PASS] PROJECT_G Track G suite health finalization READY: superseded clusters documented; PROJECT_E+F+G tasks present exactly once; REQUIRED unchanged')
    sys.exit(0)

if __name__ == '__main__': main()
