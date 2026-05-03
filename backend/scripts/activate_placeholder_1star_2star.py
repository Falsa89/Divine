#!/usr/bin/env python3
"""
RM1.22-F — Controlled Activation of Official 1★/2★ Placeholder Heroes
═══════════════════════════════════════════════════════════════════════

Attiva ESCLUSIVAMENTE i 20 eroi ufficiali 1★/2★ già wired in RM1.22-D
(asset placeholder + contratti placeholder_dev) impostando i flag DB di
visibilità e obtainability senza mai marcarli come `approved_final`.

DEFAULT: dry-run (read-only).
APPLY  : richiede env-var
        PLACEHOLDER_ACTIVATION_CONFIRM=I_UNDERSTAND_THIS_WILL_ACTIVATE_PLACEHOLDER_HEROES
        e flag --apply.

Uso:
    # Dry-run
    python backend/scripts/activate_placeholder_1star_2star.py

    # Apply REALE (richiede env-var)
    PLACEHOLDER_ACTIVATION_CONFIRM=I_UNDERSTAND_THIS_WILL_ACTIVATE_PLACEHOLDER_HEROES \\
      python backend/scripts/activate_placeholder_1star_2star.py --apply

Vincoli non negoziabili (verificati da audit + filtri update_one):
  • Modifica SOLO i 20 hero_id target.
  • NON cambia is_official, is_legacy_placeholder, native_rarity, rarity,
    image / image_url / hero_image, gacha rates, kit JSON, asset files.
  • NON elimina nulla.
  • Marca contract_status = "placeholder_contract_ready" e asset_status
    = "placeholder_dev" — NON "approved_final".
"""
from __future__ import annotations
import argparse
import asyncio
import json
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

# ════════════════════════════════════════════════════════════════════════
# Source of truth: data/design/placeholder_assignment_1star_2star_manifest.json
# Per safety, validiamo che il manifest combaci con questa lista hardcoded.
# ════════════════════════════════════════════════════════════════════════
TARGET_HERO_IDS = [
    # 1★ (8)
    "greek_phalanx_recruit",
    "demonic_infernal_handmaiden",
    "egyptian_nile_guard",
    "celtic_forest_archer",
    "norse_rune_initiate",
    "angelic_sanctuary_acolyte",
    "angelic_sacred_novice",
    "yokai_veiled_spirit",
    # 2★ (12)
    "egyptian_temple_guardian",
    "norse_valhalla_warden",
    "egyptian_desert_blade",
    "celtic_menhir_warrior",
    "egyptian_oasis_markswoman",
    "yokai_huntress",
    "yokai_thunder_novice",
    "yokai_shinobi_shadow",
    "angelic_cantor",
    "egyptian_nile_healer",
    "cursed_bone_sibyl",
    "demonic_infernal_adept",
]

ACTIVATION_BATCH = "RM1.22-F_1star_2star_placeholder_activation"
ENV_CONFIRM_KEY = "PLACEHOLDER_ACTIVATION_CONFIRM"
ENV_CONFIRM_VAL = "I_UNDERSTAND_THIS_WILL_ACTIVATE_PLACEHOLDER_HEROES"

REQUIRED_RUNTIME_FILES = [
    "idle_sheet.png",
    "attack_sheet.png",
    "skill_sheet.png",
    "hit_sheet.png",
    "death_sheet.png",
    "battle_animations.json",
]


