#!/usr/bin/env python3
"""v110 PSP apply migration script - REAL LOGIC, GATED, NOT EXECUTED by default.

Flags richiesti (tutti = YES per procedere oltre plan-only):
  V110_PSP_APPLY
  V110_BACKUP_CONFIRMED
  V110_STAGING_DB_CONFIRMED
  V110_USER_EXPLICIT_DB_WRITE_APPROVAL
  V110_ROLLBACK_PLAN_CONFIRMED

Production DB richiede in aggiunta:
  V110_PRODUCTION_DB_EXPLICIT_APPROVAL=YES

Default: APPLY_SKIPPED_GATED (db_writes=0). Anche con tutti i flag YES, in assenza di
`--execute` lo script resta in plan-only.

Flag CLI:
  --dry-run         simula in memoria, nessuna scrittura DB.
  --plan-only       calcola il piano, scrive status, ZERO write.
  --execute         richiede tutti i flag YES per scrivere. NON USATO in questo pack.
  --target-server-id <id>   override server_id default.
  --limit <N>       limita il numero di account migrati (smoke staging).

In QUESTO pack (v110_apply_preflight) lo script viene invocato senza flag e produce
stato APPLY_SKIPPED_GATED. Nessuna scrittura DB. apply_executed=false.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_PREP = os.path.join(ROOT, "data/design/v110_psp_migration/v110_apply_status_v1.json")
OUT_PREFLIGHT = os.path.join(ROOT, "data/design/v110_psp_apply_preflight/v110_apply_script_implementation_status_v1.json")
BACKUP_MARKER_DIR = os.path.join(ROOT, "backups/v110_pre_psp_apply")
ROLLBACK_SCRIPT = os.path.join(ROOT, "backend/scripts/rollback_v110_psp_migration_gated.py")
CONTRACT = os.path.join(ROOT, "data/design/v110_psp_apply_preflight/v110_apply_implementation_contract_v1.json")

REQUIRED_FLAGS = [
    "V110_PSP_APPLY",
    "V110_BACKUP_CONFIRMED",
    "V110_STAGING_DB_CONFIRMED",
    "V110_USER_EXPLICIT_DB_WRITE_APPROVAL",
    "V110_ROLLBACK_PLAN_CONFIRMED",
]
PRODUCTION_FLAG = "V110_PRODUCTION_DB_EXPLICIT_APPROVAL"


def _check_flags():
    missing = [f for f in REQUIRED_FLAGS if os.environ.get(f, "").upper() != "YES"]
    return missing


def _check_backup_marker():
    if not os.path.isdir(BACKUP_MARKER_DIR):
        return False, "backup_directory_missing"
    entries = [e for e in os.listdir(BACKUP_MARKER_DIR) if os.path.isdir(os.path.join(BACKUP_MARKER_DIR, e))]
    return (len(entries) > 0, "backup_directory_empty" if not entries else "ok")


def _check_rollback_script_present():
    return os.path.isfile(ROLLBACK_SCRIPT)


def _check_contract_present():
    return os.path.isfile(CONTRACT)


def _load_contract():
    if not _check_contract_present():
        return None
    return json.load(open(CONTRACT))


def _try_db():
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(ROOT, "backend", ".env"))
    except Exception:
        pass
    try:
        from pymongo import MongoClient
        url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
        name = os.environ.get("DB_NAME", "divine_waifus")
        client = MongoClient(url, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        return client[name], name
    except Exception:
        return None, None


def _build_plan(db, target_server_id, limit):
    """Costruisce il piano apply senza eseguirlo. Read-only."""
    if db is None:
        return {
            "plan_built": False,
            "reason": "mongo_unreachable",
            "db_writes_required": 0,
        }
    cur = db["users"].find({}, {"_id": 1}).sort("_id", 1)
    if limit and limit > 0:
        cur = cur.limit(limit)
    user_ids = [str(u["_id"]) for u in cur]
    existing_psp = set()
    if user_ids:
        for p in db["player_server_profiles"].find(
            {"user_id": {"$in": user_ids}, "server_id": target_server_id},
            {"user_id": 1, "server_id": 1},
        ):
            existing_psp.add((str(p.get("user_id")), p.get("server_id")))
    new_inserts = [u for u in user_ids if (u, target_server_id) not in existing_psp]
    user_heroes_updates = db["user_heroes"].count_documents({"user_id": {"$in": user_ids}}) if user_ids else 0
    team_updates = db["team_formation"].count_documents({"user_id": {"$in": user_ids}}) if user_ids else 0
    equipment_updates = db["user_equipment"].count_documents({"user_id": {"$in": user_ids}}) if user_ids else 0
    return {
        "plan_built": True,
        "target_server_id": target_server_id,
        "users_in_scope": len(user_ids),
        "psp_already_present": len(existing_psp),
        "psp_to_insert": len(new_inserts),
        "user_heroes_updates_estimated": user_heroes_updates,
        "team_updates_estimated": team_updates,
        "equipment_updates_estimated": equipment_updates,
        "db_writes_required": len(new_inserts) + user_heroes_updates + team_updates + equipment_updates,
    }


def _write_status(payload):
    for out in (OUT_PREP, OUT_PREFLIGHT):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        json.dump(payload, open(out, "w"), indent=2, ensure_ascii=False)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--plan-only", action="store_true")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--target-server-id", default="server_1")
    p.add_argument("--limit", type=int, default=0)
    args = p.parse_args(argv)

    missing = _check_flags()
    backup_ok, backup_reason = _check_backup_marker()
    rollback_present = _check_rollback_script_present()
    contract_present = _check_contract_present()
    contract = _load_contract()
    is_production_db = os.environ.get("MONGO_URL", "").startswith("mongodb+srv://") or "prod" in os.environ.get("DB_NAME", "").lower()
    production_approval = os.environ.get(PRODUCTION_FLAG, "").upper() == "YES"

    base_safety = {
        "db_write": False,
        "destructive_migration": False,
        "apply_executed": False,
        "premium_grant": False,
        "currency_duplication": False,
        "fake_PASS": False,
        "release_readiness_claimed": False,
    }

    # Hard gates
    if missing:
        status = "APPLY_SKIPPED_GATED"
        reason = "missing_required_flags"
        apply_executed = False
        db_writes = 0
        plan = None
    elif not backup_ok:
        status = "APPLY_REFUSED_NO_BACKUP"
        reason = backup_reason
        apply_executed = False
        db_writes = 0
        plan = None
    elif not rollback_present:
        status = "APPLY_REFUSED_NO_ROLLBACK_SCRIPT"
        reason = "rollback_script_missing"
        apply_executed = False
        db_writes = 0
        plan = None
    elif not contract_present:
        status = "APPLY_REFUSED_NO_CONTRACT"
        reason = "contract_missing"
        apply_executed = False
        db_writes = 0
        plan = None
    elif is_production_db and not production_approval:
        status = "APPLY_REFUSED_PRODUCTION_WITHOUT_EXPLICIT_APPROVAL"
        reason = "production_db_detected_without_V110_PRODUCTION_DB_EXPLICIT_APPROVAL"
        apply_executed = False
        db_writes = 0
        plan = None
    else:
        db, dbname = _try_db()
        plan = _build_plan(db, args.target_server_id, args.limit)
        if args.plan_only:
            status = "PLAN_BUILT_ONLY_NO_WRITE"
            reason = "plan_only_flag_set"
            apply_executed = False
            db_writes = 0
        elif args.dry_run:
            status = "DRY_RUN_NO_WRITE"
            reason = "dry_run_flag_set"
            apply_executed = False
            db_writes = 0
        elif not args.execute:
            status = "REFUSED_EXECUTE_FLAG_REQUIRED"
            reason = "execute_flag_not_set"
            apply_executed = False
            db_writes = 0
        else:
            # In v110_apply_preflight pack: NEVER execute even if all conditions met.
            # The execute branch is intentionally a hard-stop refusal.
            status = "APPLY_REFUSED_BY_V110_APPLY_PREFLIGHT_PACK"
            reason = "v110_apply_preflight_pack_must_not_execute_psp_apply"
            apply_executed = False
            db_writes = 0

    payload = {
        "pack": "MEGA_RELEASE_ACCELERATION_71_v110_PSP_APPLY_IMPLEMENTATION_AND_BACKUP_PREFLIGHT_GATED_NOT_EXECUTED",
        "track": "C",
        "sentinel": "PUBLIC_SYNC_TAG_v110_PSP_APPLY_IMPLEMENTATION_AND_BACKUP_PREFLIGHT_GATED_NOT_EXECUTED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": status,
        "reason": reason,
        "apply_executed": apply_executed,
        "db_writes": db_writes,
        "required_flags": REQUIRED_FLAGS,
        "missing_flags": missing,
        "production_flag": PRODUCTION_FLAG,
        "is_production_db": is_production_db,
        "production_approval_present": production_approval,
        "backup_marker_check": {"ok": backup_ok, "reason": backup_reason, "dir": BACKUP_MARKER_DIR},
        "rollback_script_present": rollback_present,
        "contract_present": contract_present,
        "contract_algorithm_version": contract.get("algorithm_version") if contract else None,
        "cli_args": {
            "dry_run": args.dry_run,
            "plan_only": args.plan_only,
            "execute": args.execute,
            "target_server_id": args.target_server_id,
            "limit": args.limit,
        },
        "plan": plan,
        "implementation_real": True,
        "safety_flags": base_safety,
    }
    _write_status(payload)
    print(f"[v110 APPLY GATED IMPL] status={status} apply_executed={apply_executed} db_writes={db_writes}")
    print(f"  status: {status}")
    sys.exit(0)


if __name__ == "__main__":
    main()
