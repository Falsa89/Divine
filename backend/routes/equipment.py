"""
Divine Waifus - Equipment & Fusion Routes
"""
import uuid
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from .game_data import EQUIPMENT_TEMPLATES

# v108_POSTQA_D: legacy mutation gate (default-OFF) per /api/equipment/equip
# PUBLIC_SYNC_TAG_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS
from utils.postqa_d_mutation_gate import make_legacy_mutation_gate_dep


def register_equipment_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    @router.get("/equipment/templates")
    async def get_equipment_templates():
        return EQUIPMENT_TEMPLATES

    @router.get("/user/equipment")
    async def get_user_equipment(server_id: str = None, current_user: dict = Depends(get_current_user)):
        """
        Pack 94 — Equipment loader STRICT server-scoped (post-backfill 100% coverage).

        - server_id presente: read REALE filtrato per (user_id, server_id) con
          PSP existence check. filter_applied=true.
        - server_id assente: legacy account-wide path (non-player-facing).
        """
        uid = current_user["id"]
        if not server_id or not isinstance(server_id, str) or not server_id.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "blocker": "SERVER_ID_REQUIRED_FOR_GAMEPLAY_STATE",
                    "route": "/api/user/equipment",
                    "message": "server_id is required for server-bound equipment reads.",
                },
            )
        if server_id and isinstance(server_id, str) and server_id.strip():
            sid = server_id.strip()
            psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
            if not psp:
                return {
                    "blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
                    "server_id": sid,
                    "filter_applied": True,
                    "equipment_source": "none",
                    "items": [],
                    "_slc_pack_94_equipment_loader_strict": True,
                }
            equips = await db.user_equipment.find({"user_id": uid, "server_id": sid}).to_list(500)
            return {
                "server_id": sid,
                "filter_applied": True,
                "equipment_source": "psp_server_scoped",
                "items": [serialize_doc(e) for e in equips],
                "_slc_pack_94_equipment_loader_strict": True,
            }
        # Legacy non-player-facing path
        equips = await db.user_equipment.find({"user_id": uid}).to_list(500)
        return {
            "items": [serialize_doc(e) for e in equips],
            "filter_applied": False,
            "equipment_source": "legacy_account_wide_deprecated",
            "_slc_pack_92_equipment_legacy_path_warning": "Non-player-facing path. Player-facing reads MUST include server_id.",
        }

    class EquipRequest(BaseModel):
        equipment_id: str
        user_hero_id: str

    @router.post(
        "/equipment/equip",
        dependencies=[
            Depends(
                make_legacy_mutation_gate_dep(
                    "DIVINE_ALLOW_LEGACY_EQUIPMENT_MUTATIONS",
                    "/api/equipment/equip",
                )
            )
        ],
    )
    async def equip_item(req: EquipRequest, server_id: str = None, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        # Pack 94 — STRICT server-scoped write path (post-backfill 100% coverage).
        if server_id and isinstance(server_id, str) and server_id.strip():
            sid = server_id.strip()
            psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
            if not psp:
                raise HTTPException(409, "PLAYER_SERVER_PROFILE_REQUIRED")
            equip = await db.user_equipment.find_one({"id": req.equipment_id, "user_id": uid, "server_id": sid})
            if not equip:
                raise HTTPException(404, "Equipaggiamento non trovato per questo server")
            hero = await db.user_heroes.find_one({"id": req.user_hero_id, "user_id": uid, "server_id": sid})
            if not hero:
                raise HTTPException(404, "Eroe non trovato per questo server")
            if equip.get("equipped_to"):
                await db.user_equipment.update_one({"id": req.equipment_id, "user_id": uid, "server_id": sid}, {"$unset": {"equipped_to": ""}})
            slot = equip.get("slot", "weapon")
            existing = await db.user_equipment.find_one({"user_id": uid, "server_id": sid, "equipped_to": req.user_hero_id, "slot": slot})
            if existing:
                await db.user_equipment.update_one({"id": existing["id"], "user_id": uid, "server_id": sid}, {"$unset": {"equipped_to": ""}})
            await db.user_equipment.update_one({"id": req.equipment_id, "user_id": uid, "server_id": sid}, {"$set": {"equipped_to": req.user_hero_id, "_slc_pack_94_equipment_strict_write": True}})
            return {"success": True, "server_id": sid, "pack_94_strict_server_scoped_write": True}
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
    async def unequip_item(equipment_id: str, server_id: str = None, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        # Pack 94 — STRICT server-scoped unequip (post-backfill).
        if server_id and isinstance(server_id, str) and server_id.strip():
            sid = server_id.strip()
            psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
            if not psp:
                raise HTTPException(409, "PLAYER_SERVER_PROFILE_REQUIRED")
            r = await db.user_equipment.update_one(
                {"id": equipment_id, "user_id": uid, "server_id": sid},
                {"$unset": {"equipped_to": ""}, "$set": {"_slc_pack_94_equipment_strict_unequip": True}},
            )
            if r.matched_count == 0:
                raise HTTPException(404, "Equipaggiamento non trovato per questo server")
            return {"success": True, "server_id": sid, "pack_94_strict_server_scoped_write": True}
        # Pre-QA Stabilization 115B — legacy no-server-id path fail-closed.
        # In assenza di server_id, l'unequip account-wide e' una mutazione legacy
        # non autorizzata in pre-QA. Restituiamo 423 esplicito senza side-effect.
        raise HTTPException(
            423,
            {
                "code": "LEGACY_UNEQUIP_NO_SERVER_ID_FAIL_CLOSED",
                "pack_origin": "pre_qa_stabilization_115b",
                "endpoint": "/api/equipment/unequip/{equipment_id}",
                "reason": "Legacy account-wide unequip path is fail-closed in pre-QA. Provide server_id query param to use the strict server-scoped path.",
                "no_db_write": True,
                "strict_path_available": True,
            },
        )
