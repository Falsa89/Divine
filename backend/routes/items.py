"""
Divine Waifus - Items & Skill Upgrade Routes
EXP potions, skill materials, and hero skill upgrades
"""
import uuid
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

# SLC-F Batch-1B: server/account scope helper (set-only-if-missing on insert)
from utils.server_scope import ensure_server_scope

# Pre-QA Stabilization 115B — legacy mutation gate default-OFF su
# /api/item-shop/buy (spende users.gold/gems), /api/inventory/use-exp,
# /api/hero/skill-upgrade (spende users.gold).
# PUBLIC_SYNC_TAG_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS
from utils.postqa_d_mutation_gate import make_legacy_mutation_gate_dep
from fastapi import Depends as _Depends_postqa_d

# ============ EXP ITEMS ============
EXP_ITEMS = {
    "exp_potion_s": {"name": "Pozione EXP Piccola", "icon": "\U0001f9ea", "exp": 1000, "shop_price": 500, "currency": "gold", "rarity": 1},
    "exp_potion_m": {"name": "Pozione EXP Media", "icon": "\U0001f9ea", "exp": 5000, "shop_price": 2000, "currency": "gold", "rarity": 2},
    "exp_potion_l": {"name": "Pozione EXP Grande", "icon": "\U0001f9ea", "exp": 20000, "shop_price": 8000, "currency": "gold", "rarity": 3},
    "exp_potion_xl": {"name": "Pozione EXP Super", "icon": "\U0001f9ea", "exp": 100000, "shop_price": 30000, "currency": "gold", "rarity": 4},
    "exp_book_s": {"name": "Libro EXP Comune", "icon": "\U0001f4d5", "exp": 3000, "shop_price": 1200, "currency": "gold", "rarity": 1},
    "exp_book_m": {"name": "Libro EXP Raro", "icon": "\U0001f4d7", "exp": 15000, "shop_price": 6000, "currency": "gold", "rarity": 3},
    "exp_book_l": {"name": "Libro EXP Epico", "icon": "\U0001f4d8", "exp": 50000, "shop_price": 20000, "currency": "gold", "rarity": 4},
}

# ============ SKILL MATERIALS ============
SKILL_MATERIALS = {
    "skill_scroll_s": {"name": "Pergamena Skill Base", "icon": "\U0001f4dc", "shop_price": 1000, "currency": "gold", "rarity": 1},
    "skill_scroll_m": {"name": "Pergamena Skill Rara", "icon": "\U0001f4dc", "shop_price": 5000, "currency": "gold", "rarity": 3},
    "skill_scroll_l": {"name": "Pergamena Skill Epica", "icon": "\U0001f4dc", "shop_price": 20000, "currency": "gold", "rarity": 4},
    "skill_crystal": {"name": "Cristallo Skill", "icon": "\U0001f48e", "shop_price": 3000, "currency": "gems", "rarity": 4},
    "element_stone_fire": {"name": "Pietra Fuoco", "icon": "\U0001f525", "shop_price": 2000, "currency": "gold", "rarity": 2},
    "element_stone_water": {"name": "Pietra Acqua", "icon": "\U0001f4a7", "shop_price": 2000, "currency": "gold", "rarity": 2},
    "element_stone_earth": {"name": "Pietra Terra", "icon": "\U0001faa8", "shop_price": 2000, "currency": "gold", "rarity": 2},
    "element_stone_wind": {"name": "Pietra Vento", "icon": "\U0001f4a8", "shop_price": 2000, "currency": "gold", "rarity": 2},
    "element_stone_thunder": {"name": "Pietra Tuono", "icon": "\u26a1", "shop_price": 2000, "currency": "gold", "rarity": 2},
    "element_stone_light": {"name": "Pietra Luce", "icon": "\u2728", "shop_price": 2000, "currency": "gold", "rarity": 2},
    "element_stone_shadow": {"name": "Pietra Ombra", "icon": "\U0001f311", "shop_price": 2000, "currency": "gold", "rarity": 2},
}

