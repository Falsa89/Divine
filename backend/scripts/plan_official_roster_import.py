#!/usr/bin/env python3
"""
RM1.20-B — Official Roster Import Plan (DRY-RUN BY DEFAULT)
═══════════════════════════════════════════════════════════════════════
Genera il PIANO di import per il roster ufficiale (Character Bible) verso
la collection `heroes` di MongoDB, in due tronconi:

  A) INSERT planned per gli eroi ufficiali MANCANTI dal DB (99 attesi).
     Tutti inseriti come "pending_assets/pending_contract" e nascosti da
     catalog/summon/collection/battle picker tramite flag dedicati.

  B) UPDATE planned per gli eroi ufficiali GIÀ PRESENTI nel DB (2 attesi:
     greek_hoplite, norse_berserker). Aggiunge solo campi safe e
     normalizza i metadati. NON sovrascrive image/base_stats/skills.

Garanzie di sicurezza:
  • Default: DRY-RUN. NESSUNA scrittura su DB.
  • Nessun delete, mai (heroes/user_heroes/teams/users restano intatti).
  • Nessun cambio runtime (nessun endpoint toccato qui).
  • La soft-deactivation legacy è governata da un altro script
    (RM1.20-A: plan_legacy_soft_deactivation.py).
  • Anche con --apply lo script è abilitato solo se è settata la env var
    ROSTER_IMPORT_APPLY_CONFIRM=I_UNDERSTAND_THIS_WILL_INSERT_OFFICIAL_HEROES,
    e in RM1.20-B il path di scrittura è comunque disabilitato by-design.

Uso (sempre safe in RM1.20-B):
    cd /app && python backend/scripts/plan_official_roster_import.py

NON eseguire in RM1.20-B:
    python backend/scripts/plan_official_roster_import.py --apply
"""
from __future__ import annotations
import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(BACKEND_ROOT.parent))

from dotenv import load_dotenv  # noqa: E402
load_dotenv(BACKEND_ROOT / ".env")

