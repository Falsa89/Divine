#!/usr/bin/env python3
# Alpha Internal QA Readiness Runner v1
# Pack: MEGA_RELEASE_ACCELERATION_20_v71
#
# Read-only runner. Nessun backend live call. Nessun DB. Nessuna rete.
# Verifica solo presenza locale di file/contracts/screens richiesti per
# poter avviare la QA interna alpha. Output JSON.
#
# Uso:
#   python3 backend/scripts/alpha_internal_qa_readiness_runner_v1.py
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

EXPECTED_SCREENS = [
    "frontend/app/training-combat-onboarding-preview.tsx",
    "frontend/app/first-session-onboarding-preview.tsx",
    "frontend/app/story-alpha-slice-preview.tsx",
    "frontend/app/boss-tower-alpha-loop-preview.tsx",
    "frontend/app/event-arena-alpha-gate-preview.tsx",
    "frontend/app/event-arena-first-alpha-slice-preview.tsx",
]

EXPECTED_CONTRACTS = [
    "data/design/onboarding/training_combat_onboarding_contract_v1.json",
    "data/design/onboarding/first_session_onboarding_contract_v1.json",
    "data/design/onboarding/first_session_onboarding_hardening_contract_v1.json",
    "data/design/story/story_first_playable_alpha_slice_contract_v1.json",
    "data/design/modes/boss_tower_alpha_loop_contract_v1.json",
    "data/design/modes/event_arena_alpha_gate_contract_v1.json",
    "data/design/modes/event_arena_first_alpha_slice_contract_v1.json",
    "data/design/assets/hero_asset_dryrun_manifest_contract_v1.json",
]

EXPECTED_QA_DESIGN = [
    "data/design/qa/alpha_internal_qa_execution_plan_v1.json",
    "data/design/qa/alpha_internal_qa_device_matrix_v1.json",
    "data/design/qa/alpha_internal_qa_bug_severity_matrix_v1.json",
    "data/design/qa/alpha_internal_qa_evidence_template_v1.json",
]


def check(paths):
    present = []
    missing = []
    for rel in paths:
        if os.path.isfile(os.path.join(ROOT, rel)):
            present.append(rel)
        else:
            missing.append(rel)
    return present, missing


def main() -> int:
    sc_present, sc_missing = check(EXPECTED_SCREENS)
    co_present, co_missing = check(EXPECTED_CONTRACTS)
    qa_present, qa_missing = check(EXPECTED_QA_DESIGN)

    overall_ready = not (sc_missing or co_missing or qa_missing)

    report = {
        "runner_version": "alpha_internal_qa_readiness_runner_v1",
        "pack": "MEGA_RELEASE_ACCELERATION_20_v71",
        "read_only": True,
        "network_used": False,
        "db_writes": 0,
        "backend_live_calls": False,
        "overall_ready": overall_ready,
        "screens": {"present": sc_present, "missing": sc_missing},
        "contracts": {"present": co_present, "missing": co_missing},
        "qa_design": {"present": qa_present, "missing": qa_missing},
        "notes": "Read-only check di presenza file. Nessuna mutazione, nessun network.",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if overall_ready else 1


if __name__ == "__main__":
    sys.exit(main())