# Skill upgrade costs per level
SKILL_UPGRADE_COSTS = {
    1: {"gold": 1000, "skill_scroll_s": 2},
    2: {"gold": 2500, "skill_scroll_s": 4},
    3: {"gold": 5000, "skill_scroll_m": 2},
    4: {"gold": 10000, "skill_scroll_m": 4},
    5: {"gold": 20000, "skill_scroll_l": 2},
    6: {"gold": 40000, "skill_scroll_l": 3, "skill_crystal": 1},
    7: {"gold": 80000, "skill_scroll_l": 5, "skill_crystal": 2},
    8: {"gold": 150000, "skill_scroll_l": 8, "skill_crystal": 3},
    9: {"gold": 300000, "skill_scroll_l": 10, "skill_crystal": 5},
}

# Battle drop table
BATTLE_DROPS = [
    {"item_id": "exp_potion_s", "weight": 40},
    {"item_id": "exp_potion_m", "weight": 25},
    {"item_id": "exp_potion_l", "weight": 10},
    {"item_id": "exp_book_s", "weight": 30},
    {"item_id": "exp_book_m", "weight": 12},
    {"item_id": "skill_scroll_s", "weight": 35},
    {"item_id": "skill_scroll_m", "weight": 15},
    {"item_id": "skill_scroll_l", "weight": 5},
    {"item_id": "skill_crystal", "weight": 3},
]


