#!/usr/bin/env python3
"""
RM1.20-A — Legacy Soft-Deactivation Plan (DRY-RUN BY DEFAULT)
═══════════════════════════════════════════════════════════════════════
Genera il PIANO di soft-deactivation per i placeholder legacy e di
canonicalizzazione per gli eroi ufficiali presenti nel DB.

Garanzie di sicurezza:
  • Default: DRY-RUN. NESSUNA scrittura su DB.
  • Il piano viene serializzato in JSON in backend/reports/.
  • Il flag `--apply` esiste per uso FUTURO ma in RM1.20-A NON va eseguito.
  • Nessun DELETE, mai. user_heroes / teams / users non vengono toccati.

Uso:
    cd /app && python backend/scripts/plan_legacy_soft_deactivation.py
    # dry-run, scrive solo il piano JSON.

Uso futuro (NON in RM1.20-A):
    cd /app && python backend/scripts/plan_legacy_soft_deactivation.py --apply
"""
from __future__ import annotations
import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(BACKEND_ROOT.parent))

from dotenv import load_dotenv  # noqa: E402
load_dotenv(BACKEND_ROOT / ".env")

from motor.motor_asyncio import AsyncIOMotorClient  # noqa: E402
from data.character_bible import (  # noqa: E402
    CHARACTER_BIBLE_BY_ID,
    LAUNCH_BASE_HERO_IDS,
    EXTRA_PREMIUM_HERO_IDS,
    normalize_element,
    normalize_role,
    normalize_faction,
    get_max_stars,
)

REPORTS_DIR = BACKEND_ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


# ════════════════════════════════════════════════════════════════════════
# Builder dei payload di update (PURE)
# ════════════════════════════════════════════════════════════════════════

def build_official_update_payload(bible_entry: Dict[str, Any]) -> Dict[str, Any]:
    """Payload che marca un eroe come ufficiale e canonicalizza i campi.
    NON sovrascrive image/base_stats/skills: la canonicalizzazione vera e
    propria di asset/skills sarà gestita dall'import roster ufficiale in
    una task successiva."""
    hid = bible_entry["id"]
    in_extra = hid in EXTRA_PREMIUM_HERO_IDS
    release_group = "launch_extra_premium" if in_extra else "launch_base"
    native_rarity = int(bible_entry["native_rarity"])
    return {
        "is_official": True,
        "is_legacy_placeholder": False,
        "legacy_status": None,
        "release_group": release_group,
        "native_rarity": native_rarity,
        "max_stars": get_max_stars(native_rarity),
        "canonical_element": normalize_element(bible_entry["element"]),
        "canonical_role": normalize_role(bible_entry["role"]),
        "canonical_faction": normalize_faction(bible_entry["faction"]),
        "obtainable": True,
        "show_in_catalog": True,
        "show_in_summon": True,
        "show_in_hero_collection": True,
        "show_in_battle_picker": True,
        "do_not_delete": True,
    }


def build_legacy_deactivation_payload(
    db_hero: Dict[str, Any],
    *,
    deactivation_reason: str = "legacy_placeholder_pre_official_roster",
) -> Dict[str, Any]:
    """Payload di soft-deactivation per un placeholder legacy.
    Conservativo: il legacy resta visibile SOLO ai giocatori che lo
    possiedono, mai cancellato, mai forzato fuori da team già attivi."""
    return {
        "is_official": False,
        "is_legacy_placeholder": True,
        "legacy_status": "deprecated_placeholder",
        "obtainable": False,
        "show_in_catalog": False,
        "show_in_summon": False,
        "show_in_hero_collection": "owned_only",
        "show_in_battle_picker": "owned_only",
        "do_not_delete": True,
        "deactivation_reason": deactivation_reason,
        "deactivated_at_planned": datetime.utcnow().isoformat() + "Z",
    }


def _redact_mongo(url: str) -> str:
    return url.split("@")[-1] if "@" in url else url


# ════════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════════