# ════════════════════════════════════════════════════════════════════════
# Pre-apply audit (read-only)
# ════════════════════════════════════════════════════════════════════════
async def audit(db) -> dict:
    """Read-only audit. Ritorna dict con findings. Non muta nulla."""
    findings: dict = {
        "target_count": len(TARGET_HERO_IDS),
        "missing_db_records": [],
        "unexpected_status": [],
        "missing_asset_dirs": [],
        "missing_placeholder_status": [],
        "bad_placeholder_status": [],
        "missing_runtime_files": [],
        "manifest_match": None,
    }

    # 1. Manifest cross-check
    manifest_path = APP_ROOT / "data" / "design" / "placeholder_assignment_1star_2star_manifest.json"
    if manifest_path.is_file():
        try:
            mf = json.loads(manifest_path.read_text())
            mf_ids = set()
            # Cerca id degli eroi nel manifest indipendentemente dalla shape
            for key in ("targets", "heroes", "assignments", "hero_ids", "items"):
                v = mf.get(key)
                if isinstance(v, list):
                    for entry in v:
                        if isinstance(entry, dict):
                            hid = entry.get("hero_id") or entry.get("id")
                            if hid:
                                mf_ids.add(hid)
                        elif isinstance(entry, str):
                            mf_ids.add(entry)
            findings["manifest_match"] = (mf_ids == set(TARGET_HERO_IDS))
            findings["manifest_target_ids"] = sorted(mf_ids)
        except Exception as e:
            findings["manifest_match"] = False
            findings["manifest_error"] = str(e)
    else:
        findings["manifest_match"] = False
        findings["manifest_error"] = f"manifest not found at {manifest_path}"

    # 2. DB records audit
    found = await db.heroes.find(
        {"id": {"$in": TARGET_HERO_IDS}},
        {"image_base64": 0},
    ).to_list(None)
    found_ids = {h["id"] for h in found}
    findings["missing_db_records"] = sorted(set(TARGET_HERO_IDS) - found_ids)
    findings["db_records_found"] = len(found)

    # 3. DB status audit (campo per campo)
    expected_pre = {
        "is_official": True,
        "is_legacy_placeholder": False,
        "asset_status": "pending_assets",
        "obtainable": False,
        "show_in_catalog": False,
        "show_in_summon": False,
        "show_in_hero_collection": False,
        "show_in_battle_picker": False,
    }
    for h in found:
        bad = []
        for k, v in expected_pre.items():
            actual = h.get(k)
            if actual != v:
                bad.append(f"{k}={actual!r} (expected {v!r})")
        nr = h.get("native_rarity")
        if nr not in (1, 2):
            bad.append(f"native_rarity={nr!r} (expected 1 or 2)")
        if bad:
            findings["unexpected_status"].append({"id": h["id"], "issues": bad})

    # 4. Asset folder audit
    for hid in TARGET_HERO_IDS:
        base = APP_ROOT / "frontend" / "assets" / "heroes" / hid
        if not base.is_dir():
            findings["missing_asset_dirs"].append(hid)
            continue
        ps = base / "placeholder_status.json"
        if not ps.is_file():
            findings["missing_placeholder_status"].append(hid)
        else:
            try:
                data = json.loads(ps.read_text())
                bad = {}
                if data.get("asset_status") != "placeholder_dev":
                    bad["asset_status"] = data.get("asset_status")
                if data.get("final_art_ready") is not False:
                    bad["final_art_ready"] = data.get("final_art_ready")
                if data.get("assigned_by") != "RM1.22-C":
                    bad["assigned_by"] = data.get("assigned_by")
                if bad:
                    findings["bad_placeholder_status"].append({"id": hid, "bad_fields": bad})
            except Exception as e:
                findings["bad_placeholder_status"].append({"id": hid, "parse_error": str(e)})
        rt = base / "runtime"
        for rf in REQUIRED_RUNTIME_FILES:
            if not (rt / rf).is_file():
                findings["missing_runtime_files"].append(f"{hid}/runtime/{rf}")

    return findings


def audit_passed(f: dict) -> bool:
    return (
        f.get("manifest_match") is True
        and not f["missing_db_records"]
        and not f["unexpected_status"]
        and not f["missing_asset_dirs"]
        and not f["missing_placeholder_status"]
        and not f["bad_placeholder_status"]
        and not f["missing_runtime_files"]
        and f.get("db_records_found") == len(TARGET_HERO_IDS)
    )


