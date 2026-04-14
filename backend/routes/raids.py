"""
Divine Waifus - Raid & Exclusive Items Routes
"""
import random
import uuid
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from .game_data import RAID_BOSSES, EXCLUSIVE_ITEMS


def register_raids_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    @router.get("/raids")
    async def get_raids(current_user: dict = Depends(get_current_user)):
        active_raids = await db.active_raids.find({}).to_list(20)
        raids_info = []
        for raid in active_raids:
            boss = next((b for b in RAID_BOSSES if b["id"] == raid.get("boss_id")), None)
            if boss:
                participants = await db.users.find({"id": {"$in": raid.get("participants", [])}}).to_list(5)
                raids_info.append({
                    **raid, "_id": str(raid.get("_id", "")),
                    "boss": boss,
                    "participant_names": [p.get("username", "?") for p in participants],
                    "current_hp": raid.get("current_hp", boss["hp"]),
                    "total_damage": raid.get("total_damage", 0),
                    "is_participant": current_user["id"] in raid.get("participants", []),
                })
        return {"bosses": RAID_BOSSES, "active_raids": raids_info}

    class CreateRaidRequest(BaseModel):
        boss_id: str

    @router.post("/raid/create")
    async def create_raid(req: CreateRaidRequest, current_user: dict = Depends(get_current_user)):
        boss = next((b for b in RAID_BOSSES if b["id"] == req.boss_id), None)
        if not boss:
            raise HTTPException(404, "Boss non trovato")
        uid = current_user["id"]
        existing = await db.active_raids.find_one({"boss_id": req.boss_id, "status": "active"})
        if existing and uid in existing.get("participants", []):
            raise HTTPException(400, "Sei gia in questo raid!")
        if existing:
            if len(existing.get("participants", [])) >= boss["max_players"]:
                raise HTTPException(400, "Raid pieno!")
            await db.active_raids.update_one({"_id": existing["_id"]}, {"$push": {"participants": uid}})
            return {"success": True, "action": "joined", "raid_id": str(existing["_id"])}
        raid = {
            "id": str(uuid.uuid4()), "boss_id": req.boss_id, "status": "active",
            "participants": [uid], "current_hp": boss["hp"], "total_damage": 0,
            "damage_by_player": {}, "created_at": datetime.utcnow(),
        }
        await db.active_raids.insert_one(raid)
        return {"success": True, "action": "created", "raid_id": raid["id"]}

    @router.post("/raid/attack/{boss_id}")
    async def attack_raid_boss(boss_id: str, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        boss = next((b for b in RAID_BOSSES if b["id"] == boss_id), None)
        if not boss:
            raise HTTPException(404, "Boss non trovato")
        raid = await db.active_raids.find_one({"boss_id": boss_id, "status": "active"})
        if not raid:
            raise HTTPException(404, "Nessun raid attivo per questo boss")
        if uid not in raid.get("participants", []):
            raise HTTPException(400, "Non sei in questo raid! Unisciti prima.")
        user = await db.users.find_one({"id": uid})
        if user.get("stamina", 0) < 10:
            raise HTTPException(400, "Stamina insufficiente! (10 richiesti)")
        await db.users.update_one({"id": uid}, {"$inc": {"stamina": -10}})
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        team_power = team.get("total_power", 5000) if team else 5000
        element_bonus = 1.0
        damage = int(team_power * random.uniform(0.8, 1.5) * element_bonus)
        new_hp = max(0, raid.get("current_hp", boss["hp"]) - damage)
        player_dmg = raid.get("damage_by_player", {})
        player_dmg[uid] = player_dmg.get(uid, 0) + damage
        update = {"$set": {"current_hp": new_hp, "damage_by_player": player_dmg}, "$inc": {"total_damage": damage}}
        victory = new_hp <= 0
        if victory:
            update["$set"]["status"] = "completed"
            update["$set"]["completed_at"] = datetime.utcnow()
            for pid in raid.get("participants", []):
                pdmg = player_dmg.get(pid, 0)
                contribution = pdmg / max(1, raid.get("total_damage", 1) + damage)
                rewards_mult = max(0.5, min(2.0, contribution * len(raid["participants"])))
                rewards = {
                    "gold": int(boss["reward_gold"] * rewards_mult),
                    "gems": int(boss["reward_gems"] * rewards_mult),
                    "exp": int(boss["reward_exp"] * rewards_mult),
                }
                await db.users.update_one({"id": pid}, {"$inc": {"gold": rewards["gold"], "gems": rewards["gems"], "experience": rewards["exp"]}})
        await db.active_raids.update_one({"_id": raid["_id"]}, update)
        return {
            "damage_dealt": damage, "boss_hp_remaining": new_hp,
            "victory": victory, "your_total_damage": player_dmg.get(uid, 0),
            "boss_name": boss["name"],
        }

    # ==================== CHARACTER-EXCLUSIVE ITEMS ====================
    @router.get("/exclusive-items")
    async def get_exclusive_items(current_user: dict = Depends(get_current_user)):
        user_heroes = await db.user_heroes.find({"user_id": current_user["id"]}).to_list(200)
        hero_ids = [uh["hero_id"] for uh in user_heroes]
        heroes = await db.heroes.find({"id": {"$in": hero_ids}}).to_list(200)
        hero_names = [h["name"] for h in heroes]
        user_equips = await db.user_equipment.find({"user_id": current_user["id"]}).to_list(500)
        owned_names = [e["name"] for e in user_equips]
        result = []
        for ei in EXCLUSIVE_ITEMS:
            result.append({
                **ei,
                "hero_owned": ei["hero_name"] in hero_names,
                "item_owned": ei["item"]["name"] in owned_names,
            })
        return result

    class CraftExclusiveRequest(BaseModel):
        hero_name: str

    @router.post("/exclusive-items/craft")
    async def craft_exclusive_item(req: CraftExclusiveRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        ei = next((e for e in EXCLUSIVE_ITEMS if e["hero_name"] == req.hero_name), None)
        if not ei:
            raise HTTPException(404, "Oggetto esclusivo non trovato per questo eroe")
        user_heroes = await db.user_heroes.find({"user_id": uid}).to_list(200)
        hero_ids = [uh["hero_id"] for uh in user_heroes]
        heroes = await db.heroes.find({"id": {"$in": hero_ids}}).to_list(200)
        if req.hero_name not in [h["name"] for h in heroes]:
            raise HTTPException(400, f"Non possiedi {req.hero_name}!")
        existing = await db.user_equipment.find_one({"user_id": uid, "name": ei["item"]["name"]})
        if existing:
            raise HTTPException(400, "Gia posseduto!")
        cost_gold = 20000 if ei["item"]["rarity"] == 5 else 50000
        cost_gems = 50 if ei["item"]["rarity"] == 5 else 150
        user = await db.users.find_one({"id": uid})
        if user.get("gold", 0) < cost_gold or user.get("gems", 0) < cost_gems:
            raise HTTPException(400, f"Servono {cost_gold} oro e {cost_gems} gemme!")
        await db.users.update_one({"id": uid}, {"$inc": {"gold": -cost_gold, "gems": -cost_gems}})
        equip = {
            "id": str(uuid.uuid4()), "user_id": uid,
            "name": ei["item"]["name"], "slot": ei["item"]["slot"],
            "rarity": ei["item"]["rarity"], "stats": ei["item"]["stats"],
            "level": 1, "is_exclusive": True, "exclusive_hero": req.hero_name,
            "description": ei["item"].get("description", ""),
            "obtained_at": datetime.utcnow(),
        }
        await db.user_equipment.insert_one(equip)
        return {"success": True, "item": equip}
