#!/usr/bin/env python3
"""
RM1.20-D — Rollback restore script (DRY-RUN BY DEFAULT)
═══════════════════════════════════════════════════════════════════════
Ripristina il documento `heroes` dallo snapshot di backup creato da
`backup_roster_collections.py`. Default = DRY-RUN (mostra solo cosa
verrebbe ripristinato). L'apply richiede:
  • flag --apply
  • env var ROSTER_RESTORE_CONFIRM=I_UNDERSTAND_THIS_WILL_RESTORE_DB

Usage:
    python backend/scripts/restore_roster_backup.py \\
        --backup backend/backups/rm120d_pre_legacy_soft_deactivation_<ts>.json
    # dry-run

    ROSTER_RESTORE_CONFIRM=I_UNDERSTAND_THIS_WILL_RESTORE_DB \\
    python backend/scripts/restore_roster_backup.py \\
        --backup backend/backups/...json --apply --collection heroes
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(BACKEND_ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv(BACKEND_ROOT / ".env")

from motor.motor_asyncio import AsyncIOMotorClient  # noqa: E402


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


async def main() -> int:
    ap = argparse.ArgumentParser(description="RM1.20-D — Restore roster backup (DRY-RUN by default)")
    ap.add_argument("--backup", required=True, help="Path al file di backup JSON.")
    ap.add_argument("--apply", action="store_true", help="Esegue il restore live (richiede env var).")
    ap.add_argument(
        "--collection",
        default="heroes",
        choices=["heroes", "user_heroes", "teams", "users"],
        help="Quale collection ripristinare (default: heroes).",
    )
    args = ap.parse_args()

    backup_path = Path(args.backup).resolve()
    if not backup_path.is_file():
        print(f"❌ Backup file non trovato: {backup_path}")
        return 1

    sha = _sha256(backup_path)
    print(f"  backup file: {backup_path}")
    print(f"  size       : {backup_path.stat().st_size} bytes")
    print(f"  sha256     : {sha}")

    with open(backup_path, encoding="utf-8") as f:
        bp: Dict[str, Any] = json.load(f)

    cols: Dict[str, List[Dict[str, Any]]] = bp.get("collections", {})
    target_docs = cols.get(args.collection, [])
    print(f"  target col : {args.collection}")
    print(f"  doc count  : {len(target_docs)}")

    if not args.apply:
        print()
        print("=" * 70)
        print(" DRY-RUN — Nessuna scrittura DB.")
        print(" Per restore live:")
        print(f"   ROSTER_RESTORE_CONFIRM=I_UNDERSTAND_THIS_WILL_RESTORE_DB \\")
        print(f"   python backend/scripts/restore_roster_backup.py \\")
        print(f"     --backup {backup_path} --apply --collection {args.collection}")
        print("=" * 70)
        return 0

    confirm = os.getenv("ROSTER_RESTORE_CONFIRM", "")
    if confirm != "I_UNDERSTAND_THIS_WILL_RESTORE_DB":
        print("❌ Env var ROSTER_RESTORE_CONFIRM mancante o errata. Aborto.")
        return 2

    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "divine_waifus")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    # Restore: per ogni documento backup, $set TUTTI i campi del backup,
    # $unset dei campi eventualmente aggiunti dopo (es. flag legacy
    # introdotti da RM1.20-D che NON erano nel backup).
    NEW_FIELDS_RM120D = [
        "is_official", "is_legacy_placeholder", "legacy_status",
        "obtainable", "show_in_catalog", "show_in_summon",
        "show_in_hero_collection", "show_in_battle_picker",
        "do_not_delete", "deactivated_at", "deactivated_at_planned",
        "deactivation_reason",
    ]
    restored = 0
    for doc in target_docs:
        hid = doc.get("id")
        if not hid:
            continue
        # campi da rimuovere se non presenti nel backup
        unset = {k: "" for k in NEW_FIELDS_RM120D if k not in doc}
        update_op: Dict[str, Any] = {"$set": doc}
        if unset:
            update_op["$unset"] = unset
        res = await db[args.collection].update_one({"id": hid}, update_op, upsert=True)
        if res.matched_count or res.upserted_id:
            restored += 1

    print(f"  ✓ Restored {restored}/{len(target_docs)} documents into '{args.collection}'.")
    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