def print_audit(f: dict) -> None:
    print("=" * 78)
    print(" RM1.22-F — PRE-APPLY AUDIT")
    print("=" * 78)
    print(f"  target heroes count        : {f['target_count']}")
    print(f"  manifest cross-check       : {'OK' if f.get('manifest_match') else 'FAIL'}")
    print(f"  DB records found           : {f['db_records_found']}/{f['target_count']}")
    print(f"  missing DB records         : {len(f['missing_db_records'])}")
    if f["missing_db_records"]:
        for x in f["missing_db_records"]:
            print(f"      - {x}")
    print(f"  unexpected DB status       : {len(f['unexpected_status'])}")
    for x in f["unexpected_status"]:
        print(f"      - {x['id']}: {x['issues']}")
    print(f"  missing asset folders      : {len(f['missing_asset_dirs'])}")
    for x in f["missing_asset_dirs"]:
        print(f"      - {x}")
    print(f"  missing placeholder_status : {len(f['missing_placeholder_status'])}")
    for x in f["missing_placeholder_status"]:
        print(f"      - {x}")
    print(f"  bad placeholder_status     : {len(f['bad_placeholder_status'])}")
    for x in f["bad_placeholder_status"]:
        print(f"      - {x}")
    print(f"  missing runtime files      : {len(f['missing_runtime_files'])}")
    for x in f["missing_runtime_files"][:8]:
        print(f"      - {x}")
    if len(f["missing_runtime_files"]) > 8:
        print(f"      ... and {len(f['missing_runtime_files']) - 8} more")
    print("=" * 78)
    print(f"  RESULT: {'✓ PASS' if audit_passed(f) else '❌ FAIL — STOP'}")
    print("=" * 78)


# ════════════════════════════════════════════════════════════════════════
# Apply
# ════════════════════════════════════════════════════════════════════════
async def apply_activation(db, dry_run: bool) -> dict:
    """
    Esegue update_many filtrato. Se dry_run, calcola solo cosa
    verrebbe modificato senza scrivere. Ritorna report.
    """
    now_iso = datetime.utcnow().isoformat() + "Z"
    update_doc = {
        "$set": {
            "asset_status": "placeholder_dev",
            "contract_status": "placeholder_contract_ready",
            "combat_asset_status": "placeholder_dev",
            "ui_contract_status": "placeholder_contract_ready",
            "do_not_expose_until_assets_ready": False,

            "obtainable": True,
            "show_in_catalog": True,
            "show_in_summon": True,
            "show_in_hero_collection": True,
            "show_in_battle_picker": True,

            "activation_status": "active_with_placeholder_assets",
            "activated_at": now_iso,
            "activation_batch": ACTIVATION_BATCH,
            "final_art_ready": False,
        },
    }
    # FILTRO STRETTO: ID nella lista AND ufficiale AND non-legacy AND
    # rarity 1 o 2 AND non già final art. Difesa in profondità.
    flt = {
        "id": {"$in": TARGET_HERO_IDS},
        "is_official": True,
        "is_legacy_placeholder": False,
        "native_rarity": {"$in": [1, 2]},
        "asset_status": {"$ne": "approved_final"},
    }

    # Snapshot pre-update fields per i 20 target (per report)
    pre = await db.heroes.find(
        {"id": {"$in": TARGET_HERO_IDS}},
        {
            "id": 1, "name": 1, "native_rarity": 1, "asset_status": 1,
            "obtainable": 1, "show_in_catalog": 1, "show_in_summon": 1,
            "show_in_hero_collection": 1, "show_in_battle_picker": 1,
            "activation_status": 1, "contract_status": 1,
        },
    ).to_list(None)

    matched = await db.heroes.count_documents(flt)

    if dry_run:
        return {
            "dry_run": True,
            "filter": flt,
            "update": update_doc,
            "would_match": matched,
            "pre_state_sample": pre[:3],
        }

    # APPLY
    res = await db.heroes.update_many(flt, update_doc)

    post = await db.heroes.find(
        {"id": {"$in": TARGET_HERO_IDS}},
        {
            "id": 1, "name": 1, "native_rarity": 1, "asset_status": 1,
            "obtainable": 1, "show_in_catalog": 1, "show_in_summon": 1,
            "show_in_hero_collection": 1, "show_in_battle_picker": 1,
            "activation_status": 1, "contract_status": 1,
        },
    ).to_list(None)

    return {
        "dry_run": False,
        "matched_count": res.matched_count,
        "modified_count": res.modified_count,
        "pre_state_sample": pre[:3],
        "post_state_sample": post[:3],
    }


