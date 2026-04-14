"""
Divine Waifus - Cosmetics & Territory Conquest Routes
"""
import random
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from .game_data import AURAS, AVATAR_FRAMES, TERRITORIES


def register_cosmetics_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    @router.get("/cosmetics")
    async def get_cosmetics(current_user: dict = Depends(get_current_user)):
        user_cosmetics = await db.user_cosmetics.find_one({"user_id": current_user["id"]})
        if not user_cosmetics:
            user_cosmetics = {"user_id": current_user["id"], "owned_auras": [], "owned_frames": ["bronze"], "active_aura": None, "active_frame": "bronze"}
            await db.user_cosmetics.insert_one(user_cosmetics)
        return {
            "auras": AURAS, "frames": AVATAR_FRAMES,
            "owned_auras": user_cosmetics.get("owned_auras", []),
            "owned_frames": user_cosmetics.get("owned_frames", ["bronze"]),
            "active_aura": user_cosmetics.get("active_aura"),
            "active_frame": user_cosmetics.get("active_frame", "bronze"),
        }

    class BuyCosmeticRequest(BaseModel):
        type: str
        item_id: str

    @router.post("/cosmetics/buy")
    async def buy_cosmetic(req: BuyCosmeticRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        items = AURAS if req.type == "aura" else AVATAR_FRAMES
        item = next((i for i in items if i["id"] == req.item_id), None)
        if not item:
            raise HTTPException(404, "Oggetto non trovato")
        user_cosmetics = await db.user_cosmetics.find_one({"user_id": uid})
        if not user_cosmetics:
            user_cosmetics = {"user_id": uid, "owned_auras": [], "owned_frames": ["bronze"]}
            await db.user_cosmetics.insert_one(user_cosmetics)
        owned_key = "owned_auras" if req.type == "aura" else "owned_frames"
        if req.item_id in user_cosmetics.get(owned_key, []):
            raise HTTPException(400, "Gia posseduto!")
        user = await db.users.find_one({"id": uid})
        currency_field = "gems" if item["currency"] == "gems" else "gold"
        if user.get(currency_field, 0) < item["cost"]:
            raise HTTPException(400, f"{'Gemme' if currency_field == 'gems' else 'Oro'} insufficiente!")
        await db.users.update_one({"id": uid}, {"$inc": {currency_field: -item["cost"]}})
        await db.user_cosmetics.update_one({"user_id": uid}, {"$push": {owned_key: req.item_id}}, upsert=True)
        return {"success": True, "item": item}

    class SetCosmeticRequest(BaseModel):
        type: str
        item_id: str

    @router.post("/cosmetics/equip")
    async def equip_cosmetic(req: SetCosmeticRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        field = "active_aura" if req.type == "aura" else "active_frame"
        await db.user_cosmetics.update_one({"user_id": uid}, {"$set": {field: req.item_id}}, upsert=True)
        return {"success": True}

    # ==================== TERRITORY CONQUEST ====================
    class TerritoryAttackRequest(BaseModel):
        territory_id: str

    @router.get("/territory/map")
    async def get_territory_map(current_user: dict = Depends(get_current_user)):
        territories = []
        for t in TERRITORIES:
            control = await db.territory_control.find_one({"territory_id": t["id"]})
            guild_name = None
            if control and control.get("guild_id"):
                guild = await db.guilds.find_one({"id": control["guild_id"]})
                guild_name = guild.get("name") if guild else None
            territories.append({
                **t,
                "controlled_by": guild_name,
                "controlled_guild_id": control.get("guild_id") if control else None,
                "defense_power": control.get("defense_power", 0) if control else 0,
            })
        return {"territories": territories}

    @router.post("/territory/attack")
    async def attack_territory(req: TerritoryAttackRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        guild_id = current_user.get("guild_id")
        if not guild_id:
            raise HTTPException(400, "Devi essere in una gilda per conquistare territori!")
        territory = next((t for t in TERRITORIES if t["id"] == req.territory_id), None)
        if not territory:
            raise HTTPException(404, "Territorio non trovato")
        user = await db.users.find_one({"id": uid})
        if user.get("stamina", 0) < 15:
            raise HTTPException(400, "Stamina insufficiente! (15 richiesti)")
        await db.users.update_one({"id": uid}, {"$inc": {"stamina": -15}})
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        atk_power = team.get("total_power", 5000) if team else 5000
        control = await db.territory_control.find_one({"territory_id": req.territory_id})
        def_power = control.get("defense_power", 0) if control else 0
        is_own = control and control.get("guild_id") == guild_id
        if is_own:
            await db.territory_control.update_one({"territory_id": req.territory_id}, {"$inc": {"defense_power": atk_power // 3}})
            return {"action": "reinforce", "territory": territory["name"], "added_defense": atk_power // 3}
        victory = atk_power * random.uniform(0.7, 1.3) > def_power * random.uniform(0.5, 1.0) if def_power > 0 else True
        if victory:
            await db.territory_control.update_one(
                {"territory_id": req.territory_id},
                {"$set": {"guild_id": guild_id, "defense_power": atk_power // 2, "captured_at": datetime.utcnow(), "captured_by": uid}},
                upsert=True
            )
            rewards = {"gold": territory["reward_gold"], "gems": territory["reward_gems"]}
            await db.users.update_one({"id": uid}, {"$inc": {"gold": rewards["gold"], "gems": rewards["gems"]}})
            return {"victory": True, "territory": territory["name"], "rewards": rewards}
        return {"victory": False, "territory": territory["name"], "enemy_defense": def_power}
