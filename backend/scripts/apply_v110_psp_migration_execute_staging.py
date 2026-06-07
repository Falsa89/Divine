#!/usr/bin/env python3
"""v110 PSP apply EXECUTE on staging clone ONLY.

Hard guards:
- DB_NAME must contain BOTH 'staging' and 'clone'
- environment_markers.v110_staging_clone_confirmed=true MUST exist in target DB
- All 5 required flags must be YES
- MONGO_URL must be localhost (no mongodb+srv)
- Production marker absence verified

If any guard fails -> APPLY_REFUSED + db_writes=0 + exit 0.

Performs upserts of player_server_profiles + adds server_id field to user_heroes/team_formation/user_equipment.
Records audit log in migration_logs.v110_psp_apply collection.

CLI:
  --execute            actually upsert (otherwise plan-only)
  --plan-only          alias for "no --execute"
  --limit N            limit users processed (smoke)
  --target-server-id   server_id to assign (default s1)
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "data/design/v110_psp_apply_staging_execute/v110_limited_psp_apply_execute_result_v1.json")

REQUIRED_FLAGS = [
    "V110_PSP_APPLY",
    "V110_BACKUP_CONFIRMED",
    "V110_STAGING_DB_CONFIRMED",
    "V110_USER_EXPLICIT_DB_WRITE_APPROVAL",
    "V110_ROLLBACK_PLAN_CONFIRMED",
]
PRODUCTION_FLAG = "V110_PRODUCTION_DB_EXPLICIT_APPROVAL"
MIGRATION_SOURCE = "v110_psp_apply_v1"
AUDIT_COLLECTION = "migration_logs"


def _utc():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _try_client():
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(ROOT, "backend", ".env"))
    except Exception:
        pass
    try:
        from pymongo import MongoClient
        url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
        client = MongoClient(url, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        return client, url
    except Exception:
        return None, os.environ.get("MONGO_URL", "")


def _verify_staging_target(db, db_name, url):
    """Hard guards: returns (ok, reason)."""
    name_lower = db_name.lower()
    if "staging" not in name_lower or "clone" not in name_lower:
        return False, f"db_name='{db_name}' must contain both 'staging' AND 'clone'"
    if url.startswith("mongodb+srv://"):
        return False, "srv cluster mongo URL forbidden in staging execute"
    if "localhost" not in url and "127.0.0.1" not in url:
        return False, f"mongo url must be localhost in this pack, got: {url}"
    marker = db["environment_markers"].find_one({"marker": "v110_staging_clone_confirmed", "value": True})
    if not marker:
        return False, "missing environment_markers.v110_staging_clone_confirmed=true in target db"
    prod_marker = db["environment_markers"].find_one({"marker": "production", "value": True})
    if prod_marker:
        return False, "production marker found in target db; refusing"
    return True, "staging_clone_confirmed_with_marker"


def _build_psp_doc(user_doc, server_id):
    uid = str(user_doc.get("_id"))
    now = _utc()
    return {
        "user_id": uid,
        "server_id": server_id,
        "profile_id": f"{uid}:{server_id}",
        "created_at": now,
        "updated_at": now,
        "server_created_at": now,
        "player_level": int(user_doc.get("level", 1)),
        "player_exp": int(user_doc.get("experience", 0)),
        "selected_team_id": None,
        "soft_currencies": (user_doc.get("currencies", {}) or {}).get("soft", {}),
        "story_progress": {},
        "tower_progress": {},
        "arena_mmr": None,
        "guild_id": None,
        "battlepass_state": {},
        "mail_unread_count": 0,
        "achievements_state": {},
        "shop_state": {},
        "last_seen_at": user_doc.get("last_login"),
        "migration_source": MIGRATION_SOURCE,
    }


def _safe_set_server_id(coll, user_id, server_id, audit):
    """Add server_id field to docs that don't have it. Non-destructive."""
    res = coll.update_many(
        {"user_id": user_id, "server_id": {"$exists": False}},
        {"$set": {"server_id": server_id}},
    )
    audit["update_results"].append({"coll": coll.name, "user_id": user_id, "matched": res.matched_count, "modified": res.modified_count})
    return res.modified_count


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--execute", action="store_true")
    p.add_argument("--plan-only", action="store_true")
    p.add_argument("--target-server-id", default="s1")
    p.add_argument("--limit", type=int, default=0)
    args = p.parse_args(argv)

    missing_flags = [f for f in REQUIRED_FLAGS if os.environ.get(f, "").upper() != "YES"]
    production_approval = os.environ.get(PRODUCTION_FLAG, "").upper() == "YES"

    client, url = _try_client()
    db_name = os.environ.get("DB_NAME", "")
    db = client[db_name] if client is not None and db_name else None
    safety = {
        "db_write_to_production": False,
        "db_write_to_source": False,
        "destructive_migration": False,
        "delete": False,
        "premium_grant": False,
        "currency_duplication": False,
        "reward_live": False,
        "progress_live": False,
        "fake_PASS": False,
        "release_readiness_claimed": False,
    }
    base_out = {
        "pack": "MEGA_RELEASE_ACCELERATION_74_v110_PSP_APPLY_STAGING_SMOKE_EXECUTE",
        "track": "E",
        "sentinel": "PUBLIC_SYNC_TAG_v110_PSP_APPLY_STAGING_SMOKE_EXECUTE",
        "generated_at_utc": _utc(),
        "db_name": db_name,
        "mongo_url_kind": "srv" if url.startswith("mongodb+srv://") else ("localhost" if ("localhost" in url or "127.0.0.1" in url) else "other"),
        "production_apply_executed": False,
        "production_flag_present": production_approval,
        "required_flags": REQUIRED_FLAGS,
        "missing_flags": missing_flags,
        "cli_args": {"execute": args.execute, "plan_only": args.plan_only, "target_server_id": args.target_server_id, "limit": args.limit},
        "safety_flags": safety,
    }

    if missing_flags:
        base_out.update({"status": "APPLY_REFUSED_MISSING_FLAGS", "reason": "required flags not all YES", "apply_executed": False, "db_writes": 0})
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(base_out, open(OUT, "w"), indent=2, ensure_ascii=False)
        print(f"[v110 APPLY EXECUTE STAGING] status=APPLY_REFUSED_MISSING_FLAGS missing={missing_flags}")
        sys.exit(0)

    if client is None or db is None:
        base_out.update({"status": "APPLY_REFUSED_NO_DB", "reason": "mongo unreachable or DB_NAME unset", "apply_executed": False, "db_writes": 0})
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(base_out, open(OUT, "w"), indent=2, ensure_ascii=False)
        print("[v110 APPLY EXECUTE STAGING] status=APPLY_REFUSED_NO_DB")
        sys.exit(0)

    ok, reason = _verify_staging_target(db, db_name, url)
    if not ok:
        base_out.update({"status": "APPLY_REFUSED_NOT_STAGING_CLONE", "reason": reason, "apply_executed": False, "db_writes": 0})
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(base_out, open(OUT, "w"), indent=2, ensure_ascii=False)
        print(f"[v110 APPLY EXECUTE STAGING] status=APPLY_REFUSED_NOT_STAGING_CLONE reason={reason}")
        sys.exit(0)

    # Build plan
    cur = db["users"].find({}, {"_id": 1, "level": 1, "experience": 1, "currencies": 1, "last_login": 1}).sort("_id", 1)
    if args.limit and args.limit > 0:
        cur = cur.limit(args.limit)
    user_docs = list(cur)
    user_ids = [str(u["_id"]) for u in user_docs]
    existing_psp = list(db["player_server_profiles"].find(
        {"user_id": {"$in": user_ids}, "server_id": args.target_server_id},
        {"user_id": 1, "server_id": 1},
    ))
    existing_keys = {(str(p["user_id"]), p["server_id"]) for p in existing_psp}
    plan = {
        "target_server_id": args.target_server_id,
        "users_in_scope": len(user_ids),
        "psp_already_present_for_server": len(existing_psp),
        "psp_to_upsert": len(user_ids),
        "user_heroes_potential_updates": db["user_heroes"].count_documents({"user_id": {"$in": user_ids}, "server_id": {"$exists": False}}),
        "team_formation_potential_updates": db["team_formation"].count_documents({"user_id": {"$in": user_ids}, "server_id": {"$exists": False}}),
        "user_equipment_potential_updates": db["user_equipment"].count_documents({"user_id": {"$in": user_ids}, "server_id": {"$exists": False}}),
    }
    base_out["plan"] = plan
    base_out["target_marker_present"] = True

    if not args.execute or args.plan_only:
        base_out.update({"status": "PLAN_ONLY_NO_WRITE", "reason": "plan_only or --execute not set", "apply_executed": False, "db_writes": 0})
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(base_out, open(OUT, "w"), indent=2, ensure_ascii=False)
        print(f"[v110 APPLY EXECUTE STAGING] status=PLAN_ONLY_NO_WRITE plan_users={plan['users_in_scope']}")
        sys.exit(0)

    # EXECUTE on staging clone
    audit = {"started_at_utc": _utc(), "limit": args.limit, "target_server_id": args.target_server_id, "psp_inserts": [], "psp_updates": [], "update_results": []}
    psp_inserted = 0
    psp_skipped_existing = 0
    user_heroes_modified = 0
    team_modified = 0
    equipment_modified = 0
    for u in user_docs:
        uid = str(u["_id"])
        key = (uid, args.target_server_id)
        psp_doc = _build_psp_doc(u, args.target_server_id)
        if key in existing_keys:
            # Non-destructive update only of updated_at, last_seen_at fields
            res = db["player_server_profiles"].update_one(
                {"user_id": uid, "server_id": args.target_server_id},
                {"$set": {"updated_at": psp_doc["updated_at"], "last_seen_at": psp_doc["last_seen_at"]}},
            )
            psp_skipped_existing += 1
            audit["psp_updates"].append({"user_id": uid, "server_id": args.target_server_id, "modified": res.modified_count})
        else:
            ins = db["player_server_profiles"].insert_one(psp_doc)
            psp_inserted += 1
            audit["psp_inserts"].append({"user_id": uid, "server_id": args.target_server_id, "_id": str(ins.inserted_id)})
        user_heroes_modified += _safe_set_server_id(db["user_heroes"], uid, args.target_server_id, audit)
        team_modified += _safe_set_server_id(db["team_formation"], uid, args.target_server_id, audit)
        equipment_modified += _safe_set_server_id(db["user_equipment"], uid, args.target_server_id, audit)

    audit["ended_at_utc"] = _utc()
    audit["psp_inserted"] = psp_inserted
    audit["psp_skipped_existing"] = psp_skipped_existing
    audit["user_heroes_modified"] = user_heroes_modified
    audit["team_modified"] = team_modified
    audit["equipment_modified"] = equipment_modified
    audit["migration_source"] = MIGRATION_SOURCE
    db[AUDIT_COLLECTION].insert_one({"kind": "v110_psp_apply_run", **audit})

    total_writes = psp_inserted + psp_skipped_existing + user_heroes_modified + team_modified + equipment_modified
    base_out.update({
        "status": "APPLY_EXECUTED_STAGING_LIMITED",
        "reason": "staging clone confirmed; limited apply executed",
        "apply_executed": True,
        "db_writes": total_writes,
        "psp_inserted_in_this_run": psp_inserted,
        "psp_existing_re_run_updates": psp_skipped_existing,
        "user_heroes_server_id_set": user_heroes_modified,
        "team_formation_server_id_set": team_modified,
        "user_equipment_server_id_set": equipment_modified,
        "audit_collection": AUDIT_COLLECTION,
        "migration_source": MIGRATION_SOURCE,
    })
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(base_out, open(OUT, "w"), indent=2, ensure_ascii=False)
    print(f"[v110 APPLY EXECUTE STAGING] status=APPLY_EXECUTED psp_inserted={psp_inserted} reapply={psp_skipped_existing} user_heroes_set={user_heroes_modified} team_set={team_modified} equipment_set={equipment_modified}")
    sys.exit(0)


if __name__ == "__main__":
    main()
