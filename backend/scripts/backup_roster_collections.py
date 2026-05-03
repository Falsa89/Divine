#!/usr/bin/env python3
"""
RM1.20-D / RM1.20-E — Mandatory pre-apply backup of roster collections.
Read-only export of heroes/user_heroes/teams/users to a JSON file in
backend/backups/. Computes SHA256 of the file. Does NOT touch DB.

Usage:
    cd /app && python backend/scripts/backup_roster_collections.py [--label LABEL]

Default label: "pre_apply".
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(BACKEND_ROOT.parent))

from dotenv import load_dotenv  # noqa: E402
load_dotenv(BACKEND_ROOT / ".env")

from motor.motor_asyncio import AsyncIOMotorClient  # noqa: E402

BACKUPS_DIR = BACKEND_ROOT / "backups"
BACKUPS_DIR.mkdir(exist_ok=True)


def _scrub(d):
    """Convert ObjectId/datetime to JSON-safe primitives (passwords kept as-is in dev backup)."""
    if isinstance(d, list):
        return [_scrub(x) for x in d]
    if isinstance(d, dict):
        return {k: _scrub(v) for k, v in d.items()}
    if isinstance(d, datetime):
        return d.isoformat() + "Z"
    if hasattr(d, "binary"):  # ObjectId
        return str(d)
    return d


async def main() -> int:
    ap = argparse.ArgumentParser(description="RM1.20-D/E — Roster collections backup")
    ap.add_argument(
        "--label",
        default="pre_apply",
        help="Label for the backup filename (e.g. rm120d_pre_legacy_soft_deactivation, rm120e_pre_official_roster_import).",
    )
    args = ap.parse_args()

    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "divine_waifus")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    collections = ["heroes", "user_heroes", "teams", "users"]
    payload = {
        "task": "RM1.20-D",
        "kind": "pre_apply_backup",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "db_name": db_name,
        "collections": {},
    }
    counts = {}
    for col in collections:
        # heroes: drop image_base64 to keep file small
        proj = {"image_base64": 0} if col == "heroes" else None
        cursor = db[col].find({}, proj) if proj else db[col].find({})
        docs = await cursor.to_list(length=None)
        # strip mongo _id (we keep id field which is the canonical one)
        for d in docs:
            d.pop("_id", None)
        counts[col] = len(docs)
        payload["collections"][col] = _scrub(docs)
    payload["counts"] = counts

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = BACKUPS_DIR / f"{args.label}_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str, ensure_ascii=False)

    sha = hashlib.sha256()
    with open(out_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)

    print("=" * 78)
    print(" RM1.20-D — MANDATORY PRE-APPLY BACKUP")
    print("=" * 78)
    print(f"  path     : {out_path}")
    print(f"  size     : {out_path.stat().st_size} bytes")
    print(f"  sha256   : {sha.hexdigest()}")
    print(f"  counts   :")
    for k, v in counts.items():
        print(f"    • {k:14s} = {v}")
    print(f"  gitignore: backend/backups/ è già escluso da .gitignore (RM1.17-J)")
    print("=" * 78)

    client.close()
    # Print machine-parseable footer for CI/agent consumption
    print(f"BACKUP_PATH={out_path}")
    print(f"BACKUP_SHA256={sha.hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