def register_items_routes(router, db, get_current_user):

    # ============ INVENTORY ============
    # Pack 89 — Inventory PSP-scoped loader promotion (runtime ready).
    # Decisione canonica: inventario/materiali/items operativi sono SERVER-SCOPED.
    # Con server_id presente, /api/inventory ritorna SOLO inventory del
    # (user_id, server_id) selezionato. NESSUN fallback account-wide come
    # fonte player-facing finale. NESSUNA copia S1->S2. NESSUNA DB write.
    # PSP missing -> blocker PLAYER_SERVER_PROFILE_REQUIRED.
    # Senza server_id: legacy non-player-facing path, flagged.
    @router.get("/inventory")
    async def get_inventory(
        server_id: Optional[str] = None,
        current_user: dict = Depends(get_current_user),
    ):
        user_id = current_user['id']
        base_response = {
            "pack_89_inventory_strict_server_scope": True,
            "server_id": server_id,
        }

        # ---- Pack 89 STRICT SERVER-SCOPED path ----
        if server_id:
            sid = server_id.strip() if isinstance(server_id, str) else ""
            if not sid:
                return {
                    **base_response,
                    "items": [],
                    "filter_applied": False,
                    "inventory_source": "none",
                    "legacy_account_inventory_used": False,
                    "blocker": "SERVER_ID_REQUIRED",
                }
            # PSP existence check (Pack 85/86): non auto-creare PSP qui (read-only loader)
            psp = await db.player_server_profiles.find_one(
                {"user_id": user_id, "server_id": sid}
            )
            if not psp:
                # Dual-read fallback (Pack 82) for legacy PSP with stringified ObjectId
                try:
                    user_doc = await db.users.find_one({"id": user_id})
                    if user_doc:
                        psp = await db.player_server_profiles.find_one(
                            {"user_id": str(user_doc.get("_id") or user_doc.get("id")),
                             "server_id": sid}
                        )
                except Exception:
                    psp = None
            if not psp:
                return {
                    **base_response,
                    "items": [],
                    "filter_applied": True,
                    "inventory_source": "none",
                    "legacy_account_inventory_used": False,
                    "blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
                }
            # STRICT read: only (user_id, server_id) entries. No account-wide leak.
            inv = await db.inventory.find(
                {"user_id": user_id, "server_id": sid}
            ).to_list(length=500)
            items = []
            for entry in inv:
                item_def = EXP_ITEMS.get(entry['item_id']) or SKILL_MATERIALS.get(entry['item_id'])
                if item_def:
                    items.append({
                        "item_id": entry['item_id'],
                        "quantity": entry.get('quantity', 0),
                        "server_id": sid,
                        **item_def,
                    })
            return {
                **base_response,
                "items": items,
                "filter_applied": True,
                "inventory_source": "player_server_scoped",
                "legacy_account_inventory_used": False,
                "blocker": None,
            }

        # ---- Pack 89 LEGACY/COMPAT path (no server_id, non-player-facing) ----
        # Esposto solo per tool/debug retrocompatibili. NESSUNA promessa di
        # server-scope. filter_applied=False. Marked legacy.
        inv = await db.inventory.find({"user_id": user_id}).to_list(length=500)
        items = []
        for entry in inv:
            item_def = EXP_ITEMS.get(entry['item_id']) or SKILL_MATERIALS.get(entry['item_id'])
            if item_def:
                items.append({
                    "item_id": entry['item_id'],
                    "quantity": entry.get('quantity', 0),
                    **item_def,
                })
        return {
            **base_response,
            "items": items,
            "filter_applied": False,
            "inventory_source": "legacy_account_wide_deprecated",
            "legacy_account_inventory_used": True,
            "blocker": None,
            "_slc_pack_89_legacy_path_warning": "Non-player-facing path. Player-facing reads MUST include server_id.",
        }

    # ============ ITEM SHOP ============
    @router.get("/item-shop")
    async def get_item_shop(current_user: dict = Depends(get_current_user)):
        user = await db.users.find_one({"id": current_user['id']})
        gold = user.get('gold', 0)
        gems = user.get('gems', 0)
        
        shop_items = []
        for item_id, item in {**EXP_ITEMS, **SKILL_MATERIALS}.items():
            balance = gold if item['currency'] == 'gold' else gems
            shop_items.append({
                "item_id": item_id,
                "can_afford": balance >= item['shop_price'],
                **item,
            })
        return {"items": shop_items, "gold": gold, "gems": gems}

    class BuyItemRequest(BaseModel):
        item_id: str
        quantity: int = 1

    @router.post(
        "/item-shop/buy",
        dependencies=[
            _Depends_postqa_d(
                make_legacy_mutation_gate_dep(
                    "DIVINE_ALLOW_LEGACY_ITEM_SHOP_MUTATIONS",
                    "/api/item-shop/buy",
                )
            )
        ],
    )
    async def buy_item(req: BuyItemRequest, server_id: str, current_user: dict = Depends(get_current_user)):
        # Pack 90 — STRICT server-scoped write. server_id query param REQUIRED.
        # PSP existence verificato; selector inventory include server_id;
        # nessun hardcoded "s1"; nessun fallback account-wide.
        user_id = current_user['id']
        if not server_id or not isinstance(server_id, str) or not server_id.strip():
            raise HTTPException(status_code=400, detail="SERVER_ID_REQUIRED")
        sid = server_id.strip()
        psp = await db.player_server_profiles.find_one({"user_id": user_id, "server_id": sid})
        if not psp:
            raise HTTPException(status_code=409, detail="PLAYER_SERVER_PROFILE_REQUIRED")
        item = EXP_ITEMS.get(req.item_id) or SKILL_MATERIALS.get(req.item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Oggetto non trovato")
        total_cost = item['shop_price'] * req.quantity
        user = await db.users.find_one({"id": user_id})
        currency_field = 'gold' if item['currency'] == 'gold' else 'gems'
        if user.get(currency_field, 0) < total_cost:
            raise HTTPException(status_code=400, detail=f"Non hai abbastanza {currency_field}!")
        await db.users.update_one({"id": user_id}, {"$inc": {currency_field: -total_cost}})
        await db.inventory.update_one(
            {"user_id": user_id, "server_id": sid, "item_id": req.item_id},
            {"$inc": {"quantity": req.quantity},
             "$setOnInsert": {"server_id": sid, "account_id": user_id, "_slc_pack_90_strict_server_scoped_write": True}},
            upsert=True
        )
        return {"message": f"Acquistati {req.quantity}x {item['name']}", "item": item['name'], "quantity": req.quantity, "cost": total_cost, "server_id": sid, "pack_90_strict_server_scoped_write": True}

    # ============ USE EXP ITEM ============
    class UseExpItemRequest(BaseModel):
        user_hero_id: str
        item_id: str
        quantity: int = 1

    @router.post(
        "/inventory/use-exp",
        dependencies=[
            _Depends_postqa_d(
                make_legacy_mutation_gate_dep(
                    "DIVINE_ALLOW_LEGACY_INVENTORY_PROGRESS_MUTATIONS",
                    "/api/inventory/use-exp",
                )
            )
        ],
    )
    async def use_exp_item(req: UseExpItemRequest, server_id: str, current_user: dict = Depends(get_current_user)):
        # Pack 90 — STRICT server-scoped consume. server_id REQUIRED.
        user_id = current_user['id']
        if not server_id or not isinstance(server_id, str) or not server_id.strip():
            raise HTTPException(status_code=400, detail="SERVER_ID_REQUIRED")
        sid = server_id.strip()
        psp = await db.player_server_profiles.find_one({"user_id": user_id, "server_id": sid})
        if not psp:
            raise HTTPException(status_code=409, detail="PLAYER_SERVER_PROFILE_REQUIRED")
        item = EXP_ITEMS.get(req.item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Non e un oggetto EXP")
        inv = await db.inventory.find_one({"user_id": user_id, "server_id": sid, "item_id": req.item_id})
        if not inv or inv.get('quantity', 0) < req.quantity:
            raise HTTPException(status_code=400, detail="Non hai abbastanza oggetti!")
        # Pack 90 — Hero must be on same server (user_hero must have server_id == sid).
        uh = await db.user_heroes.find_one({"id": req.user_hero_id, "user_id": user_id, "server_id": sid})
        if not uh:
            raise HTTPException(status_code=404, detail="Eroe non trovato per questo server")
        total_exp = item['exp'] * req.quantity
        old_level = uh.get('level', 1)
        new_exp = uh.get('exp', 0) + total_exp
        new_level = old_level
        level_cap = uh.get('level_cap', 100)
        while new_level < level_cap:
            needed = new_level * 100 + 50
            if new_exp >= needed:
                new_exp -= needed
                new_level += 1
            else:
                break
        # Pack 90 — Update user_hero scoped by user_id+server_id (no cross-server hero leak).
        await db.user_heroes.update_one(
            {"id": req.user_hero_id, "user_id": user_id, "server_id": sid},
            {"$set": {"level": new_level, "exp": new_exp}}
        )
        await db.inventory.update_one(
            {"user_id": user_id, "server_id": sid, "item_id": req.item_id},
            {"$inc": {"quantity": -req.quantity}}
        )
        return {
            "hero_name": uh.get('hero_name', '?'),
            "exp_gained": total_exp,
            "old_level": old_level,
            "new_level": new_level,
            "leveled_up": new_level > old_level,
            "items_used": req.quantity,
            "server_id": sid,
            "pack_90_strict_server_scoped_write": True,
        }

    # ============ SKILL UPGRADE ============
    @router.get("/hero/skills-upgrade/{user_hero_id}")
    async def get_skill_upgrade_info(user_hero_id: str, server_id: str, current_user: dict = Depends(get_current_user)):
        # Pack 90 — STRICT server-scoped: hero + inventory letti per (user_id, server_id).
        user_id = current_user['id']
        if not server_id or not isinstance(server_id, str) or not server_id.strip():
            raise HTTPException(status_code=400, detail="SERVER_ID_REQUIRED")
        sid = server_id.strip()
        psp = await db.player_server_profiles.find_one({"user_id": user_id, "server_id": sid})
        if not psp:
            raise HTTPException(status_code=409, detail="PLAYER_SERVER_PROFILE_REQUIRED")
        uh = await db.user_heroes.find_one({"id": user_hero_id, "user_id": user_id, "server_id": sid})
        if not uh:
            raise HTTPException(status_code=404, detail="Eroe non trovato per questo server")
        hero = await db.heroes.find_one({"id": uh['hero_id']})
        skill_levels = uh.get('skill_levels', {})
        user = await db.users.find_one({"id": user_id})
        inv_items = await db.inventory.find({"user_id": user_id, "server_id": sid}).to_list(length=100)
        inv_map = {i['item_id']: i.get('quantity', 0) for i in inv_items}
        
        skills_info = []
        skill_defs = hero.get('skills', {}) if hero else {}
        
        for skill_key in ['basic_attack', 'active_skill', 'passive_skill', 'ultimate']:
            skill_def = skill_defs.get(skill_key)
            if not skill_def:
                continue
            
            current_level = skill_levels.get(skill_key, 1)
            max_level = 10
            can_upgrade = current_level < max_level
            
            costs = SKILL_UPGRADE_COSTS.get(current_level, {})
            can_afford = True
            cost_details = []
            for res, amount in costs.items():
                if res == 'gold':
                    have = user.get('gold', 0)
                else:
                    have = inv_map.get(res, 0)
                mat_info = SKILL_MATERIALS.get(res, {"name": res, "icon": ""})
                cost_details.append({
                    "resource": res,
                    "name": mat_info.get('name', res) if res != 'gold' else 'Oro',
                    "icon": mat_info.get('icon', '') if res != 'gold' else '\U0001f4b0',
                    "needed": amount,
                    "have": have,
                    "met": have >= amount,
                })
                if have < amount:
                    can_afford = False
            
            dmg_mult = (skill_def.get('damage_mult', 1.0) or 1.0)
            bonus_per_level = dmg_mult * 0.1
            
            skills_info.append({
                "key": skill_key,
                "name": skill_def.get('name', skill_key),
                "type": skill_def.get('type', 'active'),
                "icon": skill_def.get('icon', '\u2728'),
                "description": skill_def.get('description', ''),
                "current_level": current_level,
                "max_level": max_level,
                "damage_mult": round(dmg_mult + bonus_per_level * (current_level - 1), 2),
                "next_damage_mult": round(dmg_mult + bonus_per_level * current_level, 2) if can_upgrade else None,
                "can_upgrade": can_upgrade and can_afford,
                "costs": cost_details if can_upgrade else [],
            })
        
        return {"hero_name": uh.get('hero_name', '?'), "skills": skills_info}

    class UpgradeSkillRequest(BaseModel):
        user_hero_id: str
        skill_key: str

    @router.post(
        "/hero/skill-upgrade",
        dependencies=[
            _Depends_postqa_d(
                make_legacy_mutation_gate_dep(
                    "DIVINE_ALLOW_LEGACY_SKILL_UPGRADE_MUTATIONS",
                    "/api/hero/skill-upgrade",
                )
            )
        ],
    )
    async def upgrade_skill(req: UpgradeSkillRequest, server_id: str, current_user: dict = Depends(get_current_user)):
        # Pack 90 — STRICT server-scoped.
        user_id = current_user['id']
        if not server_id or not isinstance(server_id, str) or not server_id.strip():
            raise HTTPException(status_code=400, detail="SERVER_ID_REQUIRED")
        sid = server_id.strip()
        psp = await db.player_server_profiles.find_one({"user_id": user_id, "server_id": sid})
        if not psp:
            raise HTTPException(status_code=409, detail="PLAYER_SERVER_PROFILE_REQUIRED")
        uh = await db.user_heroes.find_one({"id": req.user_hero_id, "user_id": user_id, "server_id": sid})
        if not uh:
            raise HTTPException(status_code=404, detail="Eroe non trovato per questo server")
        skill_levels = uh.get('skill_levels', {})
        current_level = skill_levels.get(req.skill_key, 1)
        if current_level >= 10:
            raise HTTPException(status_code=400, detail="Skill gia al livello massimo!")
        costs = SKILL_UPGRADE_COSTS.get(current_level, {})
        user = await db.users.find_one({"id": user_id})
        gold_cost = costs.get('gold', 0)
        if user.get('gold', 0) < gold_cost:
            raise HTTPException(status_code=400, detail="Oro insufficiente!")
        for res, amount in costs.items():
            if res == 'gold':
                continue
            inv = await db.inventory.find_one({"user_id": user_id, "server_id": sid, "item_id": res})
            if not inv or inv.get('quantity', 0) < amount:
                mat = SKILL_MATERIALS.get(res, {})
                raise HTTPException(status_code=400, detail=f"Materiale insufficiente: {mat.get('name', res)}")
        if gold_cost > 0:
            await db.users.update_one({"id": user_id}, {"$inc": {"gold": -gold_cost}})
        for res, amount in costs.items():
            if res == 'gold':
                continue
            await db.inventory.update_one(
                {"user_id": user_id, "server_id": sid, "item_id": res},
                {"$inc": {"quantity": -amount}}
            )
        new_level = current_level + 1
        skill_levels[req.skill_key] = new_level
        await db.user_heroes.update_one(
            {"id": req.user_hero_id, "user_id": user_id, "server_id": sid},
            {"$set": {"skill_levels": skill_levels}}
        )
        return {
            "hero_name": uh.get('hero_name', '?'),
            "skill_key": req.skill_key,
            "old_level": current_level,
            "new_level": new_level,
            "message": f"Skill potenziata al Lv.{new_level}!",
            "server_id": sid,
            "pack_90_strict_server_scoped_write": True,
        }

    return BATTLE_DROPS
