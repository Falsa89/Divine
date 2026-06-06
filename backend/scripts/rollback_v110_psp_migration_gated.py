#!/usr/bin/env python3
"""v110 PSP rollback script - GATED. Refuse unless all flags = YES. NOT EXECUTED by default."""
import json, os, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "data/design/v110_psp_migration/v110_rollback_plan_status_v1.json")

REQUIRED_FLAGS = [
    "V110_PSP_ROLLBACK",
    "V110_BACKUP_RESTORE_CONFIRMED",
    "V110_USER_EXPLICIT_ROLLBACK_APPROVAL",
]

def main():
    missing = [f for f in REQUIRED_FLAGS if os.environ.get(f, "").upper() != "YES"]
    status = "ROLLBACK_SKIPPED_GATED" if missing else "ROLLBACK_NOT_IMPLEMENTED_IN_V110_PREP_PACK"
    rollback_executed = False
    db_writes = 0
    payload = {
        "pack": "MEGA_RELEASE_ACCELERATION_70_v110_PSP_APPLY_AND_LEGACY_CLEANUP_PREP_GATED_NOT_APPLIED",
        "track": "J",
        "sentinel": "PUBLIC_SYNC_TAG_v110_PSP_APPLY_AND_LEGACY_CLEANUP_PREP_GATED_NOT_APPLIED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": status,
        "rollback_executed": rollback_executed,
        "db_writes": db_writes,
        "required_flags": REQUIRED_FLAGS,
        "missing_flags": missing,
        "strategy": "restore_from_backup_then_validate_balance_invariants",
        "safety_flags": {
            "db_write": False,
            "rollback_executed": False,
            "fake_PASS": False,
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"[v110 ROLLBACK GATED] status={status} missing_flags={missing} db_writes=0 -> {OUT}")
    sys.exit(0)

if __name__ == "__main__":
    main()
