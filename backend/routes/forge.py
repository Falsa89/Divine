"""
Divine Waifus - Forge & Equipment System (Hokage Crisis style)
- Equipment forging (upgrade, fuse)
- Rune/Talisman system (2 slots per hero, unlocked at milestones)
- All items can be fused/upgraded in the Forge
"""
import random
import uuid
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

# ===================== EQUIPMENT TEMPLATES =====================
WEAPON_TEMPLATES = [
    {"id": "w_divine_blade", "name": "Lama Divina", "rarity": 6, "base_stats": {"physical_damage": 500, "crit_chance": 0.08, "crit_damage": 0.25}, "icon": "\u2694\uFE0F"},
    {"id": "w_celestial_staff", "name": "Bastone Celeste", "rarity": 6, "base_stats": {"magic_damage": 550, "hit_rate": 0.06, "penetration": 0.08}, "icon": "\U0001FA84"},
    {"id": "w_thunder_axe", "name": "Ascia del Tuono", "rarity": 5, "base_stats": {"physical_damage": 380, "crit_damage": 0.20, "combo_rate": 0.06}, "icon": "\U0001FA93"},
    {"id": "w_shadow_dagger", "name": "Pugnale d'Ombra", "rarity": 5, "base_stats": {"physical_damage": 320, "speed": 25, "penetration": 0.10}, "icon": "\U0001F5E1\uFE0F"},
    {"id": "w_flame_katana", "name": "Katana Infernale", "rarity": 5, "base_stats": {"physical_damage": 400, "crit_chance": 0.10, "damage_rate": 0.06}, "icon": "\U0001F525"},
    {"id": "w_sacred_bow", "name": "Arco Sacro", "rarity": 4, "base_stats": {"physical_damage": 280, "crit_chance": 0.06, "speed": 15}, "icon": "\U0001F3F9"},
    {"id": "w_ancient_wand", "name": "Bacchetta Antica", "rarity": 4, "base_stats": {"magic_damage": 300, "hit_rate": 0.04, "healing": 100}, "icon": "\U0001FA84"},
    {"id": "w_iron_sword", "name": "Spada di Ferro", "rarity": 3, "base_stats": {"physical_damage": 180, "crit_chance": 0.03}, "icon": "\u2694\uFE0F"},
    {"id": "w_wooden_staff", "name": "Bastone di Legno", "rarity": 2, "base_stats": {"magic_damage": 120, "healing": 60}, "icon": "\U0001FA84"},
    {"id": "w_rusty_knife", "name": "Coltello Arrugginito", "rarity": 1, "base_stats": {"physical_damage": 60}, "icon": "\U0001F52A"},
]

ARMOR_TEMPLATES = [
    {"id": "a_divine_plate", "name": "Corazza Divina", "rarity": 6, "base_stats": {"physical_defense": 400, "magic_defense": 300, "hp": 2000, "block_rate": 0.08}, "icon": "\U0001F6E1\uFE0F"},
    {"id": "a_dragon_mail", "name": "Maglia del Drago", "rarity": 5, "base_stats": {"physical_defense": 300, "hp": 1500, "magic_defense": 200}, "icon": "\U0001F432"},
    {"id": "a_mystic_robe", "name": "Veste Mistica", "rarity": 5, "base_stats": {"magic_defense": 300, "hp": 1200, "healing_received": 0.08}, "icon": "\U0001F9E5"},
    {"id": "a_chainmail", "name": "Cotta di Maglia", "rarity": 4, "base_stats": {"physical_defense": 220, "hp": 800}, "icon": "\U0001F6E1\uFE0F"},
    {"id": "a_leather_vest", "name": "Gilet di Cuoio", "rarity": 3, "base_stats": {"physical_defense": 130, "hp": 500, "dodge": 0.03}, "icon": "\U0001F9E5"},
    {"id": "a_cloth_robe", "name": "Veste di Tela", "rarity": 2, "base_stats": {"magic_defense": 80, "hp": 300}, "icon": "\U0001F455"},
    {"id": "a_torn_shirt", "name": "Camicia Strappata", "rarity": 1, "base_stats": {"hp": 150}, "icon": "\U0001F455"},
]

