#!/usr/bin/env python3
"""
Pack 124 — QA Team Seed Clear / Rollback.

Rimuove SOLO i documenti `user_heroes` taggati con `_qa_seed: true` e
`_qa_seed_pack: "pack_124"` per l'account specificato. Non tocca eroi
reali ne dati economy/gacha/shop.

Usage:
  QA_SEED_ENABLED=true python3 backend/scripts/qa_team_seed_clear.py \\
      --allow-account <user_id> [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _fail(msg: str, code: int = 2) -> None:
    print(f"FAIL  {msg}")
    sys.exit(code)


def main() -> int:
    parser = argparse.ArgumentParser(description="Pack 124 QA team seed clear.")
    parser.add_argument("--allow-account", dest="account", default=None, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if os.environ.get("QA_SEED_ENABLED", "").lower() != "true":
        _fail("QA_SEED_ENABLED env var must be 'true' (gate fail-closed)")

    try:
        from pymongo import MongoClient  # type: ignore
        from dotenv import load_dotenv  # type: ignore
    except ImportError:
        _fail("pymongo / python-dotenv non installati")

    load_dotenv(REPO_ROOT / "backend" / ".env")
    mongo_url = os.environ.get("MONGO_URL")
    if not mongo_url:
        _fail("MONGO_URL non trovato in backend/.env")

    client = MongoClient(mongo_url)  # type: ignore[arg-type]
    try:
        db = client.get_default_database()
    except Exception:
        db = None
    if db is None:
        names = client.list_database_names()
        db_name = next((n for n in names if n not in ("admin", "local", "config")), None)
        if not db_name:
            _fail("nessun database disponibile")
        db = client[db_name]  # type: ignore[index]

    user_heroes_col = db["user_heroes"]
    query = {"user_id": args.account, "_qa_seed": True, "_qa_seed_pack": "pack_124"}
    count = user_heroes_col.count_documents(query)
    print(f"OK    documenti QA seed trovati: {count}")
    if args.dry_run:
        print("OK    --dry-run: nessuna eliminazione")
        deleted = 0
    else:
        res = user_heroes_col.delete_many(query)
        deleted = res.deleted_count
        print(f"OK    documenti eliminati: {deleted}")

    out_dir = REPO_ROOT / "backend" / "scripts" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    report = {
        "pack": "PRE_QA_PACK_124_QA_TEAM_SEED_CLEAR",
        "validator": "qa_team_seed_clear",
        "status": "PASS",
        "account": args.account,
        "dry_run": args.dry_run,
        "found": count,
        "deleted": deleted,
        "ts": ts,
    }
    out_path = out_dir / f"pack_124_qa_team_seed_clear_{ts}.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK    report: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
