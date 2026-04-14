"""
Divine Waifus - Level Sharing System (Hokage Crisis style)
Top 6 heroes by level share their level with heroes in unlockable slots.
Heroes in slots gain the shared level without needing to level up themselves.
"""
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel

# Slot unlock costs
LEVEL_SHARE_SLOTS = [
    {"slot": 1, "cost_gold": 50000, "cost_gems": 0, "description": "Primo slot condivisione livello"},
    {"slot": 2, "cost_gold": 100000, "cost_gems": 50, "description": "Secondo slot"},
    {"slot": 3, "cost_gold": 200000, "cost_gems": 100, "description": "Terzo slot"},
    {"slot": 4, "cost_gold": 500000, "cost_gems": 200, "description": "Quarto slot"},
    {"slot": 5, "cost_gold": 1000000, "cost_gems": 500, "description": "Quinto slot"},
    {"slot": 6, "cost_gold": 2000000, "cost_gems": 1000, "description": "Sesto slot"},
    {"slot": 7, "cost_gold": 5000000, "cost_gems": 2000, "description": "Settimo slot"},
    {"slot": 8, "cost_gold": 10000000, "cost_gems": 3000, "description": "Ottavo slot - Massimo"},
]


def register_level_sharing_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    @router.get("/level-sharing")
    async def get_level_sharing(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]

        # Get top 6 heroes by level
        all_heroes = await db.user_heroes.find({"user_id": uid}).sort("level", -1).to_list(500)
        top6 = all_heroes[:6]
        top6_ids = [h["id"] for h in top6]

        # Calculate shared level (average of top 6, rounded down)
        if top6:
            shared_level = sum(h.get("level", 1) for h in top6) // len(top6)
        else:
            shared_level = 1

        # Get hero details for top 6
        top6_details = []
        for uh in top6:
            hero = await db.heroes.find_one({"id": uh["hero_id"]})
            top6_details.append({
                "user_hero_id": uh["id"],
                "hero_name": hero.get("name", "?") if hero else "?",
                "level": uh.get("level", 1),
                "stars": uh.get("stars", 1),
                "hero_class": hero.get("hero_class", "?") if hero else "?",
                "image": hero.get("image_url") if hero else None,
            })

        # Get unlocked slots
        sharing_data = await db.level_sharing.find_one({"user_id": uid})
        if not sharing_data:
            sharing_data = {"user_id": uid, "unlocked_slots": 0, "assigned_heroes": {}}
            await db.level_sharing.insert_one(sharing_data)

        unlocked = sharing_data.get("unlocked_slots", 0)
        assigned = sharing_data.get("assigned_heroes", {})

        # Build slot details
        slots = []
        for slot_info in LEVEL_SHARE_SLOTS:
            sn = str(slot_info["slot"])
            is_unlocked = slot_info["slot"] <= unlocked
            hero_id = assigned.get(sn)
            hero_detail = None
            if hero_id and is_unlocked:
                uh = await db.user_heroes.find_one({"id": hero_id, "user_id": uid})
                if uh:
                    hero = await db.heroes.find_one({"id": uh["hero_id"]})
                    hero_detail = {
                        "user_hero_id": uh["id"],
                        "hero_name": hero.get("name", "?") if hero else "?",
                        "original_level": uh.get("level", 1),
                        "shared_level": shared_level,
                        "level_bonus": max(0, shared_level - uh.get("level", 1)),
                        "image": hero.get("image_url") if hero else None,
                    }
            slots.append({
                **slot_info,
                "unlocked": is_unlocked,
                "hero": hero_detail,
            })

        return {
            "shared_level": shared_level,
            "top6": top6_details,
            "slots": slots,
            "unlocked_slots": unlocked,
            "max_slots": len(LEVEL_SHARE_SLOTS),
        }

    class UnlockSlotRequest(BaseModel):
        slot_number: int

    @router.post("/level-sharing/unlock")
    async def unlock_slot(req: UnlockSlotRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        slot_info = next((s for s in LEVEL_SHARE_SLOTS if s["slot"] == req.slot_number), None)
        if not slot_info:
            raise HTTPException(404, "Slot non valido")

        sharing = await db.level_sharing.find_one({"user_id": uid})
        if not sharing:
            sharing = {"user_id": uid, "unlocked_slots": 0, "assigned_heroes": {}}
            await db.level_sharing.insert_one(sharing)

        if sharing.get("unlocked_slots", 0) >= req.slot_number:
            raise HTTPException(400, "Slot gia sbloccato!")
        if sharing.get("unlocked_slots", 0) + 1 != req.slot_number:
            raise HTTPException(400, "Devi sbloccare gli slot in ordine!")

        # Check cost
        user = await db.users.find_one({"id": uid})
        if user.get("gold", 0) < slot_info["cost_gold"]:
            raise HTTPException(400, f"Servono {slot_info['cost_gold']:,} oro!")
        if user.get("gems", 0) < slot_info["cost_gems"]:
            raise HTTPException(400, f"Servono {slot_info['cost_gems']} gemme!")

        await db.users.update_one({"id": uid}, {"$inc": {"gold": -slot_info["cost_gold"], "gems": -slot_info["cost_gems"]}})
        await db.level_sharing.update_one({"user_id": uid}, {"$set": {"unlocked_slots": req.slot_number}})

        return {"success": True, "slot": req.slot_number, "cost_gold": slot_info["cost_gold"], "cost_gems": slot_info["cost_gems"]}

    class AssignHeroRequest(BaseModel):
        slot_number: int
        user_hero_id: str

    @router.post("/level-sharing/assign")
    async def assign_hero_to_slot(req: AssignHeroRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        sharing = await db.level_sharing.find_one({"user_id": uid})
        if not sharing or sharing.get("unlocked_slots", 0) < req.slot_number:
            raise HTTPException(400, "Slot non sbloccato!")

        uh = await db.user_heroes.find_one({"id": req.user_hero_id, "user_id": uid})
        if not uh:
            raise HTTPException(404, "Eroe non trovato")

        # Can't assign a top-6 hero (they're already sharing)
        all_heroes = await db.user_heroes.find({"user_id": uid}).sort("level", -1).to_list(6)
        top6_ids = [h["id"] for h in all_heroes[:6]]
        if req.user_hero_id in top6_ids:
            raise HTTPException(400, "Questo eroe e gia nei Top 6! Non serve assegnarlo.")

        # Check not already in another slot
        assigned = sharing.get("assigned_heroes", {})
        for sn, hid in assigned.items():
            if hid == req.user_hero_id and sn != str(req.slot_number):
                raise HTTPException(400, "Eroe gia assegnato ad un altro slot!")

        assigned[str(req.slot_number)] = req.user_hero_id
        await db.level_sharing.update_one({"user_id": uid}, {"$set": {"assigned_heroes": assigned}})

        hero = await db.heroes.find_one({"id": uh["hero_id"]})
        return {
            "success": True,
            "hero_name": hero.get("name", "?") if hero else "?",
            "slot": req.slot_number,
        }

    @router.post("/level-sharing/remove/{slot_number}")
    async def remove_hero_from_slot(slot_number: int, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        sharing = await db.level_sharing.find_one({"user_id": uid})
        if not sharing:
            raise HTTPException(400, "Nessun dato condivisione")
        assigned = sharing.get("assigned_heroes", {})
        sn = str(slot_number)
        if sn not in assigned:
            raise HTTPException(400, "Slot vuoto")
        del assigned[sn]
        await db.level_sharing.update_one({"user_id": uid}, {"$set": {"assigned_heroes": assigned}})
        return {"success": True, "slot": slot_number}
