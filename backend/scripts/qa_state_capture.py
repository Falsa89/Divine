#!/usr/bin/env python3
"""
Pack 126 — Before/After state capture for QA preview combat.
Reads account/hero/currency/progress state for the test account and
writes a JSON snapshot. Used to prove NO mutation after preview combat.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parents[2]


def _fail(msg: str, code: int = 2) -> None:
    print(f"FAIL  {msg}")
    sys.exit(code)


def main() -> int:
    parser = argparse.ArgumentParser(description="Pack 126 before/after state capture.")
    parser.add_argument("--account", required=True, help="user_id (UUID)")
    parser.add_argument("--server-id", default=None)
    parser.add_argument("--label", default="snapshot", help="before|after|<label>")
    parser.add_argument("--out", default=None, help="Output path (default: auto)")
    args = parser.parse_args()

    try:
        from pymongo import MongoClient
        from dotenv import load_dotenv
    except ImportError:
        _fail("pymongo/dotenv missing")

    load_dotenv(REPO_ROOT / "backend" / ".env")
    mongo_url = os.environ.get("MONGO_URL")
    if not mongo_url:
        _fail("MONGO_URL missing")

    client = MongoClient(mongo_url)
    try:
        db = client.get_default_database()
    except Exception:
        db = None
    if db is None:
        names = client.list_database_names()
        db_name = next((n for n in names if n not in ("admin", "local", "config")), None)
        if not db_name:
            _fail("no DB available")
        db = client[db_name]

    uid = args.account
    sid = args.server_id

    snap: dict = {
        "pack": "PACK_126_BEFORE_AFTER_STATE",
        "label": args.label,
        "ts": int(time.time()),
        "ts_iso": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "account": uid,
        "server_id": sid,
        "db_name": db.name,
    }

    # users
    u = db.users.find_one({"id": uid}) or {}
    snap["user"] = {
        "email": u.get("email"),
        "username": u.get("username"),
        "level": u.get("level"),
        "exp": u.get("exp"),
        "diamonds": u.get("diamonds"),
        "gold": u.get("gold"),
        "energy": u.get("energy"),
        "vip_level": u.get("vip_level"),
        "battlepass_level": u.get("battlepass_level"),
    }

    # PSPs
    psp_query = {"user_id": uid}
    if sid:
        psp_query["server_id"] = sid
    psps = list(db.player_server_profiles.find(psp_query))
    snap["psps"] = []
    for p in psps:
        snap["psps"].append({
            "server_id": p.get("server_id"),
            "team_formation_size": len(p.get("team_formation") or []),
            "team_formation": p.get("team_formation"),
            "story_progress": p.get("story_progress"),
            "tower_progress": p.get("tower_progress"),
            "arena_rank": p.get("arena_rank"),
            "arena_mmr": p.get("arena_mmr"),
        })

    # user_heroes (count + hashes)
    uh_query = {"user_id": uid}
    if sid:
        uh_query["server_id"] = sid
    heroes = list(db.user_heroes.find(uh_query, {
        "hero_id": 1, "level": 1, "exp": 1, "stars": 1, "power": 1, "server_id": 1, "_qa_seed": 1,
    }))
    snap["user_heroes_count"] = len(heroes)
    snap["user_heroes_by_server"] = dict(Counter([h.get("server_id", "<none>") for h in heroes]))
    snap["user_heroes_total_exp"] = sum((h.get("exp") or 0) for h in heroes)
    snap["user_heroes_total_levels"] = sum((h.get("level") or 0) for h in heroes)
    snap["user_heroes_total_power"] = sum((h.get("power") or 0) for h in heroes)
    snap["user_heroes_qa_seed_count"] = sum(1 for h in heroes if h.get("_qa_seed"))
    snap["user_heroes_sample"] = [
        {"hero_id": h.get("hero_id"), "level": h.get("level"), "exp": h.get("exp"), "server_id": h.get("server_id")}
        for h in heroes[:20]
    ]

    # Inventory / materials
    inv = db.user_inventory.find_one({"user_id": uid}) if "user_inventory" in db.list_collection_names() else None
    if inv:
        snap["inventory_keys"] = sorted(list(inv.keys()))
        snap["inventory_item_count"] = sum(1 for v in (inv.get("items") or {}).values() if v) if isinstance(inv.get("items"), dict) else None
    else:
        snap["inventory_keys"] = None

    # Mail
    mail_count = db.mail.count_documents({"user_id": uid}) if "mail" in db.list_collection_names() else 0
    snap["mail_count"] = mail_count

    out_path = Path(args.out) if args.out else (REPO_ROOT / "backend" / "scripts" / "reports" / f"pack_126_state_{args.label}_{snap['ts']}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(snap, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"OK    state captured: {out_path}")
    print(f"      user_heroes count={snap['user_heroes_count']}, total_exp={snap['user_heroes_total_exp']}, qa_seed={snap['user_heroes_qa_seed_count']}")
    print(f"      psps: {len(snap['psps'])}, diamonds={snap['user'].get('diamonds')}, gold={snap['user'].get('gold')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
