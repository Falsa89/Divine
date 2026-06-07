#!/usr/bin/env python3
"""v110 pre/post smoke DB snapshot - read-only counts. Never writes."""
import json, os, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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


def _c(db, name):
    try:
        return int(db[name].count_documents({})) if db is not None else None
    except Exception:
        return None


def snapshot(label_key, track_label):
    db = _try_db()
    counts = {
        "users": _c(db, "users"),
        "player_server_profiles": _c(db, "player_server_profiles"),
        "user_heroes": _c(db, "user_heroes"),
        "team_formation": _c(db, "team_formation"),
        "user_inventory": _c(db, "user_inventory"),
        "user_equipment": _c(db, "user_equipment"),
        "battlepass_progress": _c(db, "battlepass_progress"),
        "vip_progress": _c(db, "vip_progress"),
        "user_mail": _c(db, "user_mail"),
        "achievements": _c(db, "achievements"),
        "story_progress": _c(db, "story_progress"),
        "tower_progress": _c(db, "tower_progress"),
        "arena_mmr": _c(db, "arena_mmr"),
        "guild_membership": _c(db, "guild_membership"),
        "guild_wars": _c(db, "guild_wars"),
        "chat_messages": _c(db, "chat_messages"),
        "rankings": _c(db, "rankings"),
        "battle_instances": _c(db, "battle_instances"),
        "bots": _c(db, "bots"),
        "migration_logs": _c(db, "migration_logs"),
    }
    return {
        "pack": "MEGA_RELEASE_ACCELERATION_72_v110_PSP_APPLY_STAGING_SMOKE_LIMITED",
        "track": track_label,
        "sentinel": "PUBLIC_SYNC_TAG_v110_PSP_APPLY_STAGING_SMOKE_LIMITED",
        "snapshot_kind": label_key,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "read_only": True,
        "db_writes": 0,
        "mongo_reachable": db is not None,
        "counts": counts,
        "safety_flags": {
            "db_write": False,
            "fake_PASS": False,
        },
    }


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("pre", "post"):
        print("usage: snapshot_v110_smoke.py [pre|post]")
        sys.exit(2)
    kind = sys.argv[1]
    if kind == "pre":
        out = os.path.join(ROOT, "data/design/v110_psp_apply_staging_smoke/v110_pre_smoke_db_snapshot_v1.json")
        track = "C"
        label = "pre_smoke"
    else:
        out = os.path.join(ROOT, "data/design/v110_psp_apply_staging_smoke/v110_post_smoke_final_snapshot_v1.json")
        track = "I"
        label = "post_smoke"
    payload = snapshot(label, track)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(payload, open(out, "w"), indent=2, ensure_ascii=False)
    print(f"[v110 SNAPSHOT {kind.upper()}] mongo_reachable={payload['mongo_reachable']} db_writes=0 -> {out}")
    sys.exit(0)


if __name__ == "__main__":
    main()
