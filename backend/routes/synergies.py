"""
Divine Waifus - Synergy Routes
Team synergy endpoints for checking and displaying active synergies.
"""
from fastapi import Depends
from synergy_system import calculate_team_synergies, get_all_synergy_definitions


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
