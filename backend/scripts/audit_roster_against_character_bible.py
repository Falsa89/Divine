#!/usr/bin/env python3
"""
RM1.20-A — Roster Audit Script (READ-ONLY)
═══════════════════════════════════════════════════════════════════════
Confronta la collezione `heroes` MongoDB con il Character Bible ufficiale
e produce un report strutturato (console + JSON).

NESSUNA scrittura su DB. NESSUNA modifica a heroes/user_heroes/teams.

Uso:
    python backend/scripts/audit_roster_against_character_bible.py

Output:
    - Console: report leggibile.
    - JSON:    backend/reports/roster_audit_<timestamp>.json
"""
from __future__ import annotations
import asyncio
import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Backend root on sys.path (script può essere lanciato da qualsiasi cwd)
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(BACKEND_ROOT.parent))  # /app per import 'backend.*'

from dotenv import load_dotenv
load_dotenv(BACKEND_ROOT / ".env")

from motor.motor_asyncio import AsyncIOMotorClient
from data.character_bible import (
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


def classify_legacy(db_hero: Dict[str, Any]) -> str:
    """Raccomanda lo status di soft-deactivation per un eroe non-ufficiale."""
    return "legacy_placeholder_keep_owned"  # default conservativo


async def main() -> int:
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "divine_waifus")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    # ── A. Character Bible summary ─────────────────────────────────────
    bible_total = len(CHARACTER_BIBLE)
    by_rarity = Counter(e["native_rarity"] for e in CHARACTER_BIBLE)
    by_element = Counter(normalize_element(e["element"]) for e in CHARACTER_BIBLE)
    by_role = Counter(normalize_role(e["role"]) for e in CHARACTER_BIBLE)
    by_faction = Counter(normalize_faction(e["faction"]) for e in CHARACTER_BIBLE)
    by_release = Counter(e["release_group"] for e in CHARACTER_BIBLE)

    # ── B. DB heroes summary ───────────────────────────────────────────
    heroes_cur = db.heroes.find({})
    db_heroes = await heroes_cur.to_list(length=None)
    db_total = len(db_heroes)
    db_ids = set(h.get("id") for h in db_heroes if h.get("id"))
    bible_ids = set(CHARACTER_BIBLE_BY_ID.keys())

    official_present = sorted(db_ids & bible_ids)
    official_missing = sorted(bible_ids - db_ids)
    legacy_candidates_ids = sorted(db_ids - bible_ids)

    # ── C. Legacy placeholder details ──────────────────────────────────
    user_heroes_cur = db.user_heroes.find({}, {"hero_id": 1, "user_id": 1})
    user_heroes_docs = await user_heroes_cur.to_list(length=None)
    ownership_count: Counter = Counter()
    user_hero_ids_seen: Counter = Counter()
    for uh in user_heroes_docs:
        hid = uh.get("hero_id")
        if hid:
            user_hero_ids_seen[hid] += 1

    # team usage
    teams_cur = db.users.find({}, {"team": 1, "email": 1, "_id": 1, "active_team": 1})
    user_docs = await teams_cur.to_list(length=None)
    team_legacy_users: List[Dict[str, Any]] = []
    legacy_in_active_team: Counter = Counter()
    for u in user_docs:
        team_field = u.get("active_team") or u.get("team") or []
        if not isinstance(team_field, list):
            continue
        # team può essere lista di hero_id strings o di obj con hero_id
        flat_ids: List[str] = []
        for slot in team_field:
            if isinstance(slot, str):
                flat_ids.append(slot)
            elif isinstance(slot, dict):
                hid = slot.get("hero_id") or slot.get("id")
                if hid:
                    flat_ids.append(hid)
        legacy_in_team = [hid for hid in flat_ids if hid not in bible_ids]
        if legacy_in_team:
            team_legacy_users.append({
                "user_id": str(u.get("_id")),
                "email": u.get("email"),
                "legacy_hero_ids": sorted(set(legacy_in_team)),
            })
            for hid in legacy_in_team:
                legacy_in_active_team[hid] += 1

    # legacy details
    legacy_details: List[Dict[str, Any]] = []
    for hid in legacy_candidates_ids:
        h = next((x for x in db_heroes if x.get("id") == hid), {}) or {}
        legacy_details.append({
            "id": hid,
            "name": h.get("name"),
            "rarity": h.get("rarity") or h.get("hero_rarity"),
            "element": h.get("element"),
            "role": h.get("role"),
            "faction": h.get("faction"),
            "image_url": (h.get("image") or h.get("image_url") or "")[:60],
            "owned_by_users": user_hero_ids_seen.get(hid, 0),
            "in_active_team_count": legacy_in_active_team.get(hid, 0),
            "recommended_status": classify_legacy(h),
        })

    # ── D. User ownership impact ───────────────────────────────────────
    user_heroes_total = len(user_heroes_docs)
    user_heroes_official = sum(1 for uh in user_heroes_docs if uh.get("hero_id") in bible_ids)
    user_heroes_legacy = user_heroes_total - user_heroes_official
    top_legacy_owned = sorted(
        ((hid, c) for hid, c in user_hero_ids_seen.items() if hid not in bible_ids),
        key=lambda x: -x[1],
    )[:20]

    # test@test.com legacy ownership
    test_user = await db.users.find_one({"email": "test@test.com"}, {"_id": 1})
    test_legacy_ids: List[str] = []
    if test_user:
        cur = db.user_heroes.find({"user_id": str(test_user["_id"])}, {"hero_id": 1})
        async for uh in cur:
            hid = uh.get("hero_id")
            if hid and hid not in bible_ids:
                test_legacy_ids.append(hid)

    # ── F. Recommended migration plan ──────────────────────────────────
    recommendations = [
        "Phase 1: keep all owned legacy heroes intact in user_heroes.",
        "Phase 2: set is_official/is_legacy_placeholder/show_in_* flags via plan_legacy_soft_deactivation.py --apply (DRY-RUN by default).",
        "Phase 3: catalog/summon hide legacy non-owned (route filter, not deletion).",
        "Phase 4: battle picker honors team-migration strategy before hiding legacy from active teams.",
        "NEVER delete heroes or user_heroes records.",
    ]

    report: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "db": {"mongo_url_redacted": mongo_url.split("@")[-1], "db_name": db_name},
        "character_bible_summary": {
            "total_official": bible_total,
            "by_release_group": dict(by_release),
            "by_rarity": dict(by_rarity),
            "by_element": dict(by_element),
            "by_role": dict(by_role),
            "by_faction": dict(by_faction),
            "launch_base_count": len(LAUNCH_BASE_HERO_IDS),
            "extra_premium_count": len(EXTRA_PREMIUM_HERO_IDS),
            "extra_premium_ids": EXTRA_PREMIUM_HERO_IDS,
        },
        "db_summary": {
            "heroes_total": db_total,
            "official_present": len(official_present),
            "official_missing": len(official_missing),
            "legacy_candidates": len(legacy_candidates_ids),
            "official_missing_ids": official_missing,
            "legacy_candidate_ids_sample": legacy_candidates_ids[:50],
        },
        "legacy_details": legacy_details,
        "user_ownership_impact": {
            "user_heroes_total": user_heroes_total,
            "user_heroes_official": user_heroes_official,
            "user_heroes_legacy": user_heroes_legacy,
            "top_legacy_by_ownership": [{"hero_id": h, "count": c} for h, c in top_legacy_owned],
            "test_account_legacy_owned_count": len(test_legacy_ids),
            "test_account_legacy_owned_ids_sample": test_legacy_ids[:20],
        },
        "team_impact": {
            "users_with_legacy_in_active_team": len(team_legacy_users),
            "legacy_ids_in_active_teams": [{"hero_id": h, "count": c} for h, c in legacy_in_active_team.items()],
            "warning": "Do NOT hide legacy heroes from battle picker until per-user team migration is in place.",
        },
        "recommendations": recommendations,
        "safety": {
            "db_writes_performed": False,
            "user_heroes_modified": False,
            "teams_modified": False,
            "heroes_deleted": False,
        },
    }

    # ── Console output ────────────────────────────────────────────────
    print("=" * 72)
    print("ROSTER AUDIT vs CHARACTER BIBLE — READ-ONLY")
    print("=" * 72)
    print(f"DB:              {db_name}")
    print(f"Bible total:     {bible_total} ({len(LAUNCH_BASE_HERO_IDS)} base + {len(EXTRA_PREMIUM_HERO_IDS)} premium)")
    print(f"DB heroes:       {db_total}")
    print(f"  official:      {len(official_present)}")
    print(f"  missing:       {len(official_missing)}")
    print(f"  legacy:        {len(legacy_candidates_ids)}")
    print(f"User heroes:     {user_heroes_total}")
    print(f"  official:      {user_heroes_official}")
    print(f"  legacy:        {user_heroes_legacy}")
    print(f"Test account legacy owned: {len(test_legacy_ids)}")
    print(f"Users with legacy in active team: {len(team_legacy_users)}")
    print()
    print("Top legacy IDs by ownership (preview):")
    for h, c in top_legacy_owned[:10]:
        print(f"  {h:40s} owned×{c}")
    print()
    print("Bible distribution:")
    print(f"  by_rarity:  {dict(by_rarity)}")
    print(f"  by_element: {dict(by_element)}")
    print(f"  by_role:    {dict(by_role)}")
    print(f"  by_faction: {dict(by_faction)}")
    print()

    # ── Write JSON report ─────────────────────────────────────────────
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = REPORTS_DIR / f"roster_audit_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"JSON report: {out_path}")
    print()
    print("Recommendations:")
    for rec in recommendations:
        print(f"  - {rec}")

    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
