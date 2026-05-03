"""
Divine Waifus - Synergy Routes
Team synergy endpoints for checking and displaying active synergies.

V1 endpoints (legacy, name-based):
    GET /api/synergies/guide
    GET /api/synergies/team

V2 endpoints (RM1.23-B, ID-based, read-only):
    GET /api/synergies/team_v2
    GET /api/synergies/v2/all       (lista enabled per UI guide)

V1 e V2 coesistono. V2 NON modifica V1.
"""
from fastapi import Depends
from synergy_system import calculate_team_synergies, get_all_synergy_definitions
from data.synergy_definitions_v2 import (
    get_enabled_team_synergies_v2,
)
from data.character_bible import CHARACTER_BIBLE_BY_ID as _BIBLE_BY_ID
from utils.team_synergy_v2_calculator import compute_team_synergies_v2


def register_synergy_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    @router.get("/synergies/guide")
    async def get_synergy_guide():
        """Get all synergy definitions for the guide/encyclopedia."""
        return get_all_synergy_definitions()

    @router.get("/synergies/team")
    async def get_team_synergies(current_user: dict = Depends(get_current_user)):
        """Get active synergies for the current team."""
        uid = current_user["id"]
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        if not team or not team.get("formation"):
            return {"active_synergies": [], "total_buffs": {}, "synergy_count": 0}

        names, elements, classes = [], [], []
        for pos in team.get("formation", []):
            uhid = pos.get("user_hero_id")
            if not uhid:
                continue
            uh = await db.user_heroes.find_one({"id": uhid, "user_id": uid})
            if not uh:
                continue
            hero = await db.heroes.find_one({"id": uh["hero_id"]})
            if hero:
                names.append(hero.get("name", ""))
                elements.append(hero.get("element", "neutral"))
                classes.append(hero.get("hero_class", "DPS"))
            else:
                names.append(uh.get("hero_name", ""))
                elements.append(uh.get("hero_element", "neutral"))
                classes.append(uh.get("hero_class", "DPS"))

        result = calculate_team_synergies(names, elements, classes)
        return result

    # ── RM1.23-B V2 endpoints (READ-ONLY, ID-based) ────────────────────
    @router.get("/synergies/team_v2")
    async def get_team_synergies_v2(current_user: dict = Depends(get_current_user)):
        """Get active V2 ID-based team synergies for the current team.

        Read-only. Nessuna mutazione DB. Coesiste con /api/synergies/team
        (V1). Per legacy team senza canonical IDs, ritorna safely empty.
        """
        uid = current_user["id"]
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        if not team or not team.get("formation"):
            return {
                "active_team_synergies_v2": [],
                "near_complete": [],
                "aggregated_buffs": {},
                "members_resolved": 0,
                "members_skipped_legacy_or_orphan": 0,
                "team_id": None,
            }

        # Resolve only the user_heroes referenced by this active team
        # (efficient: avoid loading all 1700+ user_heroes).
        slot_uhids = [
            pos.get("user_hero_id")
            for pos in team.get("formation", [])
            if pos.get("user_hero_id")
        ]
        user_heroes_list = await db.user_heroes.find(
            {"id": {"$in": slot_uhids}, "user_id": uid}
        ).to_list(None)
        user_heroes_by_id = {uh["id"]: uh for uh in user_heroes_list}

        # Resolve the heroes referenced (full collection for UI metadata)
        hero_ids = list({uh.get("hero_id") for uh in user_heroes_list if uh.get("hero_id")})
        heroes_list = await db.heroes.find(
            {"id": {"$in": hero_ids}}, {"image_base64": 0}
        ).to_list(None)
        heroes_by_id = {h["id"]: h for h in heroes_list}

        bible_ids = set(_BIBLE_BY_ID.keys())
        enabled = get_enabled_team_synergies_v2()

        result = compute_team_synergies_v2(
            team_doc=team,
            user_heroes_by_id=user_heroes_by_id,
            heroes_by_id=heroes_by_id,
            enabled_synergies=enabled,
            bible_ids=bible_ids,
        )
        result["team_id"] = team.get("id")
        result["enabled_synergy_count"] = len(enabled)
        return result

    @router.get("/synergies/v2/all")
    async def get_all_v2_definitions():
        """Public read-only list of enabled V2 synergies for UI guide."""
        enabled = get_enabled_team_synergies_v2()
        return {
            "version": 2,
            "team_synergies": [
                {
                    "id": s["id"],
                    "display_name": s.get("display_name") or s["id"],
                    "description": s.get("description"),
                    "lore_group": s.get("lore_group"),
                    "icon": s.get("icon"),
                    "rarity_tier": s.get("rarity_tier"),
                    "release_group": s.get("release_group"),
                    "required_hero_ids": s.get("required_hero_ids", []),
                    "min_required": s.get("min_required"),
                    "max_members": s.get("max_members"),
                    "effects": s.get("effects", []),
                    "target_filter": s.get("target_filter"),
                }
                for s in enabled
            ],
            "count": len(enabled),
        }
