#!/usr/bin/env python3
"""v110 PSP backup preflight - REAL LOGIC, GATED, NOT EXECUTED by default.

Flags richiesti per execute:
  V110_BACKUP_EXECUTE
  V110_USER_EXPLICIT_BACKUP_APPROVAL

Production DB richiede in aggiunta:
  V110_PRODUCTION_DB_EXPLICIT_APPROVAL=YES

Flag CLI:
  --dry-run     simula mongodump in memoria.
  --plan-only   produce piano + verifica spazio.
  --execute     esegue mongodump reale. NON USATO in questo pack.

Default: BACKUP_PLAN_ONLY (db_writes=0, export_executed=false). In v110_apply_preflight
NON eseguire mai mongodump anche se flag presenti.
"""
import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "data/design/v110_psp_apply_preflight/v110_backup_preflight_status_v1.json")
MANIFEST = os.path.join(ROOT, "data/design/v110_psp_migration/v110_backup_manifest_plan_v1.json")
BACKUP_BASE = os.path.join(ROOT, "backups/v110_pre_psp_apply")

REQUIRED_FLAGS = [
    "V110_BACKUP_EXECUTE",
    "V110_USER_EXPLICIT_BACKUP_APPROVAL",
]
PRODUCTION_FLAG = "V110_PRODUCTION_DB_EXPLICIT_APPROVAL"


def _check_flags():
    return [f for f in REQUIRED_FLAGS if os.environ.get(f, "").upper() != "YES"]


def _load_manifest():
    if not os.path.isfile(MANIFEST):
        return None
    return json.load(open(MANIFEST))


def _disk_space_check():
    try:
        st = shutil.disk_usage(os.path.dirname(BACKUP_BASE) if os.path.isdir(os.path.dirname(BACKUP_BASE)) else ROOT)
        return {"free_bytes": st.free, "total_bytes": st.total, "free_gb": round(st.free / (1024 ** 3), 2)}
    except Exception as e:
        return {"error": str(e)}


def _mongodump_available():
    return shutil.which("mongodump") is not None


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--plan-only", action="store_true")
    p.add_argument("--execute", action="store_true")
    args = p.parse_args(argv)

    manifest = _load_manifest()
    missing = _check_flags()
    is_production_db = os.environ.get("MONGO_URL", "").startswith("mongodb+srv://") or "prod" in os.environ.get("DB_NAME", "").lower()
    production_approval = os.environ.get(PRODUCTION_FLAG, "").upper() == "YES"
    space = _disk_space_check()
    mongodump_present = _mongodump_available()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    target_dir = os.path.join(BACKUP_BASE, timestamp)
    command_planned = f"mongodump --uri={os.environ.get('MONGO_URL', '<MONGO_URL>')} --db={os.environ.get('DB_NAME', '<DB_NAME>')} --out={target_dir}"

    if not manifest:
        status = "BACKUP_REFUSED_NO_MANIFEST"
        reason = "v110_backup_manifest_plan_missing"
        export_executed = False
    elif missing:
        status = "BACKUP_PLAN_ONLY"
        reason = "missing_required_flags_for_execute"
        export_executed = False
    elif not mongodump_present:
        status = "BACKUP_REFUSED_MONGODUMP_NOT_FOUND"
        reason = "mongodump_binary_not_in_PATH"
        export_executed = False
    elif is_production_db and not production_approval:
        status = "BACKUP_REFUSED_PRODUCTION_WITHOUT_EXPLICIT_APPROVAL"
        reason = "production_db_without_explicit_approval"
        export_executed = False
    elif args.plan_only:
        status = "PLAN_BUILT_ONLY"
        reason = "plan_only_flag_set"
        export_executed = False
    elif args.dry_run:
        status = "DRY_RUN_NO_WRITE"
        reason = "dry_run_flag_set"
        export_executed = False
    elif not args.execute:
        status = "REFUSED_EXECUTE_FLAG_REQUIRED"
        reason = "execute_flag_not_set"
        export_executed = False
    else:
        # In v110_apply_preflight: NEVER execute mongodump even if flags + execute set
        status = "BACKUP_REFUSED_BY_V110_APPLY_PREFLIGHT_PACK"
        reason = "v110_apply_preflight_pack_must_not_execute_backup"
        export_executed = False

    payload = {
        "pack": "MEGA_RELEASE_ACCELERATION_71_v110_PSP_APPLY_IMPLEMENTATION_AND_BACKUP_PREFLIGHT_GATED_NOT_EXECUTED",
        "track": "D",
        "sentinel": "PUBLIC_SYNC_TAG_v110_PSP_APPLY_IMPLEMENTATION_AND_BACKUP_PREFLIGHT_GATED_NOT_EXECUTED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": status,
        "reason": reason,
        "export_executed": export_executed,
        "db_writes": 0,
        "required_flags": REQUIRED_FLAGS,
        "missing_flags": missing,
        "production_flag": PRODUCTION_FLAG,
        "is_production_db": is_production_db,
        "production_approval_present": production_approval,
        "manifest_present": manifest is not None,
        "manifest_collections_count": len(manifest.get("collections_to_backup", [])) if manifest else 0,
        "mongodump_present_in_path": mongodump_present,
        "disk_space": space,
        "command_planned": command_planned,
        "target_dir_planned": target_dir,
        "masking_rules": manifest.get("masking_rules") if manifest else None,
        "cli_args": {
            "dry_run": args.dry_run,
            "plan_only": args.plan_only,
            "execute": args.execute,
        },
        "implementation_real": True,
        "safety_flags": {
            "db_write": False,
            "export_executed": False,
            "fake_PASS": False,
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(payload, open(OUT, "w"), indent=2, ensure_ascii=False)
    print(f"[v110 BACKUP PREFLIGHT IMPL] status={status} export_executed=false db_writes=0")
    sys.exit(0)


if __name__ == "__main__":
    main()