# ════════════════════════════════════════════════════════════════════════
# Smoke checks (read-only, NO live gacha pulls, NO live registration)
# ════════════════════════════════════════════════════════════════════════
async def smoke_visibility(db) -> dict:
    """Conta heroes visibili / summon eligible / starter eligible. NO writes."""
    sys.path.insert(0, str(BACKEND_ROOT))
    from utils.hero_visibility import (
        should_show_in_catalog,
        should_show_in_summon,
    )

    all_heroes = await db.heroes.find({}, {"image_base64": 0}).to_list(None)

    show_catalog = [h for h in all_heroes if should_show_in_catalog(h, owned=False)]
    summon_eligible = [h for h in all_heroes if should_show_in_summon(h)]
    starter_eligible = [h for h in summon_eligible if (h.get("native_rarity") or h.get("rarity") or 99) <= 2]

    legacy_summon = [h for h in summon_eligible if h.get("is_legacy_placeholder")]
    pending_3plus_visible = [
        h for h in all_heroes
        if h.get("asset_status") == "pending_assets"
        and (h.get("show_in_catalog") or h.get("show_in_summon"))
    ]
    activated_targets = await db.heroes.count_documents({
        "id": {"$in": TARGET_HERO_IDS},
        "activation_status": "active_with_placeholder_assets",
    })

    by_rarity_summon = {}
    for h in summon_eligible:
        r = h.get("native_rarity") or h.get("rarity") or 0
        by_rarity_summon[r] = by_rarity_summon.get(r, 0) + 1

    return {
        "total_heroes": len(all_heroes),
        "show_in_catalog": len(show_catalog),
        "summon_eligible": len(summon_eligible),
        "summon_eligible_by_rarity": dict(sorted(by_rarity_summon.items())),
        "starter_eligible": len(starter_eligible),
        "legacy_summon_eligible": len(legacy_summon),
        "pending_3plus_visible": len(pending_3plus_visible),
        "activated_placeholder_1star_2star": activated_targets,
    }


# ════════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════════
async def main() -> int:
    ap = argparse.ArgumentParser(description="RM1.22-F — Activate 1★/2★ placeholder heroes")
    ap.add_argument("--apply", action="store_true",
                    help=f"Esegue il write reale. Richiede {ENV_CONFIRM_KEY}={ENV_CONFIRM_VAL}.")
    args = ap.parse_args()

    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "divine_waifus")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    # 1. Audit
    findings = await audit(db)
    print_audit(findings)

    if not audit_passed(findings):
        print("\n❌ AUDIT FAIL — non procedo. Risolvi i findings sopra.")
        client.close()
        return 1

    # 2. Smoke pre
    print("\n" + "=" * 78)
    print(" SMOKE PRE-APPLY (read-only)")
    print("=" * 78)
    pre = await smoke_visibility(db)
    for k, v in pre.items():
        print(f"  {k:36s} = {v}")
    print("=" * 78)

    # 3. Decide dry-run vs apply
    if not args.apply:
        print("\n[DRY-RUN] modalità di default. Per scrivere usa --apply con env-var.")
        result = await apply_activation(db, dry_run=True)
        print(f"\n  matched_count (would update): {result['would_match']}")
        client.close()
        return 0

    confirm = os.getenv(ENV_CONFIRM_KEY)
    if confirm != ENV_CONFIRM_VAL:
        print(f"\n❌ ABORT: {ENV_CONFIRM_KEY} non impostato correttamente.")
        print(f"   Atteso: {ENV_CONFIRM_VAL}")
        print(f"   Trovato: {confirm!r}")
        client.close()
        return 2

    # 4. Apply
    print("\n" + "=" * 78)
    print(" APPLY")
    print("=" * 78)
    result = await apply_activation(db, dry_run=False)
    print(f"  matched  : {result['matched_count']}")
    print(f"  modified : {result['modified_count']}")
    print("=" * 78)

    # 5. Smoke post
    print("\n" + "=" * 78)
    print(" SMOKE POST-APPLY (read-only)")
    print("=" * 78)
    post = await smoke_visibility(db)
    for k, v in post.items():
        print(f"  {k:36s} = {v}")
    print("=" * 78)

    # 6. Persist report
    report_dir = BACKEND_ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    report_path = report_dir / f"placeholder_activation_1star_2star_APPLIED_{ts}.json"
    payload = {
        "task": "RM1.22-F",
        "applied_at": datetime.utcnow().isoformat() + "Z",
        "activation_batch": ACTIVATION_BATCH,
        "target_hero_ids": TARGET_HERO_IDS,
        "matched_count": result["matched_count"],
        "modified_count": result["modified_count"],
        "smoke_pre": pre,
        "smoke_post": post,
    }
    report_path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"  report : {report_path}")

    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