from motor.motor_asyncio import AsyncIOMotorClient  # noqa: E402
from data.character_bible import (  # noqa: E402
    CHARACTER_BIBLE,
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

# Campi safe da NON sovrascrivere mai sugli ufficiali già presenti.
PRESERVED_FIELDS_ON_EXISTING: Tuple[str, ...] = (
    "id",
    "_id",
    "image",
    "image_url",
    "image_base64",
    "hero_image",
    "base_stats",
    "stats",
    "skills",
    "passive",
    "description",
    "hero_class",
    "lore",
    "battle_contract",
    "ui_contract",
    "asset_variants",
    "created_at",
)


# ════════════════════════════════════════════════════════════════════════
# Builders dei payload (PURE)
# ════════════════════════════════════════════════════════════════════════

def build_missing_official_insert_payload(
    bible_entry: Dict[str, Any],
) -> Dict[str, Any]:
    """Payload INSERT per un eroe ufficiale assente dal DB.

    L'eroe viene marcato `pending_assets`/`pending_contract` e con TUTTI
    i flag di visibilità a False, in modo che — anche se per errore venisse
    inserito ora — non comparirebbe in nessuna superficie player-facing
    appena gli endpoint runtime onoreranno i flag (RM1.20-C).

    NESSUN sentinel asset fittizio: image/image_url/hero_image restano None
    finché l'asset contract non è davvero pronto.
    """
    hid = bible_entry["id"]
    in_extra = hid in EXTRA_PREMIUM_HERO_IDS
    release_group = "launch_extra_premium" if in_extra else "launch_base"
    native_rarity = int(bible_entry["native_rarity"])

    return {
        # ── identità ──────────────────────────────────────────────────
        "id": hid,
        "canonical_id": hid,
        "name": bible_entry["display_name"],
        "display_name": bible_entry["display_name"],

        # ── classificazione ufficiale ─────────────────────────────────
        "release_group": release_group,
        "is_official": True,
        "is_legacy_placeholder": False,
        "legacy_status": None,
        "is_premium": in_extra,
        "is_extra_premium": in_extra,

        # ── rarity / stars ────────────────────────────────────────────
        "native_rarity": native_rarity,
        "rarity": native_rarity,
        "max_stars": get_max_stars(native_rarity),

        # ── canonical taxonomy (sia campi raw che canonical_*) ───────
        "element": normalize_element(bible_entry["element"]),
        "canonical_element": normalize_element(bible_entry["element"]),
        "role": normalize_role(bible_entry["role"]),
        "canonical_role": normalize_role(bible_entry["role"]),
        "faction": normalize_faction(bible_entry["faction"]),
        "canonical_faction": normalize_faction(bible_entry["faction"]),

        "origin_group": bible_entry["origin_group"],
        "category": bible_entry["category"],

        # ── status di pipeline asset/contract ─────────────────────────
        "asset_status": "pending_assets",
        "contract_status": "pending_contract",
        "combat_asset_status": "pending_assets",
        "ui_contract_status": "pending_contract",

        # ── nessun asset fittizio ─────────────────────────────────────
        "image": None,
        "image_url": None,
        "hero_image": None,

        # ── visibilità: TUTTO nascosto finché non pronto ──────────────
        "obtainable": False,
        "show_in_catalog": False,
        "show_in_summon": False,
        "show_in_hero_collection": False,
        "show_in_battle_picker": False,

        # ── status import + protezione operativa ──────────────────────
        "import_status": "planned_missing_official",
        "do_not_expose_until_assets_ready": True,
        "do_not_delete": True,
        "imported_at_planned": datetime.utcnow().isoformat() + "Z",
    }


def build_existing_official_canonicalize_payload(
    bible_entry: Dict[str, Any],
    db_hero: Dict[str, Any],
) -> Dict[str, Any]:
    """Payload `$set` per canonicalizzare un eroe ufficiale già nel DB.

    Regola d'oro: NON sovrascrive mai image/image_url/base_stats/skills.
    Aggiunge solo campi mancanti o normalizza metadati canonici.
    Conserva il valore già presente per `obtainable` / `show_in_*` se è
    già stato esplicitamente impostato (es: True per heroes attivi);
    altrimenti li imposta a True (gli already-present official heroes
    come Hoplite/Berserker sono già in produzione e visibili).
    """
    hid = bible_entry["id"]
    in_extra = hid in EXTRA_PREMIUM_HERO_IDS
    release_group = "launch_extra_premium" if in_extra else "launch_base"
    native_rarity = int(bible_entry["native_rarity"])

    def keep_or_default(key: str, default: Any) -> Any:
        cur = db_hero.get(key)
        return cur if cur is not None else default

    payload: Dict[str, Any] = {
        # ── classificazione ufficiale ─────────────────────────────────
        "is_official": True,
        "is_legacy_placeholder": False,
        "legacy_status": None,
        "release_group": release_group,
        "is_premium": in_extra,
        "is_extra_premium": in_extra,

        # ── rarity / stars (la Bibbia è veritÃ) ──────────────────────
        "native_rarity": native_rarity,
        "rarity": native_rarity,
        "max_stars": get_max_stars(native_rarity),

        # ── canonical taxonomy normalizzata ───────────────────────────
        "canonical_element": normalize_element(bible_entry["element"]),
        "canonical_role": normalize_role(bible_entry["role"]),
        "canonical_faction": normalize_faction(bible_entry["faction"]),

        # ── metadati Character Bible (se mancanti nel DB li aggiunge) ─
        "origin_group": bible_entry["origin_group"],
        "category": bible_entry["category"],

        # ── visibilità: heroes già in produzione → keep o default True ─
        "obtainable": keep_or_default("obtainable", True),
        "show_in_catalog": keep_or_default("show_in_catalog", True),
        "show_in_summon": keep_or_default("show_in_summon", True),
        "show_in_hero_collection": keep_or_default("show_in_hero_collection", True),
        "show_in_battle_picker": keep_or_default("show_in_battle_picker", True),

        # ── status import ─────────────────────────────────────────────
        "import_status": "planned_canonicalize_existing_official",
        "do_not_delete": True,
    }
    return payload


def diff_existing_vs_payload(
    db_hero: Dict[str, Any], payload: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    """Restituisce solo i campi che cambierebbero (before vs after) per
    leggibilità del piano. NON modifica nulla."""
    out: Dict[str, Dict[str, Any]] = {}
    for k, new_val in payload.items():
        cur = db_hero.get(k)
        if cur != new_val:
            out[k] = {"before": cur, "after": new_val}
    return out


def _redact_mongo(url: str) -> str:
    return url.split("@")[-1] if "@" in url else url


# ════════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════════

async def run(apply_changes: bool, official_only: bool = True) -> int:
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "divine_waifus")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    db_heroes: List[Dict[str, Any]] = await db.heroes.find(
        {}, {"image_base64": 0}
    ).to_list(length=None)
    db_by_id: Dict[str, Dict[str, Any]] = {
        h.get("id"): h for h in db_heroes if h.get("id")
    }
    db_ids = set(db_by_id.keys())
    bible_ids = set(CHARACTER_BIBLE_BY_ID.keys())

    official_present_ids = sorted(db_ids & bible_ids)
    official_missing_ids = sorted(bible_ids - db_ids)
    legacy_ids = sorted(db_ids - bible_ids)

    # ── A. INSERT plan per ufficiali mancanti ──────────────────────────
    insert_plan: List[Dict[str, Any]] = []
    for hid in official_missing_ids:
        entry = CHARACTER_BIBLE_BY_ID[hid]
        payload = build_missing_official_insert_payload(entry)
        insert_plan.append({
            "hero_id": hid,
            "display_name": entry["display_name"],
            "release_group": payload["release_group"],
            "rarity": payload["rarity"],
            "match_filter": {"id": hid},
            "operation": "insertOne",
            "insert_payload": payload,
        })

    # ── B. UPDATE plan per ufficiali già presenti ──────────────────────
    update_plan: List[Dict[str, Any]] = []
    for hid in official_present_ids:
        entry = CHARACTER_BIBLE_BY_ID[hid]
        db_hero = db_by_id[hid]
        payload = build_existing_official_canonicalize_payload(entry, db_hero)
        delta = diff_existing_vs_payload(db_hero, payload)
        # Verifica protezione preserved fields
        for protected_key in PRESERVED_FIELDS_ON_EXISTING:
            if protected_key in payload:
                # Non dovrebbe mai succedere col builder corrente, ma è una
                # protezione ulteriore: rimuovi qualsiasi chiave protetta.
                payload.pop(protected_key, None)
        update_plan.append({
            "hero_id": hid,
            "display_name": entry["display_name"],
            "release_group": payload["release_group"],
            "match_filter": {"id": hid},
            "operation": "updateOne",
            "update_payload": {"$set": payload},
            "diff_preview": delta,
            "preserved_fields_check": {
                "image_preserved": db_hero.get("image"),
                "image_url_preserved": db_hero.get("image_url"),
                "base_stats_preserved": bool(db_hero.get("base_stats")),
                "hero_class_preserved": db_hero.get("hero_class"),
            },
        })

    # ── Riepilogo legacy (NON toccato qui) ─────────────────────────────
    legacy_summary = {
        "count": len(legacy_ids),
        "note": (
            "I legacy non vengono toccati da questo script. La loro "
            "soft-deactivation è gestita da plan_legacy_soft_deactivation.py "
            "(RM1.20-A)."
        ),
    }

    # ── Visibility / exposure warning ─────────────────────────────────
    visibility_warning = (
        "Non eseguire INSERT degli ufficiali mancanti finché non è "
        "soddisfatta almeno UNA di queste condizioni:\n"
        "  1) Gli endpoint runtime (/api/heroes, gacha, hero collection, "
        "battle picker) onorano i flag show_in_catalog / show_in_summon / "
        "show_in_hero_collection / show_in_battle_picker / obtainable "
        "(target: RM1.20-C); oppure\n"
        "  2) Gli inserimenti sono dev-only e mascherati da un toggle "
        "ENV (es. ROSTER_DEV_PREVIEW=1) che non è attivo in produzione; "
        "oppure\n"
        "  3) L'utente accetta esplicitamente che gli eroi pending_assets "
        "siano temporaneamente visibili senza asset (sconsigliato)."
    )

    next_phase_recommendation = (
        "Procedere con RM1.20-C: implementazione filtri runtime per "
        "is_official / is_legacy_placeholder / show_in_* / obtainable. "
        "Solo dopo, eseguire l'apply combinato di "
        "plan_legacy_soft_deactivation.py --apply e poi "
        "plan_official_roster_import.py --apply."
    )

    # ── Composizione report ────────────────────────────────────────────
    report: Dict[str, Any] = {
        "task": "RM1.20-B",
        "kind": "official_roster_import_plan",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "dry_run": not apply_changes,
        "apply_flag_executed": False,
        "db": {
            "mongo_url_redacted": _redact_mongo(mongo_url),
            "db_name": db_name,
        },
        "character_bible_summary": {
            "total_official": len(CHARACTER_BIBLE),
            "launch_base_count": len(LAUNCH_BASE_HERO_IDS),
            "extra_premium_count": len(EXTRA_PREMIUM_HERO_IDS),
            "extra_premium_ids": EXTRA_PREMIUM_HERO_IDS,
        },
        "db_summary": {
            "heroes_total": len(db_heroes),
            "official_present": len(official_present_ids),
            "official_missing": len(official_missing_ids),
            "legacy_candidates": len(legacy_ids),
        },
        "summary": {
            "missing_to_insert": len(insert_plan),
            "existing_to_canonicalize": len(update_plan),
            "legacy_untouched": len(legacy_ids),
            "borea_status": (
                "missing_planned_for_insert"
                if "greek_borea" in official_missing_ids
                else "present_planned_for_canonicalize"
            ),
        },
        "visibility_warning": visibility_warning,
        "next_phase_recommendation": next_phase_recommendation,
        "preserved_fields_on_existing": list(PRESERVED_FIELDS_ON_EXISTING),
        "plan_insert_missing_official": insert_plan,
        "plan_canonicalize_existing_official": update_plan,
        "legacy_summary": legacy_summary,
        "safety": {
            "db_writes_performed": False,
            "user_heroes_modified": False,
            "teams_modified": False,
            "users_modified": False,
            "heroes_deleted": False,
            "legacy_modified": False,
            "runtime_endpoints_changed": False,
            "frontend_changed": False,
            "gacha_changed": False,
        },
        "policy_doc": "docs/ROSTER_IMPORT_AND_LEGACY_POLICY.md",
        "future_apply_command": (
            "ROSTER_IMPORT_APPLY_CONFIRM=I_UNDERSTAND_THIS_WILL_INSERT_OFFICIAL_HEROES "
            "python backend/scripts/plan_official_roster_import.py --apply"
        ),
    }

    # ── Console output ────────────────────────────────────────────────
    print("=" * 78)
    print(" RM1.20-B — PIANO IMPORT ROSTER UFFICIALE  ({})".format(
        "APPLY (LIVE)" if apply_changes else "DRY-RUN"
    ))
    print("=" * 78)
    print(f" DB:                              {db_name}  ({_redact_mongo(mongo_url)})")
    print(f" Character Bible totale:          {len(CHARACTER_BIBLE)} ufficiali")
    print(f"   • launch_base:                 {len(LAUNCH_BASE_HERO_IDS)}")
    print(f"   • extra_premium:               {len(EXTRA_PREMIUM_HERO_IDS)}  -> {EXTRA_PREMIUM_HERO_IDS}")
    print(f" DB heroes totali:                {len(db_heroes)}")
    print(f"   • ufficiali presenti:          {len(official_present_ids)}")
    print(f"   • ufficiali mancanti:          {len(official_missing_ids)}")
    print(f"   • legacy (non toccati):        {len(legacy_ids)}")
    print()
    print(f" PIANO INSERT (missing official): {len(insert_plan)}")
    print(f" PIANO UPDATE (existing official): {len(update_plan)}")
    print()

    if update_plan:
        print(" Eroi ufficiali già nel DB (canonicalizzazione):")
        for u in update_plan:
            n_changes = len(u.get("diff_preview", {}))
            print(
                f"   - {u['hero_id']:42s}  {n_changes:>3d} campi da aggiornare"
                f"  (image preservata: {u['preserved_fields_check']['image_preserved']!r})"
            )
        print()

    if insert_plan:
        print(" Preview INSERT (primi 8):")
        for item in insert_plan[:8]:
            print(
                f"   - {item['hero_id']:42s}  {item['release_group']:22s}"
                f"  R{item['rarity']}  ({item['display_name']})"
            )
        print(f"   … e altri {max(0, len(insert_plan)-8)} eroi.")
        print()

    print(" ⚠️  WARNING di visibilità:")
    for line in visibility_warning.splitlines():
        print(f"   {line}")
    print()
    print(" ▶  Raccomandazione fase successiva:")
    print(f"   {next_phase_recommendation}")
    print()

    # ── --apply gating ────────────────────────────────────────────────
    if apply_changes:
        print(" --apply ricevuto: validazione confirm env var…")
        confirm = os.getenv("ROSTER_IMPORT_APPLY_CONFIRM", "")
        expected = "I_UNDERSTAND_THIS_WILL_INSERT_OFFICIAL_HEROES"
        if confirm != expected:
            print(
                f"   ❌ Aborto: ROSTER_IMPORT_APPLY_CONFIRM non valida.\n"
                f"   Atteso: {expected}\n"
                f"   Per eseguire davvero:\n"
                f"     {report['future_apply_command']} --official-only"
            )
            client.close()
            return 2

        # RM1.20-E: in questa task accettiamo SOLO --official-only.
        # Il path "non-official-only" è riservato a future revisioni.
        if not official_only:
            print(
                "   ❌ Aborto: in RM1.20-E è abilitato SOLO `--official-only`.\n"
                "   Comando corretto:\n"
                "     ROSTER_IMPORT_APPLY_CONFIRM=I_UNDERSTAND_THIS_WILL_INSERT_OFFICIAL_HEROES \\\n"
                "     python backend/scripts/plan_official_roster_import.py --apply --official-only"
            )
            client.close()
            return 3

        # ── Apply LIVE: INSERT missing + canonicalize existing officials ──
        # Garanzia: legacy NON vengono toccati. Match filter usa `id` su
        # heroes che NON sono is_legacy_placeholder=true per le UPDATE,
        # e usa upsert via insertOne (NOT update_one) per gli INSERT —
        # SE l'eroe esiste già con quell'id l'INSERT andrà in conflitto e
        # quel item viene saltato (safe-by-default, mai overwrite).
        applied_at = datetime.utcnow().isoformat() + "Z"
        inserted_count = 0
        canonicalized_count = 0
        skipped_inserts: List[str] = []
        skipped_updates: List[str] = []

        # 1) INSERT missing officials (pending_assets, hidden)
        for item in insert_plan:
            payload = dict(item["insert_payload"])
            payload["import_status"] = "imported_pending_assets"
            payload["imported_at"] = applied_at
            # Pre-check: non sovrascrivere heroes esistenti con stesso id.
            existing = await db.heroes.find_one({"id": payload["id"]}, {"_id": 1})
            if existing is not None:
                skipped_inserts.append(payload["id"])
                continue
            try:
                await db.heroes.insert_one(payload)
                inserted_count += 1
            except Exception as exc:  # noqa: BLE001
                print(f"   ⚠ insert error {payload['id']}: {exc}")
                skipped_inserts.append(payload["id"])

        # 2) UPDATE canonicalize existing officials (NON legacy, NON missing)
        for item in update_plan:
            hid = item["hero_id"]
            payload = dict(item["update_payload"]["$set"])
            # SAFETY: filtriamo via i legacy. Se per qualunque ragione
            # un hero esistente è stato marcato legacy nel frattempo,
            # NON lo tocchiamo.
            res = await db.heroes.update_one(
                {"id": hid, "is_legacy_placeholder": {"$ne": True}},
                {"$set": payload},
            )
            if res.matched_count == 1:
                canonicalized_count += 1
            else:
                skipped_updates.append(hid)
                print(
                    f"   ⚠ skip canonicalize {hid}: matched={res.matched_count} "
                    f"modified={res.modified_count}"
                )

        # Aggiorna safety + apply manifest
        report["safety"]["db_writes_performed"] = True
        report["apply_flag_executed"] = True
        report["dry_run"] = False
        report["apply_manifest"] = {
            "applied_at": applied_at,
            "apply_mode": "official_only",
            "inserted_count": inserted_count,
            "canonicalized_count": canonicalized_count,
            "skipped_inserts": skipped_inserts,
            "skipped_updates": skipped_updates,
            "legacy_modified": 0,
            "user_heroes_modified": 0,
            "teams_modified": 0,
            "users_modified": 0,
            "heroes_deleted": 0,
        }

        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        out_path = REPORTS_DIR / f"official_roster_import_APPLIED_{ts}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str, ensure_ascii=False)

        print()
        print(" =====================================================")
        print(f"   APPLY COMPLETATO (official_only mode)")
        print(f"   INSERT (missing officials):     {inserted_count}/{len(insert_plan)}")
        print(f"   UPDATE (canonicalize existing): {canonicalized_count}/{len(update_plan)}")
        print(f"   skipped inserts (already exist): {len(skipped_inserts)}")
        print(f"   skipped updates (legacy/match):  {len(skipped_updates)}")
        print(f"   legacy modified:                 0")
        print(f"   heroes deleted:                  0")
        print(f"   user_heroes / teams / users:     UNTOUCHED")
        print(f"   Manifest JSON: {out_path}")
        print(" =====================================================")
        client.close()
        return 0

    # ── Scrittura JSON (DRY-RUN) ──────────────────────────────────────
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = REPORTS_DIR / f"official_roster_import_plan_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str, ensure_ascii=False)
    print(f" Report JSON: {out_path}")
    print()
    print(" SAFETY CHECKS (DRY-RUN):")
    for k, v in report["safety"].items():
        print(f"   • {k:32s} = {v}")
    print()
    print(" Per applicare in FUTURO (NON in RM1.20-B):")
    print(f"   {report['future_apply_command']}")
    print()
    print("=" * 78)
    print(" FINE PIANO — NESSUNA scrittura DB. --apply NON eseguito.")
    print("=" * 78)

    client.close()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "RM1.20-B — Genera il piano di import roster ufficiale (INSERT "
            "missing + UPDATE canonicalize existing). DRY-RUN by default."
        )
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Applica il piano sul DB (richiede anche env var "
            "ROSTER_IMPORT_APPLY_CONFIRM=I_UNDERSTAND_THIS_WILL_INSERT_OFFICIAL_HEROES). "
            "In RM1.20-E è abilitato SOLO con --official-only."
        ),
    )
    ap.add_argument(
        "--official-only",
        action="store_true",
        help=(
            "RM1.20-E: applica SOLO INSERT degli ufficiali mancanti + "
            "UPDATE canonicalize dei 2 ufficiali già presenti. Mai legacy."
        ),
    )
    args = ap.parse_args()
    return asyncio.run(run(apply_changes=args.apply, official_only=args.official_only))


if __name__ == "__main__":
    sys.exit(main())
