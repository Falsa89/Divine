"""
Divine Waifus - Guild & Faction Routes
"""
import uuid
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from .game_data import FACTIONS, FACTION_CHANGE_COST


def register_guild_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    class GuildCreateRequest(BaseModel):
        name: str

    @router.post("/guild/create")
    async def create_guild(req: GuildCreateRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        if current_user.get("guild_id"):
            raise HTTPException(400, "Sei gia in una gilda!")
        existing = await db.guilds.find_one({"name": req.name})
        if existing:
            raise HTTPException(400, "Nome gilda gia in uso!")
        guild = {
            "id": str(uuid.uuid4()), "name": req.name, "leader_id": uid,
            "members": [uid], "level": 1, "exp": 0, "created_at": datetime.utcnow(),
        }
        await db.guilds.insert_one(guild)
        await db.users.update_one({"id": uid}, {"$set": {"guild_id": guild["id"]}})
        return serialize_doc(guild)

    @router.get("/guild/info")
    async def get_guild_info(current_user: dict = Depends(get_current_user)):
        guild_id = current_user.get("guild_id")
        if not guild_id:
            return {"guild": None, "available_guilds": await get_available_guilds()}
        guild = await db.guilds.find_one({"id": guild_id})
        if not guild:
            return {"guild": None, "available_guilds": await get_available_guilds()}
        members = []
        for mid in guild.get("members", []):
            u = await db.users.find_one({"id": mid})
            if u:
                members.append({"id": mid, "username": u.get("username", "???"), "level": u.get("level", 1)})
        guild["member_details"] = members
        return {"guild": serialize_doc(guild)}

    async def get_available_guilds():
        guilds = await db.guilds.find({}).limit(20).to_list(20)
        return [{"id": g["id"], "name": g["name"], "members": len(g.get("members", [])), "level": g.get("level", 1)} for g in guilds]

    @router.post("/guild/join/{guild_id}")
    async def join_guild(guild_id: str, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        if current_user.get("guild_id"):
            raise HTTPException(400, "Sei gia in una gilda!")
        guild = await db.guilds.find_one({"id": guild_id})
        if not guild:
            raise HTTPException(404, "Gilda non trovata")
        if len(guild.get("members", [])) >= 30:
            raise HTTPException(400, "Gilda piena!")
        await db.guilds.update_one({"id": guild_id}, {"$push": {"members": uid}})
        await db.users.update_one({"id": uid}, {"$set": {"guild_id": guild_id}})
        return {"success": True}

    @router.post("/guild/leave")
    async def leave_guild(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        guild_id = current_user.get("guild_id")
        if not guild_id:
            raise HTTPException(400, "Non sei in una gilda!")
        await db.guilds.update_one({"id": guild_id}, {"$pull": {"members": uid}})
        await db.users.update_one({"id": uid}, {"$set": {"guild_id": None}})
        return {"success": True}

    # ==================== FACTIONS (permanent choice) ====================
    @router.get("/factions")
    async def get_factions(current_user: dict = Depends(get_current_user)):
        user_faction = current_user.get("faction")
        faction_locked = current_user.get("faction_locked", False)
        # Calculate active buff
        active_buff = {}
        if user_faction:
            f = next((x for x in FACTIONS if x["id"] == user_faction), None)
            if f:
                active_buff = f["bonus"]
        return {
            "factions": FACTIONS,
            "user_faction": user_faction,
            "faction_locked": faction_locked,
            "active_buff": active_buff,
            "change_cost": FACTION_CHANGE_COST,
        }

    class FactionJoinRequest(BaseModel):
        faction_id: str

    @router.post("/faction/join")
    async def join_faction(req: FactionJoinRequest, current_user: dict = Depends(get_current_user)):
        """Choose faction - first time is free, afterwards costs premium gems."""
        faction = next((f for f in FACTIONS if f["id"] == req.faction_id), None)
        if not faction:
            raise HTTPException(404, "Fazione non trovata")
        uid = current_user["id"]
        has_faction = current_user.get("faction") is not None
        faction_locked = current_user.get("faction_locked", False)

        if has_faction and faction_locked:
            # Must pay premium gems to change
            user = await db.users.find_one({"id": uid})
            if user.get("gems", 0) < FACTION_CHANGE_COST:
                raise HTTPException(400, f"Servono {FACTION_CHANGE_COST} gemme premium per cambiare fazione!")
            await db.users.update_one({"id": uid}, {"$inc": {"gems": -FACTION_CHANGE_COST}})

        await db.users.update_one({"id": uid}, {"$set": {"faction": req.faction_id, "faction_locked": True}})
        return {"success": True, "faction": faction, "locked": True}
