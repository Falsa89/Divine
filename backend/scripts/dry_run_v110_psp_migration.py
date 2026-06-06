#!/usr/bin/env python3
"""v110 PSP dry-run migration audit.

Read-only: nessuna scrittura DB. Produce stima counts per pianificare PSP apply.
Utilizza MongoDB locale (mongo_url da backend/.env) per count_documents READ-ONLY.
Se il DB non e raggiungibile, produce stime placeholder e mette warning.
"""
import json, os, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "data/design/v110_psp_migration/v110_psp_dry_run_result_v1.json")

def _safe_count(db, name):
    try:
        return int(db[name].count_documents({}))
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
        # ping
        client.admin.command("ping")
        return client[name]
    except Exception as e:
        return None

def main():
    db = _try_db()
    warnings = []
    if db is None:
        warnings.append("mongo_unreachable_using_placeholder_counts")
        counts = {
            "accounts": None,
            "server_profiles_existing": None,
            "user_heroes": None,
            "team_formation": None,
            "user_inventory": None,
            "user_equipment": None,
            "battle_instances": None,
            "story_progress_docs": None,
            "bots": None,
        }
    else:
        counts = {
            "accounts": _safe_count(db, "users"),
            "server_profiles_existing": _safe_count(db, "player_server_profiles"),
            "user_heroes": _safe_count(db, "user_heroes"),
            "team_formation": _safe_count(db, "team_formation"),
            "user_inventory": _safe_count(db, "user_inventory"),
            "user_equipment": _safe_count(db, "user_equipment"),
            "battle_instances": _safe_count(db, "battle_instances"),
            "story_progress_docs": _safe_count(db, "story_progress"),
            "bots": _safe_count(db, "bots"),
        }
    estimated_psp_inserts_if_apply = counts.get("accounts") if counts.get("accounts") is not None else 0
    estimated_user_heroes_updates_if_apply = counts.get("user_heroes") if counts.get("user_heroes") is not None else 0
    estimated_team_updates_if_apply = counts.get("team_formation") if counts.get("team_formation") is not None else 0
    payload = {
        "pack": "MEGA_RELEASE_ACCELERATION_70_v110_PSP_APPLY_AND_LEGACY_CLEANUP_PREP_GATED_NOT_APPLIED",
        "track": "E",
        "sentinel": "PUBLIC_SYNC_TAG_v110_PSP_APPLY_AND_LEGACY_CLEANUP_PREP_GATED_NOT_APPLIED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "read_only": True,
        "db_writes": 0,
        "mongo_reachable": db is not None,
        "counts": counts,
        "estimated_apply_writes": {
            "psp_inserts": estimated_psp_inserts_if_apply,
            "user_heroes_updates": estimated_user_heroes_updates_if_apply,
            "team_updates": estimated_team_updates_if_apply,
        },
        "currency_split_estimation": {
            "soft_currency_will_move_to_psp": True,
            "hard_currency_stays_account_global": True,
            "premium_currency_stays_account_global": True,
        },
        "warnings": warnings,
        "apply_executed": False,
        "applied_in_this_pack": False,
        "safety_flags": {
            "db_write": False,
            "destructive_migration": False,
            "delete": False,
            "fake_PASS": False,
            "release_readiness_claimed": False,
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"[v110 PSP DRY-RUN] mongo_reachable={payload['mongo_reachable']} db_writes=0 -> {OUT}")
    sys.exit(0)

if __name__ == "__main__":
    main()
