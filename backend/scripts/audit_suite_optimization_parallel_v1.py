#!/usr/bin/env python3
"""
V8 BLOCK_E audit/validator (read-only).

Verifica la consistenza del JSON di audit della suite e produce statistiche
leggere sul runner senza eseguire alcun validator.

NON modifica il runner, NON modifica i validator, NON esegue la suite.

Exit 0 PASS / 1 FAIL.
"""
import json
import re
import sys
from pathlib import Path

AUDIT = Path("/app/data/design/system_safety/suite_optimization_parallel_audit_v1.json")
RUNNER = Path("/app/backend/scripts/run_hero_skill_kit_validator_suite.py")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not AUDIT.exists():
        fail(f"missing audit: {AUDIT}")
    m = json.loads(AUDIT.read_text(encoding="utf-8"))

    if m.get("verdict") != "BLOCK_E_SUITE_OPTIMIZATION_PARALLEL_AUDIT_READY":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("required_validators_changed") is not False:
        fail("required_validators_changed must be False")
    if m.get("optional_validators_changed") is not False:
        # Note: V8 BLOCK_E itself does NOT change OPTIONAL list semantics; adding the new audit validator
        # entry to OPTIONAL is a registration, not a change to existing entries. Audit JSON declares
        # this contract via optional_validators_changed=false (existing OPTIONAL entries untouched).
        fail("optional_validators_changed must be False (audit declares no semantic change)")
    if m.get("validators_weakened") is not False:
        fail("validators_weakened must be False")

    if not RUNNER.exists():
        fail(f"missing runner: {RUNNER}")
    runner_src = RUNNER.read_text(encoding="utf-8")

    # Audit confirms current baseline: PASS=367 (or higher when V8 entries added),
    # FAIL=0, MISS=0. We only check the runner contains the expected OPTIONAL framework.
    if "OPTIONAL = [" not in runner_src:
        fail("runner missing OPTIONAL list framework")
    if "def run_one(" not in runner_src:
        fail("runner missing run_one function (suite engine intact check)")

    groups = m.get("proposed_parallel_groups", [])
    if len(groups) < 3:
        fail("proposed_parallel_groups must declare >=3 groups")
    group_ids = {g.get("group_id") for g in groups}
    if "G1_JSON_ONLY" not in group_ids:
        fail("missing canonical group G1_JSON_ONLY")
    if "G2_HTTP_SMOKE" not in group_ids:
        fail("missing canonical group G2_HTTP_SMOKE")

    forb = m.get("forbidden_in_block_e_respected", {})
    for k in ("weakening_validators", "skipping_failures", "required_validator_changes",
              "hiding_misses", "runtime_route_changes"):
        if forb.get(k) is not False:
            fail(f"forbidden_in_block_e_respected.{k} must be False")

    # Count OPTIONAL entries in the runner as a sanity check (non-strict).
    opt_count = len(re.findall(r"^\s*\(\s*'[A-Z0-9_\-]+'\s*,\s*'validate_|^\s*\(\s*'[A-Z0-9_\-]+'\s*,\s*'audit_",
                                runner_src, flags=re.MULTILINE))
    print(f"[INFO] OPTIONAL-like entries detected in runner: ~{opt_count}")

    print("[PASS] V8 BLOCK_E suite optimization audit OK (3+ groups, no validator weakening, runner intact)")
    sys.exit(0)


if __name__ == "__main__":
    main()
