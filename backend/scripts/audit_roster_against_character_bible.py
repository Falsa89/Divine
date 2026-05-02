#!/usr/bin/env python3
"""
RM1.20-A — Roster Audit Script (READ-ONLY)
═══════════════════════════════════════════════════════════════════════
Confronta la collezione `heroes` MongoDB con il Character Bible ufficiale e
produce un report strutturato (console + JSON).

Garanzie di sicurezza:
  • NESSUNA scrittura su DB.
  • NESSUNA modifica a `heroes`, `user_heroes`, `teams`, `users`.
  • NESSUNA cancellazione.
  • NESSUNA mutazione del comportamento runtime/endpoint.

Uso:
    cd /app && python backend/scripts/audit_roster_against_character_bible.py

Output:
    • Console: report leggibile in italiano.
    • JSON:    backend/reports/roster_audit_<timestamp>.json
"""
from __future__ import annotations
import asyncio
import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Backend root in sys.path (script lanciabile da qualsiasi cwd).
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
)

REPORTS_DIR = BACKEND_ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def _redact_mongo(url: str) -> str:
    """Rimuove credenziali se presenti (mongodb://user:pass@host/...)."""
    return url.split("@")[-1] if "@" in url else url


def _flatten_team_user_hero_ids(team_doc: Optional[Dict[str, Any]]) -> List[str]:
    """Estrae i `user_hero_id` da un documento team. Lo schema canonico è
    `formation: [{user_hero_id, position, ...}, ...]` (vedi routes/combat.py)."""
    if not team_doc:
        return []
    formation = team_doc.get("formation") or []
    out: List[str] = []
    if isinstance(formation, list):
        for slot in formation:
            if isinstance(slot, dict):
                uhid = slot.get("user_hero_id") or slot.get("id")
                if uhid:
                    out.append(uhid)
            elif isinstance(slot, str):
                out.append(slot)
    return out


