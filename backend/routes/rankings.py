"""
Divine Waifus - Rankings Routes
"""
from fastapi import Depends
from .game_data import RANK_TIERS


def register_rankings_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    async def _build_ranking(field: str, collection: str, sort_field: str, limit: int = 50, current_uid: str = ""):
        entries = await db[collection].find({}).sort(sort_field, -1).limit(limit).to_list(limit)
        ranking = []
        my_rank = None
        for i, entry in enumerate(entries):
            uid = entry.get("user_id", entry.get("id", ""))
            user = await db.users.find_one({"id": uid})
            if not user:
                continue
            cosmetics = await db.user_cosmetics.find_one({"user_id": uid})
            score = entry.get(sort_field, 0)
            tier = RANK_TIERS[0]
            for t in RANK_TIERS:
                if score >= t["min"]:
                    tier = t
            rank_entry = {
                "rank": i + 1,
                "user_id": uid,
                "username": user.get("username", "???"),
                "level": user.get("level", 1),
                "title": user.get("active_title", ""),
                "faction": user.get("faction"),
                "is_bot": user.get("is_bot", False),
                "score": score,
                "tier_name": tier["name"],
                "tier_color": tier["color"],
                "tier_icon": tier["icon"],
                "frame": cosmetics.get("active_frame", "bronze") if cosmetics else "bronze",
                "aura": cosmetics.get("active_aura") if cosmetics else None,
                "is_you": uid == current_uid,
            }
            ranking.append(rank_entry)
            if uid == current_uid:
                my_rank = rank_entry
        return ranking, my_rank

    @router.get("/rankings/arena")
    async def get_arena_ranking(current_user: dict = Depends(get_current_user)):
        ranking, my_rank = await _build_ranking("trophies", "pvp_data", "trophies", 50, current_user["id"])
        return {"type": "arena", "title": "Classifica Arena", "ranking": ranking, "my_rank": my_rank}

    @router.get("/rankings/power")
    async def get_power_ranking(current_user: dict = Depends(get_current_user)):
        ranking, my_rank = await _build_ranking("total_power", "teams", "total_power", 50, current_user["id"])
        return {"type": "power", "title": "Classifica Potenza", "ranking": ranking, "my_rank": my_rank}

    @router.get("/rankings/tower")
    async def get_tower_ranking(current_user: dict = Depends(get_current_user)):
        ranking, my_rank = await _build_ranking("highest_floor", "tower_progress", "highest_floor", 50, current_user["id"])
        return {"type": "tower", "title": "Classifica Torre", "ranking": ranking, "my_rank": my_rank}

    @router.get("/rankings/level")
    async def get_level_ranking(current_user: dict = Depends(get_current_user)):
        users = await db.users.find({}).sort("level", -1).limit(50).to_list(50)
        ranking = []
        my_rank = None
        for i, u in enumerate(users):
            cosmetics = await db.user_cosmetics.find_one({"user_id": u["id"]})
            entry = {
                "rank": i + 1,
                "user_id": u["id"],
                "username": u.get("username", "???"),
                "level": u.get("level", 1),
                "title": u.get("active_title", ""),
                "faction": u.get("faction"),
                "is_bot": u.get("is_bot", False),
                "score": u.get("level", 1),
                "tier_name": "", "tier_color": "#ffd700", "tier_icon": "",
                "frame": cosmetics.get("active_frame", "bronze") if cosmetics else "bronze",
                "aura": cosmetics.get("active_aura") if cosmetics else None,
                "is_you": u["id"] == current_user["id"],
            }
            ranking.append(entry)
            if u["id"] == current_user["id"]:
                my_rank = entry
        return {"type": "level", "title": "Classifica Livello", "ranking": ranking, "my_rank": my_rank}

    @router.get("/rankings/guild")
    async def get_guild_ranking(current_user: dict = Depends(get_current_user)):
        guilds = await db.guilds.find({}).to_list(50)
        ranking = []
        for i, g in enumerate(guilds):
            territories = await db.territory_control.count_documents({"guild_id": g["id"]})
            member_count = len(g.get("members", []))
            guild_score = territories * 1000 + member_count * 100 + g.get("level", 1) * 50
            ranking.append({
                "rank": i + 1,
                "guild_id": g["id"],
                "name": g.get("name", "???"),
                "level": g.get("level", 1),
                "members": member_count,
                "territories": territories,
                "score": guild_score,
                "is_yours": g["id"] == current_user.get("guild_id"),
            })
        ranking.sort(key=lambda x: x["score"], reverse=True)
        for i, r in enumerate(ranking):
            r["rank"] = i + 1
        my_guild = next((r for r in ranking if r.get("is_yours")), None)
        return {"type": "guild", "title": "Classifica Gilde", "ranking": ranking, "my_guild": my_guild}