ACCESSORY_TEMPLATES = [
    {"id": "ac_crown_olymp", "name": "Corona dell'Olimpo", "rarity": 6, "base_stats": {"crit_chance": 0.12, "crit_damage": 0.40, "speed": 20}, "icon": "\U0001F451"},
    {"id": "ac_destiny_ring", "name": "Anello del Destino", "rarity": 5, "base_stats": {"crit_chance": 0.10, "penetration": 0.08, "hit_rate": 0.05}, "icon": "\U0001F48D"},
    {"id": "ac_mystic_amulet", "name": "Amuleto Mistico", "rarity": 5, "base_stats": {"magic_damage": 200, "magic_defense": 150, "healing": 100}, "icon": "\U0001F9FF"},
    {"id": "ac_elem_necklace", "name": "Collana Elementale", "rarity": 4, "base_stats": {"speed": 18, "dodge": 0.05, "combo_rate": 0.04}, "icon": "\U0001F4FF"},
    {"id": "ac_str_bracelet", "name": "Bracciale di Forza", "rarity": 3, "base_stats": {"physical_damage": 100, "crit_chance": 0.03}, "icon": "\u26D3\uFE0F"},
    {"id": "ac_simple_earring", "name": "Orecchino Comune", "rarity": 2, "base_stats": {"speed": 8, "dodge": 0.02}, "icon": "\U0001F4A0"},
    {"id": "ac_pebble_charm", "name": "Ciondolo di Pietra", "rarity": 1, "base_stats": {"hp": 200}, "icon": "\U0001FAA8"},
]

ALL_TEMPLATES = WEAPON_TEMPLATES + ARMOR_TEMPLATES + ACCESSORY_TEMPLATES

# ===================== RUNE/TALISMAN SYSTEM =====================
RUNE_SLOT_REQUIREMENTS = {
    1: {"min_stars": 7, "min_level": 100, "description": "Slot Runa 1: 7\u2B50 + Lv.100"},
    2: {"min_stars": 10, "min_level": 150, "description": "Slot Runa 2: 10\u2B50 + Lv.150"},
}

RUNE_MAIN_STATS = {
    "attack": {"name": "Runa d'Attacco", "icon": "\u2694\uFE0F", "stat": "physical_damage", "base_value": 150, "color": "#ff4444"},
    "magic": {"name": "Runa Magica", "icon": "\U0001FA84", "stat": "magic_damage", "base_value": 150, "color": "#9944ff"},
    "defense": {"name": "Runa Difensiva", "icon": "\U0001F6E1\uFE0F", "stat": "physical_defense", "base_value": 120, "color": "#4488ff"},
    "hp": {"name": "Runa Vitale", "icon": "\u2764\uFE0F", "stat": "hp", "base_value": 800, "color": "#44cc44"},
    "speed": {"name": "Runa di Velocita", "icon": "\u26A1", "stat": "speed", "base_value": 15, "color": "#ffd700"},
    "crit": {"name": "Runa Critica", "icon": "\U0001F4A5", "stat": "crit_chance", "base_value": 0.06, "color": "#ff8844"},
}

RUNE_SUB_STATS = [
    {"stat": "physical_damage", "range": [30, 120]},
    {"stat": "magic_damage", "range": [30, 120]},
    {"stat": "physical_defense", "range": [20, 80]},
    {"stat": "magic_defense", "range": [20, 80]},
    {"stat": "hp", "range": [200, 600]},
    {"stat": "speed", "range": [3, 12]},
    {"stat": "crit_chance", "range_pct": [0.01, 0.05]},
    {"stat": "crit_damage", "range_pct": [0.03, 0.12]},
    {"stat": "penetration", "range_pct": [0.01, 0.06]},
    {"stat": "dodge", "range_pct": [0.01, 0.04]},
    {"stat": "combo_rate", "range_pct": [0.01, 0.05]},
    {"stat": "block_rate", "range_pct": [0.01, 0.04]},
    {"stat": "hit_rate", "range_pct": [0.01, 0.04]},
    {"stat": "damage_rate", "range_pct": [0.01, 0.05]},
    {"stat": "healing", "range": [20, 100]},
]