async def main() -> int:
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "divine_waifus")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    # ── A. Riepilogo Character Bible (source of truth) ────────────────
    bible_total = len(CHARACTER_BIBLE)
    by_rarity_bible = Counter(e["native_rarity"] for e in CHARACTER_BIBLE)
    by_element_bible = Counter(normalize_element(e["element"]) for e in CHARACTER_BIBLE)
    by_role_bible = Counter(normalize_role(e["role"]) for e in CHARACTER_BIBLE)
    by_faction_bible = Counter(normalize_faction(e["faction"]) for e in CHARACTER_BIBLE)
    by_release_bible = Counter(e["release_group"] for e in CHARACTER_BIBLE)

    bible_ids = set(CHARACTER_BIBLE_BY_ID.keys())

    # ── B. Riepilogo heroes nel DB ─────────────────────────────────────
    db_heroes: List[Dict[str, Any]] = await db.heroes.find(
        {}, {"image_base64": 0}
    ).to_list(length=None)
    db_total = len(db_heroes)
    db_ids: set = {h.get("id") for h in db_heroes if h.get("id")}

    official_present = sorted(db_ids & bible_ids)
    official_missing = sorted(bible_ids - db_ids)
    legacy_candidate_ids = sorted(db_ids - bible_ids)

    # Distribuzioni DB (utili per debug drift)
    by_rarity_db = Counter(h.get("rarity") for h in db_heroes)
    by_element_db = Counter(h.get("element") for h in db_heroes)
    by_role_db = Counter(h.get("role") for h in db_heroes)
    by_faction_db = Counter(h.get("faction") for h in db_heroes)

    # ── C. user_heroes — ownership impact ─────────────────────────────
    user_heroes_docs: List[Dict[str, Any]] = await db.user_heroes.find(
        {}, {"hero_id": 1, "user_id": 1, "id": 1}
    ).to_list(length=None)
    user_heroes_total = len(user_heroes_docs)
    ownership_count: Counter = Counter()
    user_hero_id_to_hero_id: Dict[str, str] = {}
    for uh in user_heroes_docs:
        hid = uh.get("hero_id")
        if hid:
            ownership_count[hid] += 1
        uhid = uh.get("id")
        if uhid and hid:
            user_hero_id_to_hero_id[uhid] = hid

    user_heroes_official = sum(
        1 for uh in user_heroes_docs if uh.get("hero_id") in bible_ids
    )
    user_heroes_legacy = user_heroes_total - user_heroes_official

    top_legacy_owned: List[Tuple[str, int]] = sorted(
        ((hid, c) for hid, c in ownership_count.items() if hid not in bible_ids),
        key=lambda x: -x[1],
    )[:25]

    # ── D. teams — active formation impact ────────────────────────────
    teams_docs: List[Dict[str, Any]] = await db.teams.find(
        {"is_active": True}, {"user_id": 1, "formation": 1, "id": 1}
    ).to_list(length=None)

    legacy_in_active_team_count: Counter = Counter()
    users_with_legacy_team: List[Dict[str, Any]] = []
    for t in teams_docs:
        uhids = _flatten_team_user_hero_ids(t)
        legacy_hero_ids: List[str] = []
        for uhid in uhids:
            hid = user_hero_id_to_hero_id.get(uhid)
            if hid and hid not in bible_ids:
                legacy_hero_ids.append(hid)
        if legacy_hero_ids:
            for hid in legacy_hero_ids:
                legacy_in_active_team_count[hid] += 1
            users_with_legacy_team.append({
                "user_id": t.get("user_id"),
                "legacy_hero_ids": sorted(set(legacy_hero_ids)),
            })

    # ── E. Account di test (test@test.com) ────────────────────────────
    test_user = await db.users.find_one(
        {"email": "test@test.com"}, {"id": 1, "email": 1}
    )
    test_legacy_owned: List[str] = []
    test_legacy_in_team: List[str] = []
    test_user_id: Optional[str] = None
    if test_user:
        test_user_id = test_user.get("id")
        if test_user_id:
            cur = db.user_heroes.find(
                {"user_id": test_user_id}, {"hero_id": 1}
            )
            async for uh in cur:
                hid = uh.get("hero_id")
                if hid and hid not in bible_ids:
                    test_legacy_owned.append(hid)
            t = await db.teams.find_one(
                {"user_id": test_user_id, "is_active": True},
                {"formation": 1},
            )
            for uhid in _flatten_team_user_hero_ids(t):
                hid = user_hero_id_to_hero_id.get(uhid)
                if hid and hid not in bible_ids:
                    test_legacy_in_team.append(hid)

    # ── F. Dettaglio per legacy candidate ─────────────────────────────
    legacy_details: List[Dict[str, Any]] = []
    for hid in legacy_candidate_ids:
        h = next((x for x in db_heroes if x.get("id") == hid), {}) or {}
        legacy_details.append({
            "id": hid,
            "name": h.get("name"),
            "rarity": h.get("rarity"),
            "element": h.get("element"),
            "role": h.get("role"),
            "faction": h.get("faction"),
            "owned_by_users": ownership_count.get(hid, 0),
            "in_active_team_count": legacy_in_active_team_count.get(hid, 0),
            "recommended_action": (
                "soft_deactivate (preserve owned)"
                if ownership_count.get(hid, 0) > 0
                else "soft_deactivate (no owners)"
            ),
        })

    # ── G. Banner / gacha pool — ispezione passiva ────────────────────
    # I banner sono attualmente hardcoded in server.py (GACHA_BANNERS).
    # Non leggono da DB il filtro per legacy/official, quindi qui non c'è
    # nulla da modificare ora. Documentiamo solo il fatto.
    gacha_note = (
        "GACHA_BANNERS è hardcoded in backend/server.py. Non filtra per "
        "is_official/obtainable. Filtro da introdurre nella fase --apply "
        "(non in questo task)."
    )

    # ── H. Composizione del report ────────────────────────────────────
    report: Dict[str, Any] = {
        "task": "RM1.20-A",
        "kind": "roster_audit",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "db": {
            "mongo_url_redacted": _redact_mongo(mongo_url),
            "db_name": db_name,
        },
        "character_bible_summary": {
            "total_official": bible_total,
            "by_release_group": dict(by_release_bible),
            "by_rarity": dict(by_rarity_bible),
            "by_element": dict(by_element_bible),
            "by_role": dict(by_role_bible),
            "by_faction": dict(by_faction_bible),
            "launch_base_count": len(LAUNCH_BASE_HERO_IDS),
            "extra_premium_count": len(EXTRA_PREMIUM_HERO_IDS),
            "extra_premium_ids": EXTRA_PREMIUM_HERO_IDS,
        },
        "db_summary": {
            "heroes_total": db_total,
            "official_present": len(official_present),
            "official_missing": len(official_missing),
            "legacy_candidates": len(legacy_candidate_ids),
            "official_missing_ids": official_missing,
            "legacy_candidate_ids": legacy_candidate_ids,
            "by_rarity_db": dict(by_rarity_db),
            "by_element_db": dict(by_element_db),
            "by_role_db": dict(by_role_db),
            "by_faction_db": dict(by_faction_db),
        },
        "legacy_details": legacy_details,
        "user_ownership_impact": {
            "user_heroes_total": user_heroes_total,
            "user_heroes_official": user_heroes_official,
            "user_heroes_legacy": user_heroes_legacy,
            "top_legacy_by_ownership": [
                {"hero_id": h, "owned_count": c} for h, c in top_legacy_owned
            ],
        },
        "team_impact": {
            "active_teams_total": len(teams_docs),
            "users_with_legacy_in_active_team": len(users_with_legacy_team),
            "legacy_in_active_team_count": [
                {"hero_id": h, "count": c}
                for h, c in legacy_in_active_team_count.most_common()
            ],
            "warning": (
                "Non nascondere i legacy dal battle picker finché non "
                "esiste una strategia per-utente di migrazione del team."
            ),
        },
        "test_account_impact": {
            "email": "test@test.com",
            "found": test_user is not None,
            "user_id": test_user_id,
            "legacy_owned_count": len(test_legacy_owned),
            "legacy_owned_ids_sample": sorted(set(test_legacy_owned))[:30],
            "legacy_in_active_team_ids": sorted(set(test_legacy_in_team)),
        },
        "gacha_note": gacha_note,
        "recommendations": [
            "Mantenere intatti tutti i user_heroes posseduti (mai DELETE).",
            "Pianificare soft-deactivation tramite plan_legacy_soft_deactivation.py "
            "(dry-run di default; --apply NON eseguito in RM1.20-A).",
            "Importare gli eroi ufficiali mancanti in fase successiva (non in questo task).",
            "Filtrare catalog/summon per is_official/obtainable solo dopo --apply.",
            "Battle picker: rispettare strategia di team-migration per-utente prima di nascondere legacy in team attivi.",
        ],
        "safety": {
            "db_writes_performed": False,
            "user_heroes_modified": False,
            "teams_modified": False,
            "users_modified": False,
            "heroes_deleted": False,
            "apply_flag_executed": False,
        },
    }

    # ── Console output (italiano) ─────────────────────────────────────
    print("=" * 78)
    print(" RM1.20-A — AUDIT ROSTER vs CHARACTER BIBLE  (READ-ONLY)")
    print("=" * 78)
    print(f" DB:                 {db_name}  ({_redact_mongo(mongo_url)})")
    print(f" Character Bible:    {bible_total} eroi totali")
    print(f"   • launch_base:    {len(LAUNCH_BASE_HERO_IDS)}")
    print(f"   • extra_premium:  {len(EXTRA_PREMIUM_HERO_IDS)}  -> {EXTRA_PREMIUM_HERO_IDS}")
    print()
    print(f" Heroes nel DB:      {db_total}")
    print(f"   • ufficiali presenti:   {len(official_present)}")
    print(f"   • ufficiali mancanti:   {len(official_missing)}")
    print(f"   • legacy candidates:    {len(legacy_candidate_ids)}")
    print()
    print(f" user_heroes:        {user_heroes_total}")
    print(f"   • ufficiali:        {user_heroes_official}")
    print(f"   • legacy:           {user_heroes_legacy}")
    print()
    print(f" Active teams:               {len(teams_docs)}")
    print(f"   • con legacy in formation: {len(users_with_legacy_team)}")
    print()
    print(" Account test@test.com:")
    print(f"   • trovato:                 {test_user is not None}")
    print(f"   • legacy owned:            {len(test_legacy_owned)}")
    print(f"   • legacy in active team:   {len(set(test_legacy_in_team))}")
    print()
    if top_legacy_owned:
        print(" Top legacy per ownership (preview, max 10):")
        for h, c in top_legacy_owned[:10]:
            print(f"   - {h:42s}  owned×{c}")
        print()
    if official_missing:
        print(f" Ufficiali mancanti dal DB (preview, max 10 di {len(official_missing)}):")
        for hid in official_missing[:10]:
            entry = CHARACTER_BIBLE_BY_ID.get(hid, {})
            print(f"   - {hid:42s}  ({entry.get('display_name', '?')})")
        print()

    # ── Scrittura JSON ────────────────────────────────────────────────
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = REPORTS_DIR / f"roster_audit_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str, ensure_ascii=False)
    print(f" Report JSON: {out_path}")
    print()
    print(" SAFETY CHECKS:")
    for k, v in report["safety"].items():
        print(f"   • {k:32s} = {v}")
    print()
    print(" Raccomandazioni:")
    for rec in report["recommendations"]:
        print(f"   - {rec}")
    print()
    print("=" * 78)
    print(" FINE AUDIT — nessuna scrittura DB eseguita.")
    print("=" * 78)

    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
