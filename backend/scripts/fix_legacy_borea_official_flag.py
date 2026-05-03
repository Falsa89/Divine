#!/usr/bin/env python3
"""
RM1.22-F3 — Fix Legacy Borea Official Flag Conflict
═══════════════════════════════════════════════════════════════════════

Resetta `is_official=False` SOLO sul record DB legacy `id="borea"` che ha
canonical_id="greek_borea" e is_legacy_placeholder=True. Il record canonico
`id="greek_borea"` rimane is_official=True invariato.

Comportamento atteso post-fix:
    • DB heroes is_official=True count: 102 → 101 (= Character Bible)
    • Conflicting (is_official=True ∧ is_legacy_placeholder=True): 1 → 0
    • borea: is_official=False, is_legacy_placeholder=True (preservato)
    • greek_borea: invariato

DEFAULT: dry-run.
APPLY  : richiede env-var
        BOREA_FIX_CONFIRM=I_UNDERSTAND_THIS_WILL_FIX_LEGACY_BOREA_FLAG
        e flag --apply.

Uso:
    # Dry-run
    python backend/scripts/fix_legacy_borea_official_flag.py

    # Apply REALE (richiede env-var)
    BOREA_FIX_CONFIRM=I_UNDERSTAND_THIS_WILL_FIX_LEGACY_BOREA_FLAG \\
      python backend/scripts/fix_legacy_borea_official_flag.py --apply

Vincoli non negoziabili (verificati da filtro update_one):
  • Modifica SOLO il doc con id="borea" AND canonical_id="greek_borea"
    AND is_legacy_placeholder=True.
  • NON tocca is_legacy_placeholder, legacy_status, obtainable, show_in_*,
    do_not_delete, ownership, team references, canonical greek_borea.
  • NON cambia gacha rates, kit JSON, asset files, frontend.
"""
from __future__ import annotations
import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_DIR.parent
APP_ROOT = BACKEND_ROOT.parent
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(APP_ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv(BACKEND_ROOT / ".env")

from motor.motor_asyncio import AsyncIOMotorClient  # noqa: E402

ENV_CONFIRM_KEY = "BOREA_FIX_CONFIRM"
ENV_CONFIRM_VAL = "I_UNDERSTAND_THIS_WILL_FIX_LEGACY_BOREA_FLAG"
RESOLUTION_TAG = "RM1.22-F3_set_legacy_borea_is_official_false"


# Filtro difensivo: tutti e tre i criteri devono matchare per modificare.
TARGET_FILTER = {
    "id": "borea",
    "canonical_id": "greek_borea",
    "is_legacy_placeholder": True,
}


async def audit(db) -> dict:
    """Read-only audit del legacy borea + canonical greek_borea."""
    legacy = await db.heroes.find_one({"id": "borea"}, {"image_base64": 0})
    canon = await db.heroes.find_one({"id": "greek_borea"}, {"image_base64": 0})
    conflicts = await db.heroes.count_documents({
        "is_official": True, "is_legacy_placeholder": True,
    })
    target_match = await db.heroes.count_documents(TARGET_FILTER)
    return {
        "legacy": legacy,
        "canonical": canon,
        "conflicts_before": conflicts,
        "target_match": target_match,
    }


def print_audit(a: dict, label: str = "PRE") -> None:
    print("=" * 78)
    print(f" RM1.22-F3 — AUDIT {label}-FIX")
    print("=" * 78)
    legacy = a["legacy"]
    canon = a["canonical"]
    if legacy:
        print("  legacy borea (id='borea'):")
        for k in ("id", "canonical_id", "is_official", "is_legacy_placeholder",
                  "legacy_status", "asset_status", "obtainable",
                  "show_in_catalog", "show_in_summon", "do_not_delete",
                  "official_conflict_resolved_at", "official_conflict_resolution"):
            if k in legacy:
                print(f"    {k}: {legacy.get(k)!r}")
    else:
        print("  legacy borea: NOT FOUND")
    print()
    if canon:
        print("  canonical greek_borea (id='greek_borea'):")
        for k in ("id", "canonical_id", "is_official", "is_legacy_placeholder",
                  "asset_status", "obtainable", "show_in_catalog",
                  "show_in_summon", "do_not_delete"):
            if k in canon:
                print(f"    {k}: {canon.get(k)!r}")
    else:
        print("  canonical greek_borea: NOT FOUND")
    print()
    print(f"  conflicts (is_official=True ∧ is_legacy_placeholder=True): {a['conflicts_before']}")
    print(f"  target_filter match: {a['target_match']}")
    print("=" * 78)


def audit_passed(a: dict) -> bool:
    if not a["legacy"]:
        return False
    if not a["canonical"]:
        return False
    if a["target_match"] != 1:
        return False
    if a["conflicts_before"] > 1:
        return False
    if not a["legacy"].get("is_legacy_placeholder"):
        return False
    if a["canonical"].get("id") != "greek_borea":
        return False
    return True


async def main() -> int:
    ap = argparse.ArgumentParser(description="RM1.22-F3 — Fix legacy borea is_official flag")
    ap.add_argument("--apply", action="store_true",
                    help=f"Esegue il write reale. Richiede {ENV_CONFIRM_KEY}={ENV_CONFIRM_VAL}.")
    args = ap.parse_args()

    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "divine_waifus")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    # 1. Pre-audit
    pre = await audit(db)
    print_audit(pre, "PRE")
    if not audit_passed(pre):
        print("\n❌ AUDIT FAIL — stop.")
        client.close()
        return 1

    # 2. Decide
    if not args.apply:
        print("\n[DRY-RUN] Per scrivere usa --apply con env-var.")
        print(f"  filtro update : {TARGET_FILTER}")
        print("  $set fields   : is_official=False, official_conflict_resolved_at, official_conflict_resolution")
        print(f"  would_match   : {pre['target_match']}")
        client.close()
        return 0

    confirm = os.getenv(ENV_CONFIRM_KEY)
    if confirm != ENV_CONFIRM_VAL:
        print(f"\n❌ ABORT: {ENV_CONFIRM_KEY} non impostato.")
        print(f"   Atteso: {ENV_CONFIRM_VAL}")
        print(f"   Trovato: {confirm!r}")
        client.close()
        return 2

    # 3. Apply
    now_iso = datetime.utcnow().isoformat() + "Z"
    # Usa $set per idempotenza. Se official_conflict_resolution è già presente
    # (precedente run di F3), aggiorna solo i campi effettivi e traccia un
    # timestamp di re-fix separato (official_conflict_refixed_at).
    already_tagged = bool((pre.get("legacy") or {}).get("official_conflict_resolution"))
    set_doc = {
        "is_official": False,
        "official_conflict_resolution": RESOLUTION_TAG,
    }
    if already_tagged:
        set_doc["official_conflict_refixed_at"] = now_iso
    else:
        set_doc["official_conflict_resolved_at"] = now_iso
    update_doc = {"$set": set_doc}
    print("\n" + "=" * 78)
    print(" APPLY")
    print("=" * 78)
    res = await db.heroes.update_one(TARGET_FILTER, update_doc)
    print(f"  matched  : {res.matched_count}")
    print(f"  modified : {res.modified_count}")
    print("=" * 78)

    # 4. Post-audit
    post = await audit(db)
    print_audit(post, "POST")

    # Sanity: canonical greek_borea was NOT touched
    pre_c = pre["canonical"] or {}
    post_c = post["canonical"] or {}
    canonical_unchanged = all(
        pre_c.get(k) == post_c.get(k)
        for k in ("id", "canonical_id", "is_official", "is_legacy_placeholder",
                  "asset_status", "obtainable", "show_in_catalog",
                  "show_in_summon", "do_not_delete")
    )
    print(f"  canonical greek_borea unchanged: {'OK' if canonical_unchanged else 'FAIL'}")

    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