RUNE_PASSIVE_SKILLS = [
    {"id": "rp_lifesteal", "name": "Risucchio Vitale", "description": "Ruba 5% dei danni inflitti come HP", "effect": {"lifesteal": 0.05}, "rarity_min": 4},
    {"id": "rp_thorns", "name": "Riflesso Spinoso", "description": "Riflette 8% dei danni ricevuti", "effect": {"thorns": 0.08}, "rarity_min": 4},
    {"id": "rp_swift", "name": "Piedi Rapidi", "description": "+12% velocita per i primi 3 turni", "effect": {"speed_buff_3t": 0.12}, "rarity_min": 3},
    {"id": "rp_fortify", "name": "Fortificazione", "description": "+10% difese quando HP > 70%", "effect": {"def_buff_hp70": 0.10}, "rarity_min": 3},
    {"id": "rp_rage", "name": "Furia Crescente", "description": "+3% danno per ogni turno (max +15%)", "effect": {"stacking_dmg": 0.03, "max_stack": 5}, "rarity_min": 5},
    {"id": "rp_healing_aura", "name": "Aura Curativa", "description": "Cura 3% HP max ogni turno", "effect": {"heal_per_turn": 0.03}, "rarity_min": 3},
    {"id": "rp_last_stand", "name": "Ultima Resistenza", "description": "Sopravvive con 1 HP una volta se il colpo sarebbe letale", "effect": {"last_stand": True}, "rarity_min": 5},
    {"id": "rp_piercing", "name": "Colpo Perforante", "description": "20% chance di ignorare completamente la difesa nemica", "effect": {"ignore_def_chance": 0.20}, "rarity_min": 5},
]

# Forge upgrade costs per level
FORGE_UPGRADE_COSTS = {
    1: {"gold": 1000, "material": 0},
    5: {"gold": 3000, "material": 1},
    10: {"gold": 8000, "material": 2},
    15: {"gold": 20000, "material": 3},
    20: {"gold": 50000, "material": 5},
    25: {"gold": 100000, "material": 8},
    30: {"gold": 200000, "material": 10},
}

MAX_EQUIP_LEVEL = 30


