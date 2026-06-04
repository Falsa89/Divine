#!/usr/bin/env python3
# Validator: PROJECT-ALPHA-INTERNAL-QA-EXECUTION
# Pack: MEGA_RELEASE_ACCELERATION_20_v71
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "plan": "data/design/qa/alpha_internal_qa_execution_plan_v1.json",
    "devices": "data/design/qa/alpha_internal_qa_device_matrix_v1.json",
    "severity": "data/design/qa/alpha_internal_qa_bug_severity_matrix_v1.json",
    "evidence": "data/design/qa/alpha_internal_qa_evidence_template_v1.json",
    "marker": "data/design/qa/alpha_internal_qa_execution_marker_v1.json",
    "runner": "backend/scripts/alpha_internal_qa_readiness_runner_v1.py",
}

FORBIDDEN_RUNNER = [
    "pymongo", "motor", "MONGO_URL", "redis",
    "requests.get", "requests.post", "urllib.request.urlopen",
    "httpx", "aiohttp",
]

TARGET_FLOWS = {
    "first_session_onboarding_preview",
    "training_combat_onboarding_preview",
    "story_alpha_slice_preview",
    "boss_alpha_loop_preview",
    "tower_alpha_loop_preview",
    "event_arena_first_alpha_preview",
    "event_arena_gate_preview",
    "hero_asset_dryrun_readiness_report",
}
SEVERITIES = {"P0", "P1", "P2", "P3"}
EVIDENCE_REQUIRED = {
    "device", "os", "app_build_commit", "route", "steps",
    "expected", "actual", "severity", "regression",
}


def strip_py_comments(src: str) -> str:
    return re.sub(r"#[^\n]*", "", src)


def main() -> int:
    errors = []
    for k, rel in FILES.items():
        if not os.path.isfile(os.path.join(ROOT, rel)):
            errors.append(f"MISSING_FILE: {k}={rel}")
    if errors:
        for e in errors:
            print(e)
        return 1

    plan = json.load(open(os.path.join(ROOT, FILES["plan"]), "r", encoding="utf-8"))
    for k, v in {
        "qa_execution_plan_only": True,
        "automated_live_mutation": False,
        "backend_route_calls_required": False,
        "db_writes": 0,
        "reward_grant_enabled": False,
        "account_persistence": False,
    }.items():
        if plan.get(k) != v:
            errors.append(f"PLAN_BAD: {k}={plan.get(k)!r} expected {v!r}")
    if not TARGET_FLOWS.issubset(set(plan.get("target_flows") or [])):
        errors.append("PLAN_TARGETS_MISSING")

    devices = json.load(open(os.path.join(ROOT, FILES["devices"]), "r", encoding="utf-8"))
    if len(devices.get("devices") or []) < 4:
        errors.append("DEVICES_TOO_FEW")
    if devices.get("network_required") is not False:
        errors.append("DEVICES_NETWORK_REQUIRED")

    sev = json.load(open(os.path.join(ROOT, FILES["severity"]), "r", encoding="utf-8"))
    sev_ids = {s.get("id") for s in (sev.get("severities") or [])}
    if sev_ids != SEVERITIES:
        errors.append("SEVERITY_IDS_MISMATCH")
    forbidden_class = set(sev.get("forbidden_classifications") or [])
    if "reward_grant_required_to_reproduce" not in forbidden_class:
        errors.append("SEVERITY_FORBIDDEN_CLASS_MISSING")

    ev = json.load(open(os.path.join(ROOT, FILES["evidence"]), "r", encoding="utf-8"))
    field_ids = {f.get("id") for f in (ev.get("fields") or [])}
    if not EVIDENCE_REQUIRED.issubset(field_ids):
        errors.append("EVIDENCE_FIELDS_MISSING")
    if ev.get("db_writes") != 0:
        errors.append("EVIDENCE_BAD_DB_WRITES")

    marker = json.load(open(os.path.join(ROOT, FILES["marker"]), "r", encoding="utf-8"))
    if marker.get("runner_read_only") is not True:
        errors.append("MARKER_RUNNER_NOT_READ_ONLY")
    if marker.get("db_writes") != 0:
        errors.append("MARKER_BAD_DB_WRITES")
    if marker.get("backend_live_calls") is not False:
        errors.append("MARKER_BACKEND_LIVE_CALLS")

    runner_src = open(os.path.join(ROOT, FILES["runner"]), "r", encoding="utf-8").read()
    runner_code = strip_py_comments(runner_src)
    for bad in FORBIDDEN_RUNNER:
        if bad in runner_code:
            errors.append(f"RUNNER_FORBIDDEN: {bad}")

    if errors:
        for e in errors:
            print(e)
        return 1
    print("PROJECT-ALPHA-INTERNAL-QA-EXECUTION: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
