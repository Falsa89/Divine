#!/usr/bin/env python3
# Validator: PROJECT-ALPHA-SLICE-RESULT-IDEMPOTENCY-BOUNDARY
# Pack: MEGA_RELEASE_ACCELERATION_17_v68
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "result": "data/design/release_acceleration/alpha_slice_result_preview_boundary_v1.json",
    "idemp": "data/design/release_acceleration/story_boss_tower_alpha_idempotency_boundary_v1.json",
    "obs": "data/design/release_acceleration/alpha_slice_observation_preview_plan_v1.json",
}

APPLIES = ["story_alpha_slice", "boss_alpha_loop", "tower_alpha_loop"]


def main() -> int:
    errors = []
    for key, rel in FILES.items():
        if not os.path.isfile(os.path.join(ROOT, rel)):
            errors.append(f"MISSING_FILE: {rel}")
    if errors:
        for e in errors:
            print(e)
        return 1

    res = json.load(open(os.path.join(ROOT, FILES["result"]), "r", encoding="utf-8"))
    for k, v in {
        "result_preview_enabled": True,
        "result_authoritative": False,
        "reward_preview_enabled": True,
        "reward_grant_enabled": False,
        "progress_preview_enabled": True,
        "permanent_progress_enabled": False,
        "db_writes": 0,
        "idempotency_design_required_before_live": True,
        "observation_required_before_live": True,
        "rollback_required_before_live": True,
    }.items():
        if res.get(k) != v:
            errors.append(f"RESULT_BAD: {k}={res.get(k)!r} expected {v!r}")
    if set(res.get("applies_to") or []) != set(APPLIES):
        errors.append("RESULT_APPLIES_MISMATCH")

    idemp = json.load(open(os.path.join(ROOT, FILES["idemp"]), "r", encoding="utf-8"))
    if set(idemp.get("applies_to") or []) != set(APPLIES):
        errors.append("IDEMP_APPLIES_MISMATCH")
    if idemp.get("db_writes") != 0:
        errors.append("IDEMP_BAD_DB_WRITES")
    if idemp.get("reward_grant_enabled") is not False:
        errors.append("IDEMP_BAD_REWARD")

    obs = json.load(open(os.path.join(ROOT, FILES["obs"]), "r", encoding="utf-8"))
    if obs.get("observation_critical_count") != 0:
        errors.append("OBS_CRITICAL_NONZERO")
    if obs.get("db_writes") != 0:
        errors.append("OBS_BAD_DB_WRITES")
    if not (obs.get("observation_targets") or []):
        errors.append("OBS_TARGETS_EMPTY")

    if errors:
        for e in errors:
            print(e)
        return 1

    print("PROJECT-ALPHA-SLICE-RESULT-IDEMPOTENCY-BOUNDARY: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