def _generate_rune(rarity: int) -> dict:
    """Generate a random rune with main stat + sub-stats."""
    main_type = random.choice(list(RUNE_MAIN_STATS.keys()))
    main_info = RUNE_MAIN_STATS[main_type]
    rarity_mult = 0.5 + rarity * 0.25

    # Generate sub-stats (rarity determines how many: 1★=1, 3★=2, 5★=3, 6★=4)
    num_subs = min(4, max(1, (rarity + 1) // 2))
    available_subs = [s for s in RUNE_SUB_STATS if s["stat"] != main_info["stat"]]
    chosen_subs = random.sample(available_subs, min(num_subs, len(available_subs)))
    sub_stats = {}
    for sub in chosen_subs:
        if "range_pct" in sub:
            val = round(random.uniform(sub["range_pct"][0], sub["range_pct"][1]) * rarity_mult, 3)
        else:
            val = int(random.uniform(sub["range"][0], sub["range"][1]) * rarity_mult)
        sub_stats[sub["stat"]] = val

    # Passive skill (5★+ runes have a chance)
    passive = None
    if rarity >= 4 and random.random() < 0.3 + (rarity - 4) * 0.15:
        eligible = [p for p in RUNE_PASSIVE_SKILLS if p["rarity_min"] <= rarity]
        if eligible:
            passive = random.choice(eligible)

    main_val = main_info["base_value"] * rarity_mult
    if isinstance(main_info["base_value"], float):
        main_val = round(main_val, 3)
    else:
        main_val = int(main_val)

    return {
        "id": str(uuid.uuid4()),
        "type": main_type,
        "name": main_info["name"],
        "icon": main_info["icon"],
        "color": main_info["color"],
        "rarity": rarity,
        "level": 1,
        "main_stat": {main_info["stat"]: main_val},
        "sub_stats": sub_stats,
        "passive_skill": passive,
    }


def register_forge_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    # ==================== FORGE - EQUIPMENT UPGRADE ====================
    @router.get("/forge")
    async def get_forge_info(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        equips = await db.user_equipment.find({"user_id": uid}).to_list(500)
        return {
            "equipment_count": len(equips),
            "max_level": MAX_EQUIP_LEVEL,
            "templates": {
                "weapons": [{"id": t["id"], "name": t["name"], "rarity": t["rarity"], "icon": t["icon"]} for t in WEAPON_TEMPLATES],
                "armors": [{"id": t["id"], "name": t["name"], "rarity": t["rarity"], "icon": t["icon"]} for t in ARMOR_TEMPLATES],
                "accessories": [{"id": t["id"], "name": t["name"], "rarity": t["rarity"], "icon": t["icon"]} for t in ACCESSORY_TEMPLATES],
            },
        }

    class ForgeUpgradeRequest(BaseModel):
        equipment_id: str

    @router.post("/forge/upgrade")
    async def forge_upgrade(req: ForgeUpgradeRequest, current_user: dict = Depends(get_current_user)):
        """Upgrade equipment level in the forge."""
        uid = current_user["id"]
        equip = await db.user_equipment.find_one({"id": req.equipment_id, "user_id": uid})
        if not equip:
            raise HTTPException(404, "Equipaggiamento non trovato")
        level = equip.get("level", 1)
        if level >= MAX_EQUIP_LEVEL:
            raise HTTPException(400, f"Livello massimo ({MAX_EQUIP_LEVEL}) raggiunto!")
        # Find cost tier
        cost_tier = 1
        for tier_level in sorted(FORGE_UPGRADE_COSTS.keys()):
            if level >= tier_level:
                cost_tier = tier_level
        costs = FORGE_UPGRADE_COSTS[cost_tier]
        gold_cost = costs["gold"]
        user = await db.users.find_one({"id": uid})
        if user.get("gold", 0) < gold_cost:
            raise HTTPException(400, f"Servono {gold_cost:,} oro!")
        await db.users.update_one({"id": uid}, {"$inc": {"gold": -gold_cost}})
        # Apply upgrade - stats increase by 5% per level
        new_level = level + 1
        base_stats = equip.get("base_stats", equip.get("stats", {}))
        upgraded_stats = {}
        for stat, val in base_stats.items():
            if isinstance(val, (int, float)):
                mult = 1 + (new_level - 1) * 0.05
                upgraded_stats[stat] = round(val * mult, 3) if isinstance(val, float) else int(val * mult)
        await db.user_equipment.update_one(
            {"id": req.equipment_id},
            {"$set": {"level": new_level, "stats": upgraded_stats, "base_stats": base_stats}}
        )
        return {
            "success": True, "new_level": new_level,
            "stats": upgraded_stats, "gold_spent": gold_cost,
        }

    class ForgeFuseRequest(BaseModel):
        base_id: str
        fodder_ids: list

    @router.post("/forge/fuse")
    async def forge_fuse_equipment(req: ForgeFuseRequest, current_user: dict = Depends(get_current_user)):
        """Fuse duplicate equipment to increase rarity (stars)."""
        uid = current_user["id"]
        base = await db.user_equipment.find_one({"id": req.base_id, "user_id": uid})
        if not base:
            raise HTTPException(404, "Equipaggiamento base non trovato")
        if not req.fodder_ids or len(req.fodder_ids) < 2:
            raise HTTPException(400, "Servono almeno 2 equipaggiamenti da sacrificare!")
        base_rarity = base.get("rarity", 1)
        if base_rarity >= 6:
            raise HTTPException(400, "Rarita massima (6\u2B50) raggiunta!")
        # Validate and delete fodder
        for fid in req.fodder_ids:
            fodder = await db.user_equipment.find_one({"id": fid, "user_id": uid})
            if not fodder:
                raise HTTPException(404, f"Equipaggiamento {fid} non trovato")
            if fid == req.base_id:
                raise HTTPException(400, "Non puoi sacrificare l'equipaggiamento base!")
            await db.user_equipment.delete_one({"id": fid, "user_id": uid})
        # Upgrade rarity
        new_rarity = min(6, base_rarity + 1)
        # Boost base stats by 20%
        base_stats = base.get("base_stats", base.get("stats", {}))
        boosted = {}
        for stat, val in base_stats.items():
            if isinstance(val, (int, float)):
                boosted[stat] = round(val * 1.2, 3) if isinstance(val, float) else int(val * 1.2)
        level = base.get("level", 1)
        mult = 1 + (level - 1) * 0.05
        current_stats = {k: round(v * mult, 3) if isinstance(v, float) else int(v * mult) for k, v in boosted.items()}
        await db.user_equipment.update_one(
            {"id": req.base_id},
            {"$set": {"rarity": new_rarity, "base_stats": boosted, "stats": current_stats, "fused_at": datetime.utcnow()}}
        )
        return {
            "success": True, "new_rarity": new_rarity,
            "base_stats": boosted, "fodder_consumed": len(req.fodder_ids),
        }

    # ==================== RUNE / TALISMAN SYSTEM ====================
    @router.get("/runes")
    async def get_runes(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        runes = await db.user_runes.find({"user_id": uid}).to_list(200)
        return {
            "runes": [serialize_doc(r) for r in runes],
            "slot_requirements": RUNE_SLOT_REQUIREMENTS,
            "main_stat_types": {k: {"name": v["name"], "icon": v["icon"], "color": v["color"]} for k, v in RUNE_MAIN_STATS.items()},
        }

    @router.post("/runes/craft")
    async def craft_rune(current_user: dict = Depends(get_current_user)):
        """Craft a random rune (costs gold)."""
        uid = current_user["id"]
        user = await db.users.find_one({"id": uid})
        cost = 10000
        if user.get("gold", 0) < cost:
            raise HTTPException(400, f"Servono {cost:,} oro!")
        await db.users.update_one({"id": uid}, {"$inc": {"gold": -cost}})
        # Random rarity (weighted)
        rarity = random.choices([1, 2, 3, 4, 5, 6], weights=[0.25, 0.25, 0.20, 0.15, 0.10, 0.05])[0]
        rune = _generate_rune(rarity)
        rune["user_id"] = uid
        rune["created_at"] = datetime.utcnow()
        await db.user_runes.insert_one(rune)
        return {"success": True, "rune": rune}

    @router.post("/runes/craft-premium")
    async def craft_premium_rune(current_user: dict = Depends(get_current_user)):
        """Craft a guaranteed 4★+ rune (costs gems)."""
        uid = current_user["id"]
        user = await db.users.find_one({"id": uid})
        cost = 100
        if user.get("gems", 0) < cost:
            raise HTTPException(400, f"Servono {cost} gemme!")
        await db.users.update_one({"id": uid}, {"$inc": {"gems": -cost}})
        rarity = random.choices([4, 5, 6], weights=[0.55, 0.30, 0.15])[0]
        rune = _generate_rune(rarity)
        rune["user_id"] = uid
        rune["created_at"] = datetime.utcnow()
        await db.user_runes.insert_one(rune)
        return {"success": True, "rune": rune}

    class RuneFuseRequest(BaseModel):
        base_rune_id: str
        fodder_rune_ids: list

    @router.post("/runes/fuse")
    async def fuse_runes(req: RuneFuseRequest, current_user: dict = Depends(get_current_user)):
        """Fuse runes to upgrade level. 3 runes = +1 level to base rune."""
        uid = current_user["id"]
        base = await db.user_runes.find_one({"id": req.base_rune_id, "user_id": uid})
        if not base:
            raise HTTPException(404, "Runa base non trovata")
        if len(req.fodder_rune_ids) < 3:
            raise HTTPException(400, "Servono almeno 3 rune da sacrificare!")
        if base.get("level", 1) >= 15:
            raise HTTPException(400, "Livello massimo (15) raggiunto!")
        for fid in req.fodder_rune_ids[:3]:
            fodder = await db.user_runes.find_one({"id": fid, "user_id": uid})
            if not fodder:
                raise HTTPException(404, f"Runa {fid} non trovata")
            if fid == req.base_rune_id:
                raise HTTPException(400, "Non puoi sacrificare la runa base!")
            await db.user_runes.delete_one({"id": fid, "user_id": uid})
        # Level up rune - boost all stats by 8%
        new_level = base.get("level", 1) + 1
        boost_mult = 1.08
        main_stat = base.get("main_stat", {})
        new_main = {k: round(v * boost_mult, 3) if isinstance(v, float) else int(v * boost_mult) for k, v in main_stat.items()}
        sub_stats = base.get("sub_stats", {})
        new_subs = {k: round(v * boost_mult, 3) if isinstance(v, float) else int(v * boost_mult) for k, v in sub_stats.items()}
        # Chance to gain new sub-stat at level 5, 10, 15
        if new_level in [5, 10, 15] and len(new_subs) < 4:
            available = [s for s in RUNE_SUB_STATS if s["stat"] not in new_subs and s["stat"] not in main_stat]
            if available:
                new_sub = random.choice(available)
                rarity_mult = 0.5 + base.get("rarity", 1) * 0.25
                if "range_pct" in new_sub:
                    new_subs[new_sub["stat"]] = round(random.uniform(new_sub["range_pct"][0], new_sub["range_pct"][1]) * rarity_mult, 3)
                else:
                    new_subs[new_sub["stat"]] = int(random.uniform(new_sub["range"][0], new_sub["range"][1]) * rarity_mult)
        await db.user_runes.update_one(
            {"id": req.base_rune_id},
            {"$set": {"level": new_level, "main_stat": new_main, "sub_stats": new_subs}}
        )
        return {
            "success": True, "new_level": new_level,
            "main_stat": new_main, "sub_stats": new_subs,
            "fodder_consumed": 3,
        }

    class EquipRuneRequest(BaseModel):
        rune_id: str
        user_hero_id: str
        slot: int  # 1 or 2

    @router.post("/runes/equip")
    async def equip_rune(req: EquipRuneRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        if req.slot not in [1, 2]:
            raise HTTPException(400, "Slot runa non valido (1 o 2)")
        rune = await db.user_runes.find_one({"id": req.rune_id, "user_id": uid})
        if not rune:
            raise HTTPException(404, "Runa non trovata")
        uh = await db.user_heroes.find_one({"id": req.user_hero_id, "user_id": uid})
        if not uh:
            raise HTTPException(404, "Eroe non trovato")
        # Check slot requirements
        hero = await db.heroes.find_one({"id": uh["hero_id"]})
        stars = uh.get("stars", hero.get("rarity", 1) if hero else 1)
        level = uh.get("level", 1)
        slot_req = RUNE_SLOT_REQUIREMENTS.get(req.slot)
        if not slot_req:
            raise HTTPException(400, "Slot non valido")
        if stars < slot_req["min_stars"] or level < slot_req["min_level"]:
            raise HTTPException(400, f"Per lo slot {req.slot} servono {slot_req['min_stars']}\u2B50 e Lv.{slot_req['min_level']}!")
        # Unequip previous rune in that slot
        await db.user_runes.update_many(
            {"user_id": uid, "equipped_to": req.user_hero_id, "equipped_slot": req.slot},
            {"$unset": {"equipped_to": "", "equipped_slot": ""}}
        )
        # Equip new rune
        await db.user_runes.update_one(
            {"id": req.rune_id},
            {"$set": {"equipped_to": req.user_hero_id, "equipped_slot": req.slot}}
        )
        return {"success": True, "rune": rune.get("name"), "slot": req.slot, "hero": hero.get("name", "?") if hero else "?"}

    @router.get("/hero/equipment/{user_hero_id}")
    async def get_hero_equipment(user_hero_id: str, current_user: dict = Depends(get_current_user)):
        """Get all equipment and runes equipped on a hero."""
        uid = current_user["id"]
        uh = await db.user_heroes.find_one({"id": user_hero_id, "user_id": uid})
        if not uh:
            raise HTTPException(404, "Eroe non trovato")
        hero = await db.heroes.find_one({"id": uh["hero_id"]})
        stars = uh.get("stars", hero.get("rarity", 1) if hero else 1)
        level = uh.get("level", 1)
        # Get equipped items
        equips = await db.user_equipment.find({"user_id": uid, "equipped_to": user_hero_id}).to_list(10)
        # Get equipped runes
        runes = await db.user_runes.find({"user_id": uid, "equipped_to": user_hero_id}).to_list(2)
        rune_1 = next((r for r in runes if r.get("equipped_slot") == 1), None)
        rune_2 = next((r for r in runes if r.get("equipped_slot") == 2), None)
        # Rune slot availability
        slot1_unlocked = stars >= RUNE_SLOT_REQUIREMENTS[1]["min_stars"] and level >= RUNE_SLOT_REQUIREMENTS[1]["min_level"]
        slot2_unlocked = stars >= RUNE_SLOT_REQUIREMENTS[2]["min_stars"] and level >= RUNE_SLOT_REQUIREMENTS[2]["min_level"]
        # Calculate total equipment bonus
        total_bonus = {}
        for eq in equips:
            for stat, val in eq.get("stats", {}).items():
                total_bonus[stat] = total_bonus.get(stat, 0) + (val if isinstance(val, (int, float)) else 0)
        for r in runes:
            for stat, val in r.get("main_stat", {}).items():
                total_bonus[stat] = total_bonus.get(stat, 0) + val
            for stat, val in r.get("sub_stats", {}).items():
                total_bonus[stat] = total_bonus.get(stat, 0) + val

        return {
            "hero_name": hero.get("name", "?") if hero else "?",
            "equipment": [serialize_doc(e) for e in equips],
            "rune_slot_1": {"unlocked": slot1_unlocked, "rune": serialize_doc(rune_1) if rune_1 else None, "requirement": RUNE_SLOT_REQUIREMENTS[1]},
            "rune_slot_2": {"unlocked": slot2_unlocked, "rune": serialize_doc(rune_2) if rune_2 else None, "requirement": RUNE_SLOT_REQUIREMENTS[2]},
            "total_equipment_bonus": total_bonus,
        }
