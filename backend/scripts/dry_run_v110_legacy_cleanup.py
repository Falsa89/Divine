#!/usr/bin/env python3
"""v110 Legacy cleanup dry-run. NO DELETE. Read-only audit."""
import json, os, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "data/design/v110_psp_migration/v110_legacy_cleanup_dry_run_result_v1.json")

def _safe_count(db, name, query=None):
    try:
        return int(db[name].count_documents(query or {}))
    except Exception:
        return None

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
        return client[name]
    except Exception:
        return None

def main():
    db = _try_db()
    warnings = []
    inspect_targets = {
        "legacy_heroes_account_wide": ("user_heroes", {"server_id": {"$exists": False}}),
        "legacy_team_formation_no_server": ("team_formation", {"server_id": {"$exists": False}}),
        "legacy_inventory_no_server": ("user_inventory", {"server_id": {"$exists": False}}),
        "legacy_equipment_no_server": ("user_equipment", {"server_id": {"$exists": False}}),
        "legacy_arena_no_server": ("arena_mmr", {"server_id": {"$exists": False}}),
        "legacy_guild_no_server": ("guild_membership", {"server_id": {"$exists": False}}),
        "legacy_chat_no_server": ("chat_messages", {"server_id": {"$exists": False}}),
        "legacy_rankings_no_server": ("rankings", {"server_id": {"$exists": False}}),
        "legacy_battle_no_server": ("battle_instances", {"server_id": {"$exists": False}}),
        "legacy_bots_no_server": ("bots", {"server_id": {"$exists": False}}),
        "legacy_encounters_no_server": ("encounters", {"server_id": {"$exists": False}}),
    }
    findings = {}
    if db is None:
        warnings.append("mongo_unreachable_using_placeholder_counts")
        for k in inspect_targets:
            findings[k] = None
    else:
        for k, (col, q) in inspect_targets.items():
            findings[k] = _safe_count(db, col, q)
    total_legacy_docs_candidate_for_archive = sum(v for v in findings.values() if isinstance(v, int))
    payload = {
        "pack": "MEGA_RELEASE_ACCELERATION_70_v110_PSP_APPLY_AND_LEGACY_CLEANUP_PREP_GATED_NOT_APPLIED",
        "track": "F",
        "sentinel": "PUBLIC_SYNC_TAG_v110_PSP_APPLY_AND_LEGACY_CLEANUP_PREP_GATED_NOT_APPLIED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "read_only": True,
        "db_writes": 0,
        "delete_executed": False,
        "mongo_reachable": db is not None,
        "findings": findings,
        "total_legacy_docs_candidate_for_archive": total_legacy_docs_candidate_for_archive,
        "archive_policy": "move_to_legacy_<collection>_archive_collection (NOT executed)",
        "delete_policy": "no_hard_delete_in_v110",
        "warnings": warnings,
        "safety_flags": {
            "db_write": False,
            "delete": False,
            "destructive_migration": False,
            "fake_PASS": False,
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"[v110 LEGACY CLEANUP DRY-RUN] mongo_reachable={payload['mongo_reachable']} delete=0 -> {OUT}")
    sys.exit(0)

if __name__ == "__main__":
    main()
