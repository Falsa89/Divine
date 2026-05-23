#!/usr/bin/env python3
"""
BLOCK_A audit validator (MEGA_COMBO_SLC_ACCELERATION_V1).

Verifica read-only che il piano di refactor economy.py paid/free split sia presente,
che le superfici di scrittura siano classificate e che NESSUN runtime patch sia stato
applicato. NON modifica file, NON scrive su DB.

Exit codes:
  0 -> PASS
  1 -> FAIL
"""
import json
import sys
from pathlib import Path

PLAN_PATH = Path("/app/data/design/server_lifecycle/economy_paid_free_split_plan_v1.json")
REPORT_PATH = Path("/app/docs/divine/115A_ECONOMY_PAID_FREE_SPLIT_PREP.md")
ECONOMY_PY = Path("/app/backend/routes/economy.py")

REQUIRED_BUCKETS = {
    "PAID_ACCOUNT_WIDE",
    "FREE_SERVER_BOUND",
    "VIP_ACCOUNT_OR_MIXED",
    "LEGACY_SERVER_SELECT_FORBIDDEN",
    "AMBIGUOUS_DEFER",
    "UPDATE_ONLY_NO_SCOPE_REQUIRED",
}


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not PLAN_PATH.exists():
        fail(f"missing plan: {PLAN_PATH}")
    if not REPORT_PATH.exists():
        fail(f"missing report: {REPORT_PATH}")
    if not ECONOMY_PY.exists():
        fail(f"missing target: {ECONOMY_PY}")

    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))

    if plan.get("verdict") != "BLOCK_A_ECONOMY_REFACTOR_PREP_READY":
        fail(f"unexpected verdict: {plan.get('verdict')}")
    if plan.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be false in BLOCK_A audit/prep mode")
    if plan.get("db_migration_required") is not False:
        fail("BLOCK_A must not require DB migration")

    buckets = plan.get("split_buckets_summary", {})
    missing = REQUIRED_BUCKETS - set(buckets.keys())
    if missing:
        fail(f"missing required buckets: {sorted(missing)}")

    surfaces = plan.get("write_surfaces_classified", [])
    if len(surfaces) < 8:
        fail(f"expected >=8 classified surfaces, found {len(surfaces)}")

    if not any(s.get("classification") == "LEGACY_SERVER_SELECT_FORBIDDEN" for s in surfaces):
        fail("LEGACY_SERVER_SELECT_FORBIDDEN classification missing")

    runtime_modified = plan.get("runtime_files_modified", [])
    if runtime_modified:
        fail(f"BLOCK_A must not modify runtime files, found: {runtime_modified}")

    print("[PASS] BLOCK_A audit/prep artifact integrity OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
