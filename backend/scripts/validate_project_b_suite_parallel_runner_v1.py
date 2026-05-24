#!/usr/bin/env python3
"""
PROJECT_B Track E validator (read-only).

Verifica:
- runner contiene flag --parallel + --parallel-workers
- runner mantiene il blocco sequential per OPTIONAL come fallback default
- runner mantiene REQUIRED sequential
- result JSON integro

NON esegue la suite (eviterebbe ricorsione).

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

RESULT = Path("/app/data/design/system_safety/project_b_suite_parallel_runner_result_v1.json")
RUNNER = Path("/app/backend/scripts/run_hero_skill_kit_validator_suite.py")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not RESULT.exists():
        fail(f"missing result: {RESULT}")
    m = json.loads(RESULT.read_text(encoding="utf-8"))
    if m.get("verdict") != "TRACK_E_SUITE_PARALLEL_RUNNER_IMPLEMENTED_SAFE":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("default_behavior_unchanged") is not True:
        fail("default_behavior_unchanged must be True")

    if not RUNNER.exists():
        fail(f"missing runner: {RUNNER}")
    src = RUNNER.read_text(encoding="utf-8")
    for needle in ("'--parallel'", "'--parallel-workers'", "ThreadPoolExecutor",
                   "if args.parallel:", "PROJECT_B Track E"):
        if needle not in src:
            fail(f"runner missing expected token: {needle}")
    # Required validators must remain sequential: ensure no parallel wrapping in REQUIRED loop.
    required_loop_block = src[src.find("for task, name in REQUIRED:"):src.find("print('-- optional --')")]
    if "ThreadPoolExecutor" in required_loop_block:
        fail("REQUIRED loop must remain strictly sequential (no ThreadPoolExecutor)")
    # Sequential fallback for OPTIONAL must be present (else branch).
    if "else:\n        for task, name in OPTIONAL:" not in src:
        fail("OPTIONAL sequential fallback branch (else) missing")

    forb = m.get("forbidden_in_track_e_respected", {})
    for k in ("weakening_required_validators", "skipping_failures", "hiding_misses",
              "default_behavior_change", "runtime_route_changes"):
        if forb.get(k) is not False:
            fail(f"forbidden_in_track_e_respected.{k} must be False")

    print("[PASS] PROJECT_B Track E parallel runner OK: --parallel + --parallel-workers added; default sequential preserved")
    sys.exit(0)


if __name__ == "__main__":
    main()
