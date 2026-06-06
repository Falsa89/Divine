#!/usr/bin/env python3
"""v110 PSP apply script - GATED. Refuse unless all flags = YES. NOT EXECUTED by default."""
import json, os, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "data/design/v110_psp_migration/v110_apply_status_v1.json")

REQUIRED_FLAGS = [
    "V110_PSP_APPLY",
    "V110_BACKUP_CONFIRMED",
    "V110_STAGING_DB_CONFIRMED",
    "V110_USER_EXPLICIT_DB_WRITE_APPROVAL",
    "V110_ROLLBACK_PLAN_CONFIRMED",
]

def main():
    missing = [f for f in REQUIRED_FLAGS if os.environ.get(f, "").upper() != "YES"]
    status = "APPLY_SKIPPED_GATED" if missing else "APPLY_NOT_IMPLEMENTED_IN_V110_PREP_PACK"
    apply_executed = False  # questo pack v110 e PREP-ONLY, mai eseguito anche se flag passati
    db_writes = 0
    payload = {
        "pack": "MEGA_RELEASE_ACCELERATION_70_v110_PSP_APPLY_AND_LEGACY_CLEANUP_PREP_GATED_NOT_APPLIED",
        "track": "I",
        "sentinel": "PUBLIC_SYNC_TAG_v110_PSP_APPLY_AND_LEGACY_CLEANUP_PREP_GATED_NOT_APPLIED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": status,
        "apply_executed": apply_executed,
        "db_writes": db_writes,
        "required_flags": REQUIRED_FLAGS,
        "missing_flags": missing,
        "reason": "prep_pack_v110_does_not_implement_apply_logic",
        "safety_flags": {
            "db_write": False,
            "destructive_migration": False,
            "apply_executed": False,
            "fake_PASS": False,
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"[v110 APPLY GATED] status={status} missing_flags={missing} db_writes=0 -> {OUT}")
    # Sempre exit 0: lo script ha completato il suo dovere onesto (rifiutare apply)
    sys.exit(0)

if __name__ == "__main__":
    main()
