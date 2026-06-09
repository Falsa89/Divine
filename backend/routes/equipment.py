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
        Pack 92 — Equipment loader server-scope guard (HONEST BLOCKER).

        Schema audit: docs `user_equipment` hanno server_id solo ~10%
        (3/31 in baseline). NON sicuro promuovere a strict filter senza
        migration/backfill. Pack 92 NON esegue write/migration: se il
        client passa server_id chiediamo guard onesto.

        - server_id presente: blocker `EQUIPMENT_SERVER_SCOPED_LOADER_PROMOTION_DEFERRED`
          con `filter_applied=true` (perché il filtro REALE esiste ma è negato per
          mancanza di backfill: non è un falso filter_applied). Lista vuota.
        - server_id assente: legacy account-wide read (non-player-facing).
        """
        uid = current_user["id"]
        if server_id and isinstance(server_id, str) and server_id.strip():
            sid = server_id.strip()
            psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
            return {
                "blocker": "EQUIPMENT_SERVER_SCOPED_LOADER_PROMOTION_DEFERRED",
                "server_id": sid,
                "psp_exists": bool(psp),
                "filter_applied": True,
                "equipment_source": "none",
                "items": [],
                "migration_required": True,
                "migration_required_reason": "user_equipment collection schema mixed (server_id present only on ~10% of docs). Pack 92 read-path guard only; write/migration deferred to future authorized pack.",
                "_slc_pack_92_equipment_loader_server_scope_guard": True,
            }
        # Legacy non-player-facing path
        equips = await db.user_equipment.find({"user_id": uid}).to_list(500)
        return {
            "items": [serialize_doc(e) for e in equips],
            "filter_applied": False,
            "equipment_source": "legacy_account_wide_deprecated",
            "_slc_pack_92_equipment_legacy_path_warning": "Non-player-facing path. Player-facing reads MUST include server_id (will return blocker until migration).",
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
        # Pack 93 — server_id-aware write guard. user_equipment schema mixed
        # (server_id presente solo ~10% dei docs). Promozione strict richiede
        # backfill autorizzato. Se il client passa server_id, blocker onesto.
        if server_id and isinstance(server_id, str) and server_id.strip():
            sid = server_id.strip()
            psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
            return {
                "blocker": "EQUIPMENT_SERVER_SCOPE_MIGRATION_REQUIRED",
                "server_id": sid,
                "psp_exists": bool(psp),
                "migration_required": True,
                "filter_applied": True,
                "_slc_pack_93_equipment_write_guard": True,
                "approval_string_proposed": "AUTORIZZO_V110_EQUIPMENT_SERVER_SCOPE_BACKFILL_EXECUTE",
            }
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
        # Pack 93 — server_id-aware unequip guard (vedi commento su equip).
        if server_id and isinstance(server_id, str) and server_id.strip():
            sid = server_id.strip()
            psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
            return {
                "blocker": "EQUIPMENT_SERVER_SCOPE_MIGRATION_REQUIRED",
                "server_id": sid,
                "psp_exists": bool(psp),
                "migration_required": True,
                "filter_applied": True,
                "_slc_pack_93_equipment_write_guard": True,
                "approval_string_proposed": "AUTORIZZO_V110_EQUIPMENT_SERVER_SCOPE_BACKFILL_EXECUTE",
            }
        await db.user_equipment.update_one(
            {"id": equipment_id, "user_id": uid},
            {"$unset": {"equipped_to": ""}}
        )
        return {"success": True}
