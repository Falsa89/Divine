#!/usr/bin/env python3
"""
RM1.22-K — Controlled Activation of Official 5★ Placeholder Heroes
═══════════════════════════════════════════════════════════════════════

Attiva ESCLUSIVAMENTE i 20 eroi ufficiali 5★ pending (RM1.22-G-BULK
placeholder assets + RM1.22-G-BULK frontend contracts), impostando i
flag DB di visibilità e obtainability senza mai marcarli come
`approved_final`. Esclude Hoplite/Berserker/1★/2★/3★/4★ già attivi e
greek_borea (rimane pending premium).

DEFAULT: dry-run (read-only).
APPLY  : richiede env-var
        PLACEHOLDER_5STAR_ACTIVATION_CONFIRM=
          I_UNDERSTAND_THIS_WILL_ACTIVATE_5STAR_PLACEHOLDER_HEROES
        e flag --apply.

Uso:
    # Dry-run
    python backend/scripts/activate_placeholder_5star.py

    # Apply REALE
    PLACEHOLDER_5STAR_ACTIVATION_CONFIRM=I_UNDERSTAND_THIS_WILL_ACTIVATE_5STAR_PLACEHOLDER_HEROES \\
      python backend/scripts/activate_placeholder_5star.py --apply
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

# ═══════════════════════════════════════════════════════════════════════
# 20 official 5★ targets (source of truth:
# data/design/placeholder_assignment_remaining_manifest.json,
# filter native_rarity == 5).
# ═══════════════════════════════════════════════════════════════════════
TARGET_HERO_IDS = [
    "greek_nemean_lioness",
    "norse_rime_jotunn",
    "angelic_bastion_angel",
    "norse_dawn_valkyrie",
    "egyptian_claw_of_sekhmet",
    "greek_atalanta",
    "greek_circe",
    "japanese_miko_of_raijin",
    "demonic_gehenna_witch",
    "egyptian_bastet",
    "yokai_oni_kunoichi",
    "greek_nike",
    "norse_volva_of_fate",
    "norse_eir",
    "greek_medusa",
    "celtic_mist_banshee",
    "yokai_yuki_onna",
    "creature_crimson_phoenix",
    "creature_lernaean_hydra",
    "cursed_pestilence_herald",
]

ACTIVATION_BATCH = "RM1.22-K_5star_placeholder_activation"
ENV_CONFIRM_KEY = "PLACEHOLDER_5STAR_ACTIVATION_CONFIRM"
ENV_CONFIRM_VAL = "I_UNDERSTAND_THIS_WILL_ACTIVATE_5STAR_PLACEHOLDER_HEROES"
TARGET_NATIVE_RARITY = 5

REQUIRED_RUNTIME_FILES = [
    "idle_sheet.png", "attack_sheet.png", "skill_sheet.png",
    "hit_sheet.png", "death_sheet.png", "battle_animations.json",
]

# ID esclusi: non devono mai essere toccati da questo script.
PROTECTED_IDS = {"greek_hoplite", "norse_berserker", "greek_borea"}


async def audit(db) -> dict:
    """Read-only audit. Ritorna dict con findings."""
    f: dict = {
        "target_count": len(TARGET_HERO_IDS),
        "missing_db_records": [],
        "unexpected_status": [],
        "missing_asset_dirs": [],
        "missing_placeholder_status": [],
        "bad_placeholder_status": [],
        "missing_runtime_files": [],
        "missing_frontend_contracts": [],
        "missing_qa_lab_options": [],
        "manifest_match": None,
        "target_intersects_protected": [],
    }

    # Sanity: targets non devono intersecare i protected
    inter = set(TARGET_HERO_IDS) & PROTECTED_IDS
    f["target_intersects_protected"] = sorted(inter)

    # Manifest cross-check
    manifest_path = APP_ROOT / "data" / "design" / "placeholder_assignment_remaining_manifest.json"
    try:
        mf = json.loads(manifest_path.read_text())
        manifest_set = {t["hero_id"] for t in mf["targets"] if t.get("native_rarity") == TARGET_NATIVE_RARITY}
        f["manifest_match"] = (manifest_set == set(TARGET_HERO_IDS))
        f["manifest_target_rarity_count"] = len(manifest_set)
    except Exception as e:
        f["manifest_match"] = False
        f["manifest_error"] = str(e)

    # DB records
    found = await db.heroes.find(
        {"id": {"$in": TARGET_HERO_IDS}},
        {"image_base64": 0},
    ).to_list(None)
    found_ids = {h["id"] for h in found}
    f["missing_db_records"] = sorted(set(TARGET_HERO_IDS) - found_ids)
    f["db_records_found"] = len(found)

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
            if h.get(k) != v:
                bad.append(f"{k}={h.get(k)!r} (expected {v!r})")
        if h.get("native_rarity") != TARGET_NATIVE_RARITY:
            bad.append(f"native_rarity={h.get('native_rarity')!r} (expected {TARGET_NATIVE_RARITY})")
        if bad:
            f["unexpected_status"].append({"id": h["id"], "issues": bad})

    # Filesystem
    for hid in TARGET_HERO_IDS:
        base = APP_ROOT / "frontend" / "assets" / "heroes" / hid
        if not base.is_dir():
            f["missing_asset_dirs"].append(hid)
            continue
        ps = base / "placeholder_status.json"
        if not ps.is_file():
            f["missing_placeholder_status"].append(hid)
        else:
            try:
                data = json.loads(ps.read_text())
                bad = {}
                if data.get("asset_status") != "placeholder_dev":
                    bad["asset_status"] = data.get("asset_status")
                if data.get("final_art_ready") is not False:
                    bad["final_art_ready"] = data.get("final_art_ready")
                if data.get("assigned_by") != "RM1.22-G-BULK":
                    bad["assigned_by"] = data.get("assigned_by")
                if bad:
                    f["bad_placeholder_status"].append({"id": hid, "bad_fields": bad})
            except Exception as e:
                f["bad_placeholder_status"].append({"id": hid, "parse_error": str(e)})
        rt = base / "runtime"
        for rf in REQUIRED_RUNTIME_FILES:
            if not (rt / rf).is_file():
                f["missing_runtime_files"].append(f"{hid}/runtime/{rf}")

    # Frontend contract + Lab option coverage
    import re
    fe_src = (APP_ROOT / "frontend" / "components" / "ui" /
              "placeholderHeroContractsRemaining.ts").read_text()
    m_con = re.search(
        r'export const PLACEHOLDER_HERO_CONTRACTS_REMAINING[^{]*\{(.+?)\n\};',
        fe_src, re.DOTALL,
    )
    con_ids = set(re.findall(
        r'^\s{2}"([a-z_]+)":\s*\{', m_con.group(1), re.MULTILINE,
    )) if m_con else set()
    m_lab = re.search(
        r'export const PLACEHOLDER_LAB_HERO_OPTIONS_REMAINING[^[]*\[(.+?)\n\];',
        fe_src, re.DOTALL,
    )
    lab_ids = set(re.findall(r'id:\s*"([a-z_]+)"', m_lab.group(1))) if m_lab else set()
    f["missing_frontend_contracts"] = sorted(set(TARGET_HERO_IDS) - con_ids)
    f["missing_qa_lab_options"] = sorted(set(TARGET_HERO_IDS) - lab_ids)

    return f


def audit_passed(f: dict) -> bool:
    return (
        f.get("manifest_match") is True
        and not f["target_intersects_protected"]
        and not f["missing_db_records"]
        and not f["unexpected_status"]
        and not f["missing_asset_dirs"]
        and not f["missing_placeholder_status"]
        and not f["bad_placeholder_status"]
        and not f["missing_runtime_files"]
        and not f["missing_frontend_contracts"]
        and not f["missing_qa_lab_options"]
        and f.get("db_records_found") == len(TARGET_HERO_IDS)
    )


def print_audit(f: dict) -> None:
    print("=" * 78)
    print(" RM1.22-K — PRE-APPLY AUDIT")
    print("=" * 78)
    print(f"  target heroes count         : {f['target_count']}")
    print(f"  manifest match              : {'OK' if f.get('manifest_match') else 'FAIL'}")
    print(f"  target ∩ protected          : {f['target_intersects_protected']}")
    print(f"  DB records found            : {f['db_records_found']}/{f['target_count']}")
    print(f"  missing DB records          : {len(f['missing_db_records'])}")
    print(f"  unexpected DB status        : {len(f['unexpected_status'])}")
    for x in f["unexpected_status"]:
        print(f"      - {x['id']}: {x['issues']}")
    print(f"  missing asset folders       : {len(f['missing_asset_dirs'])}")
    print(f"  missing placeholder_status  : {len(f['missing_placeholder_status'])}")
    print(f"  bad placeholder_status      : {len(f['bad_placeholder_status'])}")
    print(f"  missing runtime files       : {len(f['missing_runtime_files'])}")
    print(f"  missing frontend contracts  : {len(f['missing_frontend_contracts'])}")
    print(f"  missing QA Lab options      : {len(f['missing_qa_lab_options'])}")
    print("=" * 78)
    print(f"  RESULT: {'✓ PASS' if audit_passed(f) else '❌ FAIL — STOP'}")
    print("=" * 78)


async def apply_activation(db, dry_run: bool) -> dict:
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
    # FILTRO STRETTO difensivo:
    #   - ID ∈ TARGET
    #   - is_official True (no legacy)
    #   - is_legacy_placeholder False
    #   - native_rarity == TARGET_NATIVE_RARITY (no 1★/2★/3★/5★/6★)
    #   - asset_status != "approved_final" (non toccare final)
    flt = {
        "id": {"$in": TARGET_HERO_IDS},
        "is_official": True,
        "is_legacy_placeholder": False,
        "native_rarity": TARGET_NATIVE_RARITY,
        "asset_status": {"$ne": "approved_final"},
    }

    matched = await db.heroes.count_documents(flt)

    if dry_run:
        return {"dry_run": True, "would_match": matched}

    res = await db.heroes.update_many(flt, update_doc)
    return {
        "dry_run": False,
        "matched_count": res.matched_count,
        "modified_count": res.modified_count,
    }


async def smoke_visibility(db) -> dict:
    sys.path.insert(0, str(BACKEND_ROOT))
    from utils.hero_visibility import (
        should_show_in_catalog,
        should_show_in_summon,
    )

    all_h = await db.heroes.find({}, {"image_base64": 0}).to_list(None)
    show_cat = [h for h in all_h if should_show_in_catalog(h, owned=False)]
    summon = [h for h in all_h if should_show_in_summon(h)]
    starter = [h for h in summon if (h.get("native_rarity") or h.get("rarity") or 99) <= 2]

    legacy_sum = [h for h in summon if h.get("is_legacy_placeholder")]
    pending_sum = [h for h in summon if h.get("asset_status") == "pending_assets"]
    pending_6_sum = [
        h for h in summon
        if h.get("asset_status") == "pending_assets"
        and (h.get("native_rarity") or 0) >= 6
    ]
    greek_borea_sum = [h for h in summon if h.get("id") == "greek_borea"]
    legacy_borea_sum = [h for h in summon if h.get("id") == "borea"]

    activated_targets = await db.heroes.count_documents({
        "id": {"$in": TARGET_HERO_IDS},
        "activation_status": "active_with_placeholder_assets",
        "activation_batch": ACTIVATION_BATCH,
    })

    by_rarity = {}
    for h in summon:
        r = h.get("native_rarity") or h.get("rarity") or 0
        by_rarity[r] = by_rarity.get(r, 0) + 1

    # Hidden pending 6★ (post-RM1.22-K expectation: 13 = 12 launch_base + Borea)
    hidden_6 = await db.heroes.count_documents({
        "asset_status": "pending_assets",
        "native_rarity": {"$gte": 6},
    })

    return {
        "total_heroes": len(all_h),
        "show_in_catalog": len(show_cat),
        "summon_eligible": len(summon),
        "summon_eligible_by_rarity": dict(sorted(by_rarity.items())),
        "starter_eligible_rarity_le_2": len(starter),
        "legacy_summon_eligible": len(legacy_sum),
        "pending_any_summon_eligible": len(pending_sum),
        "pending_6_summon_eligible": len(pending_6_sum),
        "greek_borea_summon_eligible": len(greek_borea_sum),
        "legacy_borea_summon_eligible": len(legacy_borea_sum),
        "activated_rm122k_5star": activated_targets,
        "hidden_pending_6_count": hidden_6,
    }


async def verify_protected_untouched(db) -> dict:
    """Legge Hoplite/Berserker/greek_borea per conferma nessuna traccia di batch."""
    out = {}
    for hid in sorted(PROTECTED_IDS):
        h = await db.heroes.find_one({"id": hid}, {"image_base64": 0})
        out[hid] = {
            "exists": bool(h),
            "activation_batch": h.get("activation_batch") if h else None,
            "obtainable": h.get("obtainable") if h else None,
            "show_in_catalog": h.get("show_in_catalog") if h else None,
            "asset_status": h.get("asset_status") if h else None,
        }
    return out


async def main() -> int:
    ap = argparse.ArgumentParser(description="RM1.22-K — Activate 5★ placeholder heroes")
    ap.add_argument("--apply", action="store_true",
                    help=f"Esegue il write reale. Richiede {ENV_CONFIRM_KEY}={ENV_CONFIRM_VAL}.")
    args = ap.parse_args()

    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "divine_waifus")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    findings = await audit(db)
    print_audit(findings)
    if not audit_passed(findings):
        print("\n❌ AUDIT FAIL — stop.")
        client.close()
        return 1

    print("\n" + "=" * 78)
    print(" SMOKE PRE-APPLY (read-only)")
    print("=" * 78)
    pre = await smoke_visibility(db)
    for k, v in pre.items():
        print(f"  {k:40s} = {v}")
    print("=" * 78)

    if not args.apply:
        print("\n[DRY-RUN] default mode. Per scrivere usa --apply con env-var.")
        result = await apply_activation(db, dry_run=True)
        print(f"  matched_count (would update): {result['would_match']}")
        client.close()
        return 0

    confirm = os.getenv(ENV_CONFIRM_KEY)
    if confirm != ENV_CONFIRM_VAL:
        print(f"\n❌ ABORT: {ENV_CONFIRM_KEY} non impostato.")
        print(f"   Atteso: {ENV_CONFIRM_VAL}")
        print(f"   Trovato: {confirm!r}")
        client.close()
        return 2

    print("\n" + "=" * 78)
    print(" APPLY")
    print("=" * 78)
    result = await apply_activation(db, dry_run=False)
    print(f"  matched  : {result['matched_count']}")
    print(f"  modified : {result['modified_count']}")
    print("=" * 78)

    print("\n" + "=" * 78)
    print(" SMOKE POST-APPLY (read-only)")
    print("=" * 78)
    post = await smoke_visibility(db)
    for k, v in post.items():
        print(f"  {k:40s} = {v}")
    print("=" * 78)

    print("\n" + "=" * 78)
    print(" PROTECTED IDs POST-APPLY (Hoplite/Berserker/greek_borea)")
    print("=" * 78)
    prot = await verify_protected_untouched(db)
    for k, v in prot.items():
        print(f"  {k}: {v}")
    print("=" * 78)

    report_dir = BACKEND_ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    report_path = report_dir / f"placeholder_activation_5star_APPLIED_{ts}.json"
    payload = {
        "task": "RM1.22-K",
        "applied_at": datetime.utcnow().isoformat() + "Z",
        "activation_batch": ACTIVATION_BATCH,
        "target_hero_ids": TARGET_HERO_IDS,
        "matched_count": result["matched_count"],
        "modified_count": result["modified_count"],
        "smoke_pre": pre,
        "smoke_post": post,
        "protected_post": prot,
    }
    report_path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"  report : {report_path}")

    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
