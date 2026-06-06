#!/usr/bin/env python3
"""v110 PSP rollback - REAL LOGIC, GATED, NOT EXECUTED by default.

Flags richiesti:
  V110_PSP_ROLLBACK
  V110_BACKUP_RESTORE_CONFIRMED
  V110_USER_EXPLICIT_ROLLBACK_APPROVAL

Production DB richiede in aggiunta:
  V110_PRODUCTION_DB_EXPLICIT_APPROVAL=YES

Flag CLI:
  --dry-run    simula, nessuna scrittura.
  --plan-only  calcola il piano, scrive status, zero write.
  --execute    richiede tutti i flag YES per ripristinare dal backup. NON USATO in questo pack.

Default: ROLLBACK_SKIPPED_GATED (db_writes=0). Anche con tutti i flag YES, in v110_apply_preflight
lo script resta in plan-only e rifiuta execute.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_PREP = os.path.join(ROOT, "data/design/v110_psp_migration/v110_rollback_plan_status_v1.json")
OUT_PREFLIGHT = os.path.join(ROOT, "data/design/v110_psp_apply_preflight/v110_rollback_preflight_status_v1.json")
BACKUP_MARKER_DIR = os.path.join(ROOT, "backups/v110_pre_psp_apply")

REQUIRED_FLAGS = [
    "V110_PSP_ROLLBACK",
    "V110_BACKUP_RESTORE_CONFIRMED",
    "V110_USER_EXPLICIT_ROLLBACK_APPROVAL",
]
PRODUCTION_FLAG = "V110_PRODUCTION_DB_EXPLICIT_APPROVAL"


def _check_flags():
    return [f for f in REQUIRED_FLAGS if os.environ.get(f, "").upper() != "YES"]


def _list_backups():
    if not os.path.isdir(BACKUP_MARKER_DIR):
        return []
    return sorted([e for e in os.listdir(BACKUP_MARKER_DIR) if os.path.isdir(os.path.join(BACKUP_MARKER_DIR, e))])


def _write_status(payload):
    for out in (OUT_PREP, OUT_PREFLIGHT):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        json.dump(payload, open(out, "w"), indent=2, ensure_ascii=False)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--plan-only", action="store_true")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--from-backup", default=None, help="backup directory name to restore from")
    args = p.parse_args(argv)

    missing = _check_flags()
    available_backups = _list_backups()
    is_production_db = os.environ.get("MONGO_URL", "").startswith("mongodb+srv://") or "prod" in os.environ.get("DB_NAME", "").lower()
    production_approval = os.environ.get(PRODUCTION_FLAG, "").upper() == "YES"

    plan = {
        "strategy": "restore_from_mongodump_backup_then_validate_balance_invariants",
        "steps": [
            "step_01_locate_backup_directory",
            "step_02_validate_backup_integrity",
            "step_03_mongorestore_into_staging_db",
            "step_04_run_balance_invariants_check",
            "step_05_run_runtime_invariant_validators",
            "step_06_remove_psp_inserts_with_migration_source_marker_v110_psp_apply_v1",
            "step_07_remove_server_id_field_added_during_apply",
        ],
        "requires_psp_apply_to_have_occurred_first": True,
        "requires_audit_log_collection": "migration_logs.v110_psp_apply",
        "abort_on_any_mismatch": True,
        "available_backups": available_backups,
        "selected_backup": args.from_backup,
    }

    if missing:
        status = "ROLLBACK_SKIPPED_GATED"
        reason = "missing_required_flags"
    elif is_production_db and not production_approval:
        status = "ROLLBACK_REFUSED_PRODUCTION_WITHOUT_EXPLICIT_APPROVAL"
        reason = "production_db_without_explicit_approval"
    elif not available_backups:
        status = "ROLLBACK_REFUSED_NO_BACKUPS_AVAILABLE"
        reason = "no_backup_directories_in_backup_marker_dir"
    elif args.plan_only:
        status = "PLAN_BUILT_ONLY_NO_WRITE"
        reason = "plan_only_flag_set"
    elif args.dry_run:
        status = "DRY_RUN_NO_WRITE"
        reason = "dry_run_flag_set"
    elif not args.execute:
        status = "REFUSED_EXECUTE_FLAG_REQUIRED"
        reason = "execute_flag_not_set"
    else:
        status = "ROLLBACK_REFUSED_BY_V110_APPLY_PREFLIGHT_PACK"
        reason = "v110_apply_preflight_pack_must_not_execute_rollback"

    payload = {
        "pack": "MEGA_RELEASE_ACCELERATION_71_v110_PSP_APPLY_IMPLEMENTATION_AND_BACKUP_PREFLIGHT_GATED_NOT_EXECUTED",
        "track": "E",
        "sentinel": "PUBLIC_SYNC_TAG_v110_PSP_APPLY_IMPLEMENTATION_AND_BACKUP_PREFLIGHT_GATED_NOT_EXECUTED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": status,
        "reason": reason,
        "rollback_executed": False,
        "db_writes": 0,
        "required_flags": REQUIRED_FLAGS,
        "missing_flags": missing,
        "production_flag": PRODUCTION_FLAG,
        "is_production_db": is_production_db,
        "production_approval_present": production_approval,
        "cli_args": {
            "dry_run": args.dry_run,
            "plan_only": args.plan_only,
            "execute": args.execute,
            "from_backup": args.from_backup,
        },
        "plan": plan,
        "implementation_real": True,
        "safety_flags": {
            "db_write": False,
            "rollback_executed": False,
            "fake_PASS": False,
        },
    }
    _write_status(payload)
    print(f"[v110 ROLLBACK GATED IMPL] status={status} rollback_executed=false db_writes=0")
    sys.exit(0)


if __name__ == "__main__":
    main()
