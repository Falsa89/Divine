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
