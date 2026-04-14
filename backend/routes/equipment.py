"""
Divine Waifus - Equipment & Fusion Routes
"""
import uuid
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from .game_data import EQUIPMENT_TEMPLATES


def register_equipment_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    @router.get("/equipment/templates")
    async def get_equipment_templates():
        return EQUIPMENT_TEMPLATES

    @router.get("/user/equipment")
    async def get_user_equipment(current_user: dict = Depends(get_current_user)):
        equips = await db.user_equipment.find({"user_id": current_user["id"]}).to_list(500)
        return [serialize_doc(e) for e in equips]

    class EquipRequest(BaseModel):
        equipment_id: str
        user_hero_id: str

    @router.post("/equipment/equip")
    async def equip_item(req: EquipRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        equip = await db.user_equipment.find_one({"id": req.equipment_id, "user_id": uid})
        if not equip:
            raise HTTPException(404, "Equipaggiamento non trovato")
        hero = await db.user_heroes.find_one({"id": req.user_hero_id, "user_id": uid})
        if not hero:
            raise HTTPException(404, "Eroe non trovato")
        if equip.get("equipped_to"):
            await db.user_equipment.update_one({"id": req.equipment_id}, {"$unset": {"equipped_to": ""}})
        slot = equip.get("slot", "weapon")
        existing = await db.user_equipment.find_one({"user_id": uid, "equipped_to": req.user_hero_id, "slot": slot})
        if existing:
            await db.user_equipment.update_one({"id": existing["id"]}, {"$unset": {"equipped_to": ""}})
        await db.user_equipment.update_one({"id": req.equipment_id}, {"$set": {"equipped_to": req.user_hero_id}})
        return {"success": True}

    @router.post("/equipment/unequip/{equipment_id}")
    async def unequip_item(equipment_id: str, current_user: dict = Depends(get_current_user)):
        await db.user_equipment.update_one(
            {"id": equipment_id, "user_id": current_user["id"]},
            {"$unset": {"equipped_to": ""}}
        )
        return {"success": True}

    # ==================== FUSION ====================
    class FusionRequest(BaseModel):
        base_hero_id: str
        fodder_hero_ids: list

    @router.post("/fusion/merge")
    async def fuse_heroes(req: FusionRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        base = await db.user_heroes.find_one({"id": req.base_hero_id, "user_id": uid})
        if not base:
            raise HTTPException(404, "Eroe base non trovato")
        if len(req.fodder_hero_ids) == 0:
            raise HTTPException(400, "Seleziona almeno un eroe da sacrificare")
        exp_gain = 0
        star_ups = 0
        for fid in req.fodder_hero_ids:
            if fid == req.base_hero_id:
                raise HTTPException(400, "Non puoi sacrificare l'eroe base!")
            fodder = await db.user_heroes.find_one({"id": fid, "user_id": uid})
            if not fodder:
                raise HTTPException(404, f"Eroe sacrificale {fid} non trovato")
            if fodder.get("hero_id") == base.get("hero_id"):
                star_ups += 1
            else:
                fodder_hero = await db.heroes.find_one({"id": fodder["hero_id"]})
                exp_gain += (fodder_hero.get("rarity", 1) * 100 + fodder.get("level", 1) * 50) if fodder_hero else 100
            await db.user_heroes.delete_one({"id": fid, "user_id": uid})
        new_stars = min(6, base.get("stars", 1) + star_ups)
        new_level = base.get("level", 1)
        new_exp = base.get("experience", 0) + exp_gain
        while new_exp >= new_level * 100 and new_level < 100:
            new_exp -= new_level * 100
            new_level += 1
        await db.user_heroes.update_one({"id": req.base_hero_id}, {"$set": {
            "stars": new_stars, "level": new_level, "experience": new_exp
        }})
        return {
            "success": True,
            "new_stars": new_stars,
            "new_level": new_level,
            "exp_gained": exp_gain,
            "star_ups": star_ups,
        }