async def run(apply_changes: bool) -> int:
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "divine_waifus")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    db_heroes: List[Dict[str, Any]] = await db.heroes.find(
        {}, {"image_base64": 0}
    ).to_list(length=None)
    db_ids = {h.get("id") for h in db_heroes if h.get("id")}
    bible_ids = set(CHARACTER_BIBLE_BY_ID.keys())

    official_in_db_ids = sorted(db_ids & bible_ids)
    legacy_in_db_ids = sorted(db_ids - bible_ids)

    # ── ownership impact (count only, niente write) ────────────────────
    ownership_count: Dict[str, int] = {}
    cur = db.user_heroes.find({}, {"hero_id": 1})
    async for uh in cur:
        hid = uh.get("hero_id")
        if hid:
            ownership_count[hid] = ownership_count.get(hid, 0) + 1

    # ── piano per eroi ufficiali presenti nel DB ───────────────────────
    plan_official: List[Dict[str, Any]] = []
    for hid in official_in_db_ids:
        entry = CHARACTER_BIBLE_BY_ID[hid]
        payload = build_official_update_payload(entry)
        plan_official.append({
            "hero_id": hid,
            "display_name": entry.get("display_name"),
            "release_group": payload["release_group"],
            "owned_by_users": ownership_count.get(hid, 0),
            "match_filter": {"id": hid},
            "update_payload": {"$set": payload},
        })

    # ── piano per legacy placeholders ──────────────────────────────────
    plan_legacy: List[Dict[str, Any]] = []
    for hid in legacy_in_db_ids:
        h = next((x for x in db_heroes if x.get("id") == hid), {}) or {}
        payload = build_legacy_deactivation_payload(h)
        plan_legacy.append({
            "hero_id": hid,
            "display_name": h.get("name"),
            "owned_by_users": ownership_count.get(hid, 0),
            "match_filter": {"id": hid},
            "update_payload": {"$set": payload},
            "user_heroes_preserved": True,
            "teams_preserved": True,
        })

    # ── eroi ufficiali mancanti (non oggetto di update — saranno INSERT
    # nella fase di import ufficiale del roster, NON in questo task) ───
    plan_missing_imports: List[Dict[str, Any]] = []
    for hid in sorted(bible_ids - db_ids):
        entry = CHARACTER_BIBLE_BY_ID[hid]
        plan_missing_imports.append({
            "hero_id": hid,
            "display_name": entry.get("display_name"),
            "native_rarity": entry["native_rarity"],
            "release_group": (
                "launch_extra_premium"
                if hid in EXTRA_PREMIUM_HERO_IDS
                else "launch_base"
            ),
            "note": (
                "INSERT da eseguire dall'import roster ufficiale in task "
                "successiva (non in RM1.20-A)."
            ),
        })

    plan: Dict[str, Any] = {
        "task": "RM1.20-A",
        "kind": "soft_deactivation_plan",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "dry_run": not apply_changes,
        "apply_flag_executed": False,
        "db": {
            "mongo_url_redacted": _redact_mongo(mongo_url),
            "db_name": db_name,
        },
        "summary": {
            "official_in_db": len(plan_official),
            "legacy_to_deactivate": len(plan_legacy),
            "official_missing_to_import_later": len(plan_missing_imports),
            "user_heroes_will_be_modified": False,
            "teams_will_be_modified": False,
            "deletions_planned": 0,
        },
        "schemas": {
            "official_update_fields": list(
                build_official_update_payload(
                    next(iter(CHARACTER_BIBLE_BY_ID.values()))
                ).keys()
            ),
            "legacy_deactivation_fields": list(
                build_legacy_deactivation_payload({}).keys()
            ),
        },
        "plan_official_canonicalize": plan_official,
        "plan_legacy_soft_deactivate": plan_legacy,
        "plan_missing_official_imports": plan_missing_imports,
        "safety": {
            "db_writes_performed": False,  # aggiornato sotto se --apply
            "user_heroes_modified": False,
            "teams_modified": False,
            "users_modified": False,
            "heroes_deleted": False,
        },
        "policy_doc": "docs/ROSTER_IMPORT_AND_LEGACY_POLICY.md",
    }

    # ── Console output ────────────────────────────────────────────────
    print("=" * 78)
    print(" RM1.20-A — PIANO DI SOFT-DEACTIVATION  ({})".format(
        "APPLY (LIVE)" if apply_changes else "DRY-RUN"
    ))
    print("=" * 78)
    print(f" DB:                              {db_name}")
    print(f" Eroi ufficiali nel DB:           {len(plan_official)}")
    print(f" Legacy da soft-deactivare:       {len(plan_legacy)}")
    print(f" Ufficiali mancanti (INSERT in fase futura): {len(plan_missing_imports)}")
    print()

    print(" Campi pianificati per UFFICIALI:")
    for k in plan["schemas"]["official_update_fields"]:
        print(f"   • {k}")
    print()
    print(" Campi pianificati per LEGACY:")
    for k in plan["schemas"]["legacy_deactivation_fields"]:
        print(f"   • {k}")
    print()

    if plan_legacy:
        print(" Preview legacy (primi 10):")
        for item in plan_legacy[:10]:
            print(
                f"   - {item['hero_id']:42s}  owned×{item['owned_by_users']}"
                f"  ({item.get('display_name')})"
            )
        print()

    # ── Esecuzione: solo se --apply ───────────────────────────────────
    if apply_changes:
        print(" --apply ricevuto: esecuzione live in corso...")
        # NB: in RM1.20-A questo blocco NON va eseguito. Lasciato in piedi
        # per la task successiva. Per sicurezza l'eseguibile lancia un
        # secondo prompt di conferma.
        confirm = os.getenv("ROSTER_APPLY_CONFIRM", "")
        if confirm != "I_UNDERSTAND_THIS_WILL_WRITE_DB":
            print(
                "   ❌ Aborto: variabile d'ambiente ROSTER_APPLY_CONFIRM non "
                "impostata al valore esatto richiesto."
            )
            print(
                "   Per eseguire davvero in futuro:"
                "\n     ROSTER_APPLY_CONFIRM=I_UNDERSTAND_THIS_WILL_WRITE_DB \\"
                "\n     python backend/scripts/plan_legacy_soft_deactivation.py --apply"
            )
            client.close()
            return 2
        # NOTA: blocco di scrittura intenzionalmente non eseguito qui in
        # RM1.20-A. Sarà integrato nella task di import ufficiale del roster.
        print(
            "   ❌ Aborto: in RM1.20-A il path di scrittura è disabilitato "
            "by-design. Nessuna operazione DB eseguita."
        )
        client.close()
        return 3

    # ── Dry-run output JSON ───────────────────────────────────────────
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = REPORTS_DIR / f"legacy_soft_deactivation_plan_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, default=str, ensure_ascii=False)
    print(f" Piano JSON: {out_path}")
    print()
    print(" SAFETY CHECKS (DRY-RUN):")
    for k, v in plan["safety"].items():
        print(f"   • {k:32s} = {v}")
    print()
    print(" Per applicare il piano in FUTURO (non in RM1.20-A):")
    print("   ROSTER_APPLY_CONFIRM=I_UNDERSTAND_THIS_WILL_WRITE_DB \\")
    print("   python backend/scripts/plan_legacy_soft_deactivation.py --apply")
    print()
    print("=" * 78)
    print(" FINE PIANO — NESSUNA scrittura DB. --apply NON eseguito.")
    print("=" * 78)

    client.close()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "RM1.20-A — Genera il piano di soft-deactivation legacy + "
            "canonicalizzazione ufficiali. DRY-RUN by default."
        )
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help=(
            "FUTURO: applica il piano sul DB (richiede anche "
            "ROSTER_APPLY_CONFIRM=I_UNDERSTAND_THIS_WILL_WRITE_DB). "
            "NON eseguire in RM1.20-A."
        ),
    )
    args = ap.parse_args()
    return asyncio.run(run(apply_changes=args.apply))


if __name__ == "__main__":
    sys.exit(main())
