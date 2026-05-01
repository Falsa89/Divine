"""
Divine Waifus - Hero Progression System
- Skill system by rarity (1-6★)
- Level system with star-based caps
- Reincarnation system
- Fragments & packages
"""
import random
import uuid
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

# ===================== LEVEL CAPS PER STAR (max 15 stars) =====================
STAR_LEVEL_CAPS = {
    1: 30, 2: 50, 3: 70, 4: 90, 5: 110,
    6: 130, 7: 150, 8: 170, 9: 190, 10: 210,
    11: 230, 12: 260, 13: 290, 14: 320, 15: 350,
}
MAX_STARS = 15

# ===================== MAX STARS BY BASE RARITY =====================
# Heroes summoned at X★ can only reach a max through fusion
MAX_STARS_BY_BASE = {1: 6, 2: 8, 3: 10, 4: 12, 5: 14, 6: 15}

# ===================== STAR FUSION REQUIREMENTS (Hokage Crisis style) =====================
# To go from star N to N+1, you need:
# - same_copies: number of duplicate copies of the SAME hero
# - any_5plus: number of any 5★+ hero sacrifices (for higher tiers)
# - gold: gold cost
# - material: special material required (None if not needed)
# - material_count: how many of that material
STAR_FUSION_REQS = {
    # 6→7: Entry to enhanced territory
    7:  {"same_copies": 1, "any_5plus": 0, "gold": 100000,  "material": None, "material_count": 0},
    # 7→8
    8:  {"same_copies": 1, "any_5plus": 0, "gold": 200000,  "material": None, "material_count": 0},
    # 8→9
    9:  {"same_copies": 2, "any_5plus": 0, "gold": 500000,  "material": None, "material_count": 0},
    # 9→10: Needs special material
    10: {"same_copies": 2, "any_5plus": 1, "gold": 1000000, "material": "stella_divina", "material_count": 1},
    # 10→11
    11: {"same_copies": 3, "any_5plus": 1, "gold": 2000000, "material": "stella_divina", "material_count": 2},
    # 11→12
    12: {"same_copies": 3, "any_5plus": 2, "gold": 5000000, "material": "stella_divina", "material_count": 3},
    # 12→13: Legendary material
    13: {"same_copies": 4, "any_5plus": 2, "gold": 10000000, "material": "cristallo_astrale", "material_count": 1},
    # 13→14
    14: {"same_copies": 4, "any_5plus": 3, "gold": 15000000, "material": "cristallo_astrale", "material_count": 2},
    # 14→15: Transcendence
    15: {"same_copies": 5, "any_5plus": 3, "gold": 25000000, "material": "essenza_trascendente", "material_count": 1},
}

# Lower rarity fusions (1★→2★, etc.) are simpler
LOW_STAR_FUSION_REQS = {
    2: {"same_copies": 2, "any_copies": 1, "gold": 5000},
    3: {"same_copies": 2, "any_copies": 2, "gold": 10000},
    4: {"same_copies": 3, "any_copies": 2, "gold": 25000},
    5: {"same_copies": 3, "any_copies": 3, "gold": 50000},
    6: {"same_copies": 4, "any_copies": 3, "gold": 100000},
}

# Fusion materials
FUSION_MATERIALS = {
    "stella_divina": {"name": "Stella Divina", "icon": "\u2B50", "description": "Stella celestiale per fusioni 9-12\u2B50. Ottenibile da Torre, Shop, Eventi.", "shop_cost_gems": 300},
    "cristallo_astrale": {"name": "Cristallo Astrale", "icon": "\U0001F48E", "description": "Cristallo cosmico per fusioni 12-14\u2B50. Ottenibile da Raid, GvG, Eventi speciali.", "shop_cost_gems": 800},
    "essenza_trascendente": {"name": "Essenza Trascendente", "icon": "\U0001F451", "description": "Essenza rarissima per la fusione finale a 15\u2B50. Solo da contenuti endgame.", "shop_cost_gems": 2000},
}

# EXP required per level: level * 100 + (level^1.3 * 20)
def exp_for_level(level: int) -> int:
    return int(level * 100 + (level ** 1.3) * 20)

# ===================== SKILL DEFINITIONS PER HERO =====================
# Each hero gets skills based on their rarity
# Skills are defined by element + class combo

ACTIVE_SKILLS_BY_ELEMENT = {
    "fire": [
        {"id": "fire_strike", "name": "Colpo Infernale", "icon": "\U0001F525", "type": "active", "damage_mult": 1.2, "target": "single", "description": "Colpo infuocato al nemico"},
        {"id": "fire_burst", "name": "Esplosione Ardente", "icon": "\U0001F30B", "type": "active", "damage_mult": 1.0, "target": "aoe", "description": "Esplosione che colpisce tutti i nemici"},
    ],
    "water": [
        {"id": "water_slash", "name": "Lama d'Acqua", "icon": "\U0001F4A7", "type": "active", "damage_mult": 1.1, "target": "single", "description": "Fendente d'acqua tagliente"},
        {"id": "water_wave", "name": "Onda Purificatrice", "icon": "\U0001F30A", "type": "active", "damage_mult": 0.8, "target": "aoe", "effect": "heal_10", "description": "Onda che cura 10% HP alleati"},
    ],
    "earth": [
        {"id": "earth_punch", "name": "Pugno di Terra", "icon": "\U0001FAA8", "type": "active", "damage_mult": 1.3, "target": "single", "description": "Pugno devastante di terra"},
        {"id": "earth_quake", "name": "Terremoto", "icon": "\u26F0\uFE0F", "type": "active", "damage_mult": 0.9, "target": "aoe", "effect": "stun_20", "description": "Terremoto con 20% stordimento"},
    ],
    "wind": [
        {"id": "wind_cut", "name": "Taglio del Vento", "icon": "\U0001F4A8", "type": "active", "damage_mult": 1.1, "target": "single", "effect": "speed_up", "description": "Taglio rapido che aumenta velocita"},
        {"id": "wind_storm", "name": "Tempesta di Vento", "icon": "\U0001F32C\uFE0F", "type": "active", "damage_mult": 1.0, "target": "aoe", "description": "Tempesta che colpisce tutti"},
    ],
    "thunder": [
        {"id": "thunder_bolt", "name": "Scarica Elettrica", "icon": "\u26A1", "type": "active", "damage_mult": 1.4, "target": "single", "description": "Fulmine concentrato sul nemico"},
        {"id": "thunder_chain", "name": "Catena di Fulmini", "icon": "\U0001F329\uFE0F", "type": "active", "damage_mult": 0.7, "target": "chain_3", "description": "Fulmine che rimbalza tra 3 nemici"},
    ],
    "light": [
        {"id": "light_beam", "name": "Raggio Sacro", "icon": "\u2728", "type": "active", "damage_mult": 1.2, "target": "single", "description": "Raggio di luce purificatrice"},
        {"id": "light_blessing", "name": "Benedizione", "icon": "\U0001F31F", "type": "active", "damage_mult": 0.5, "target": "all_allies", "effect": "heal_15", "description": "Cura 15% HP tutti gli alleati"},
    ],
    "shadow": [
        {"id": "shadow_claw", "name": "Artiglio d'Ombra", "icon": "\U0001F311", "type": "active", "damage_mult": 1.3, "target": "single", "effect": "poison", "description": "Artiglio velenoso dall'ombra"},
        {"id": "shadow_drain", "name": "Risucchio Vitale", "icon": "\U0001F480", "type": "active", "damage_mult": 1.0, "target": "single", "effect": "lifesteal_30", "description": "Ruba 30% dei danni come HP"},
    ],
}

PASSIVE_SKILLS_BY_CLASS = {
    "DPS": [
        {"id": "berserker", "name": "Furia del Berserker", "icon": "\U0001F525", "type": "passive", "effect": {"crit_chance": 0.10, "damage_rate": 0.08}, "description": "+10% Chance Critico, +8% Damage Rate"},
        {"id": "assassin_eye", "name": "Occhio dell'Assassino", "icon": "\U0001F441\uFE0F", "type": "passive", "effect": {"penetration": 0.08, "crit_damage": 0.15}, "description": "+8% Penetrazione, +15% Danno Critico"},
    ],
    "Tank": [
        {"id": "iron_wall", "name": "Muro di Ferro", "icon": "\U0001F6E1\uFE0F", "type": "passive", "effect": {"physical_defense": 0.12, "block_rate": 0.10}, "description": "+12% Difesa Fisica, +10% Block Rate"},
        {"id": "titan_body", "name": "Corpo del Titano", "icon": "\U0001F4AA", "type": "passive", "effect": {"hp": 0.15, "healing_received": 0.10}, "description": "+15% HP, +10% Cure Ricevute"},
    ],
    "Support": [
        {"id": "divine_grace", "name": "Grazia Divina", "icon": "\U0001F49A", "type": "passive", "effect": {"healing": 0.15, "speed": 0.10}, "description": "+15% Cure, +10% Velocita"},
        {"id": "spirit_link", "name": "Legame Spirituale", "icon": "\U0001F54A\uFE0F", "type": "passive", "effect": {"magic_defense": 0.10, "healing_received": 0.12}, "description": "+10% Difesa Magica, +12% Cure Ricevute"},
    ],
}

ULTIMATE_SKILLS_BY_ELEMENT = {
    "fire": {"id": "ult_fire", "name": "Inferno Divino", "icon": "\u2604\uFE0F", "type": "ultimate", "damage_mult": 4.5, "target": "aoe", "effect": "burn_3t", "charge_turns": 5, "description": "Devastante inferno che brucia tutto per 3 turni"},
    "water": {"id": "ult_water", "name": "Maremoto Celeste", "icon": "\U0001F9CA", "type": "ultimate", "damage_mult": 3.5, "target": "aoe", "effect": "freeze_1t", "charge_turns": 5, "description": "Maremoto che congela tutti i nemici per 1 turno"},
    "earth": {"id": "ult_earth", "name": "Collasso Tettonico", "icon": "\U0001F30D", "type": "ultimate", "damage_mult": 4.0, "target": "aoe", "effect": "def_break_40", "charge_turns": 5, "description": "Terremoto devastante che riduce DEF del 40%"},
    "wind": {"id": "ult_wind", "name": "Uragano Divino", "icon": "\U0001F300", "type": "ultimate", "damage_mult": 5.0, "target": "aoe", "effect": "bleed_3t", "charge_turns": 6, "description": "Uragano che lacera e provoca sanguinamento"},
    "thunder": {"id": "ult_thunder", "name": "Giudizio del Tuono", "icon": "\u26C8\uFE0F", "type": "ultimate", "damage_mult": 5.5, "target": "aoe", "effect": "stun_all_1t", "charge_turns": 6, "description": "Fulmini che stordiscono tutti i nemici per 1 turno"},
    "light": {"id": "ult_light", "name": "Apocalisse Luminosa", "icon": "\U0001F4AB", "type": "ultimate", "damage_mult": 5.0, "target": "aoe", "effect": "purify_heal_20", "charge_turns": 5, "description": "Luce che purifica debuff e cura 20% HP team"},
    "shadow": {"id": "ult_shadow", "name": "Eclissi Totale", "icon": "\U0001F573\uFE0F", "type": "ultimate", "damage_mult": 5.5, "target": "aoe", "effect": "death_mark_15", "charge_turns": 6, "description": "15% chance eliminazione istantanea per ogni nemico!"},
}

# ===================== FRAGMENTS =====================
FRAGMENT_TYPES = [
    {"id": "green", "name": "Frammento Verde", "icon": "\U0001F7E2", "color": "#44cc44", "required": 30, "hero_rarity": 2, "description": "30 frammenti = 1 eroe casuale 2\u2B50"},
    {"id": "blue", "name": "Frammento Blu", "icon": "\U0001F535", "color": "#4488ff", "required": 40, "hero_rarity": 3, "description": "40 frammenti = 1 eroe casuale 3\u2B50"},
    {"id": "purple", "name": "Frammento Viola", "icon": "\U0001F7E3", "color": "#aa44ff", "required": 50, "hero_rarity": 4, "description": "50 frammenti = 1 eroe casuale 4\u2B50"},
    {"id": "orange", "name": "Frammento Arancio", "icon": "\U0001F7E0", "color": "#ff8844", "required": 60, "hero_rarity": 5, "description": "60 frammenti = 1 eroe casuale 5\u2B50"},
    {"id": "gold", "name": "Frammento Dorato", "icon": "\U0001F7E1", "color": "#ffd700", "required": 80, "hero_rarity": 6, "description": "80 frammenti = 1 eroe casuale 6\u2B50"},
]

# Reincarnation items
REINCARNATION_ITEMS = [
    {"id": "soul_crystal", "name": "Cristallo dell'Anima", "icon": "\U0001F48E", "cost_gems": 500, "description": "Necessario per la reincarnazione. Risveglia il potenziale nascosto."},
    {"id": "divine_essence", "name": "Essenza Divina", "icon": "\u2728", "cost_gems": 200, "description": "Essenza pura per potenziare la reincarnazione."},
]

# Reincarnation stat boost
REINCARNATION_BOOST = 0.25  # +25% to all base stats


def get_hero_skills(element: str, hero_class: str, rarity: int, is_reincarnated: bool = False):
    """Build skill set based on star count (up to 15 stars).
    1-2★: 1 active skill
    3★: +1 passive (permanent)
    4★: +2nd active (alternating turns)
    5★: +2nd passive + unique item unlock
    6★: Ultimate (charged)
    7-9★: Enhanced skills (+15% damage per star above 6)
    10★: 3rd passive unlock
    12★: Enhanced Ultimate (+30% damage)
    15★: Transcendent form (all skills +20%)
    """
    skills = {
        "active_1": None, "active_2": None,
        "passive_1": None, "passive_2": None, "passive_3": None,
        "ultimate": None,
        "star_bonus": None,
    }
    element_actives = ACTIVE_SKILLS_BY_ELEMENT.get(element, ACTIVE_SKILLS_BY_ELEMENT["fire"])
    class_passives = PASSIVE_SKILLS_BY_CLASS.get(hero_class, PASSIVE_SKILLS_BY_CLASS["DPS"])

    # 1-2★: 1 active skill
    if rarity >= 1:
        skills["active_1"] = {**element_actives[0]}

    # 3★: +1 passive
    if rarity >= 3:
        skills["passive_1"] = class_passives[0]

    # 4★: +2nd active (alternating)
    if rarity >= 4:
        skills["active_2"] = {**(element_actives[1] if len(element_actives) > 1 else element_actives[0])}

    # 5★: +2nd passive + unique item
    if rarity >= 5:
        skills["passive_2"] = class_passives[1] if len(class_passives) > 1 else class_passives[0]

    # 6★: Ultimate
    if rarity >= 6:
        skills["ultimate"] = {**ULTIMATE_SKILLS_BY_ELEMENT.get(element, {})} if ULTIMATE_SKILLS_BY_ELEMENT.get(element) else None

    # 7-9★: Enhanced skills
    if rarity >= 7:
        enhance_mult = 1 + (min(rarity, 9) - 6) * 0.15  # +15% per star
        for key in ["active_1", "active_2"]:
            if skills[key] and "damage_mult" in skills[key]:
                skills[key]["damage_mult"] = round(skills[key]["damage_mult"] * enhance_mult, 2)
                skills[key]["enhanced"] = True

    # 10★: 3rd passive
    if rarity >= 10:
        skills["passive_3"] = {
            "id": "transcend_aura", "name": "Aura Trascendente", "icon": "\U0001F31F",
            "type": "passive",
            "effect": {"damage_rate": 0.10, "healing_received": 0.10, "dodge": 0.05},
            "description": "+10% Damage Rate, +10% Cure Ricevute, +5% Schivata",
        }

    # 12★: Enhanced Ultimate
    if rarity >= 12 and skills["ultimate"]:
        skills["ultimate"]["damage_mult"] = round(skills["ultimate"].get("damage_mult", 4.0) * 1.3, 2)
        skills["ultimate"]["enhanced"] = True
        skills["ultimate"]["name"] = skills["ultimate"]["name"] + " EX"

    # 15★: Transcendent bonus
    if rarity >= 15:
        skills["star_bonus"] = {
            "name": "Forma Trascendente",
            "icon": "\U0001F451",
            "description": "Tutte le skill +20% danno, +10% a tutte le stats",
            "all_skill_boost": 0.20,
            "all_stat_boost": 0.10,
        }
        for key in ["active_1", "active_2", "ultimate"]:
            if skills[key] and "damage_mult" in skills[key]:
                skills[key]["damage_mult"] = round(skills[key]["damage_mult"] * 1.2, 2)

    # Reincarnation boost to skills
    if is_reincarnated:
        for key in ["active_1", "active_2", "ultimate"]:
            if skills[key] and "damage_mult" in skills[key]:
                skills[key]["damage_mult"] = round(skills[key]["damage_mult"] * 1.2, 2)

    return skills


def register_hero_progression_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    # ==================== HERO SKILL INFO ====================
    @router.get("/hero/skills/{user_hero_id}")
    async def get_hero_skills_info(user_hero_id: str, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        uh = await db.user_heroes.find_one({"id": user_hero_id, "user_id": uid})
        if not uh:
            raise HTTPException(404, "Eroe non trovato")
        hero = await db.heroes.find_one({"id": uh["hero_id"]})
        if not hero:
            raise HTTPException(404, "Dati eroe non trovati")
        skills = get_hero_skills(
            hero.get("element", "fire"),
            hero.get("hero_class", "DPS"),
            hero.get("rarity", 1),
            uh.get("is_reincarnated", False),
        )
        level_cap = STAR_LEVEL_CAPS.get(uh.get("stars", hero.get("rarity", 1)), 30)
        return {
            "hero_name": hero.get("name"),
            "element": hero.get("element"),
            "hero_class": hero.get("hero_class"),
            "rarity": hero.get("rarity"),
            "stars": uh.get("stars", hero.get("rarity", 1)),
            "level": uh.get("level", 1),
            "level_cap": level_cap,
            "experience": uh.get("experience", 0),
            "exp_to_next": exp_for_level(uh.get("level", 1)),
            "is_reincarnated": uh.get("is_reincarnated", False),
            "reincarnation_count": uh.get("reincarnation_count", 0),
            "skills": skills,
            "skill_rules": {
                "1-2\u2B50": "1 Skill Attiva",
                "3\u2B50": "+1 Passiva permanente",
                "4\u2B50": "+2a Skill Attiva (alternanza turni)",
                "5\u2B50": "+2a Passiva permanente + Oggetto Unico",
                "6\u2B50": "Ultimate caricabile",
                "7-9\u2B50": "Skill potenziate (+15% per stella)",
                "10\u2B50": "3a Passiva: Aura Trascendente",
                "12\u2B50": "Ultimate EX potenziata (+30%)",
                "15\u2B50": "Forma Trascendente (+20% tutte le skill)",
            },
        }

    # ==================== IMPROVED LEVEL UP (battle exp) ====================
    @router.post("/hero/gain-exp")
    async def gain_battle_exp(current_user: dict = Depends(get_current_user)):
        """Called after battles - distributes EXP to team heroes."""
        uid = current_user["id"]
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        if not team or not team.get("formation"):
            return {"leveled_up": []}

        base_exp = random.randint(80, 200)
        leveled_up = []

        for pos in team.get("formation", []):
            uhid = pos.get("user_hero_id")
            if not uhid:
                continue
            uh = await db.user_heroes.find_one({"id": uhid, "user_id": uid})
            if not uh:
                continue
            hero = await db.heroes.find_one({"id": uh["hero_id"]})
            stars = uh.get("stars", hero.get("rarity", 1) if hero else 1)
            level_cap = STAR_LEVEL_CAPS.get(stars, 30)
            level = uh.get("level", 1)
            if level >= level_cap:
                continue

            exp = uh.get("experience", 0) + base_exp
            new_level = level
            while exp >= exp_for_level(new_level) and new_level < level_cap:
                exp -= exp_for_level(new_level)
                new_level += 1

            if new_level > level:
                leveled_up.append({
                    "hero_name": hero.get("name", "?") if hero else "?",
                    "old_level": level,
                    "new_level": new_level,
                })

            await db.user_heroes.update_one(
                {"id": uhid},
                {"$set": {"level": new_level, "experience": exp}}
            )

        return {"exp_gained": base_exp, "leveled_up": leveled_up}

    # ==================== REINCARNATION ====================
    @router.get("/hero/reincarnation-info/{user_hero_id}")
    async def get_reincarnation_info(user_hero_id: str, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        uh = await db.user_heroes.find_one({"id": user_hero_id, "user_id": uid})
        if not uh:
            raise HTTPException(404, "Eroe non trovato")
        hero = await db.heroes.find_one({"id": uh["hero_id"]})
        stars = uh.get("stars", hero.get("rarity", 1) if hero else 1)
        level_cap = STAR_LEVEL_CAPS.get(stars, 30)
        level = uh.get("level", 1)
        can_reincarnate = level >= level_cap and stars >= 6
        return {
            "can_reincarnate": can_reincarnate,
            "current_level": level,
            "level_cap": level_cap,
            "stars": stars,
            "is_reincarnated": uh.get("is_reincarnated", False),
            "reincarnation_count": uh.get("reincarnation_count", 0),
            "requirements": {
                "max_level": level_cap,
                "max_stars": 6,
                "items": [{"name": "Cristallo dell'Anima", "icon": "\U0001F48E", "cost": 500}],
            },
            "boost": f"+{int(REINCARNATION_BOOST * 100)}% a tutte le stats base",
        }

    class ReincarnateRequest(BaseModel):
        user_hero_id: str

    @router.post("/hero/reincarnate")
    async def reincarnate_hero(req: ReincarnateRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        uh = await db.user_heroes.find_one({"id": req.user_hero_id, "user_id": uid})
        if not uh:
            raise HTTPException(404, "Eroe non trovato")
        hero = await db.heroes.find_one({"id": uh["hero_id"]})
        if not hero:
            raise HTTPException(404, "Dati eroe non trovati")
        stars = uh.get("stars", hero.get("rarity", 1))
        level_cap = STAR_LEVEL_CAPS.get(stars, 30)
        if uh.get("level", 1) < level_cap:
            raise HTTPException(400, f"L'eroe deve essere al livello massimo ({level_cap})!")
        if stars < 6:
            raise HTTPException(400, "L'eroe deve essere almeno a 6 stelle!")
        # Check gems for soul crystal
        user = await db.users.find_one({"id": uid})
        cost = 500
        if user.get("gems", 0) < cost:
            raise HTTPException(400, f"Servono {cost} gemme per il Cristallo dell'Anima!")
        await db.users.update_one({"id": uid}, {"$inc": {"gems": -cost}})

        # Apply reincarnation
        reinc_count = uh.get("reincarnation_count", 0) + 1
        boost = 1 + REINCARNATION_BOOST * reinc_count  # Cumulative boost

        # Boost base stats in hero document (permanent per-user-hero)
        base_stats = hero.get("base_stats", {})
        boosted_stats = {}
        for k, v in base_stats.items():
            if isinstance(v, (int, float)):
                boosted_stats[k] = round(v * (1 + REINCARNATION_BOOST), 3) if isinstance(v, float) else int(v * (1 + REINCARNATION_BOOST))

        await db.user_heroes.update_one(
            {"id": req.user_hero_id},
            {"$set": {
                "level": 1,
                "experience": 0,
                "is_reincarnated": True,
                "reincarnation_count": reinc_count,
                "boosted_stats": boosted_stats,
                "reincarnated_at": datetime.utcnow(),
            }}
        )

        return {
            "success": True,
            "hero_name": hero.get("name"),
            "reincarnation_count": reinc_count,
            "stat_boost": f"+{int(REINCARNATION_BOOST * 100)}%",
            "message": f"{hero.get('name')} si e reincarnata! Statistiche potenziate del {int(REINCARNATION_BOOST * 100)}%.",
        }

    # ==================== FRAGMENTS ====================
    @router.get("/fragments")
    async def get_fragments(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        user_frags = await db.user_fragments.find_one({"user_id": uid})
        if not user_frags:
            user_frags = {"user_id": uid, "green": 0, "blue": 0, "purple": 0, "orange": 0, "gold": 0}
            await db.user_fragments.insert_one(user_frags)
        result = []
        for ft in FRAGMENT_TYPES:
            count = user_frags.get(ft["id"], 0)
            can_combine = count >= ft["required"]
            result.append({
                **ft,
                "count": count,
                "can_combine": can_combine,
                "progress": f"{count}/{ft['required']}",
            })
        return {"fragments": result}

    class CombineFragmentsRequest(BaseModel):
        fragment_type: str

    @router.post("/fragments/combine")
    async def combine_fragments(req: CombineFragmentsRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        ft = next((f for f in FRAGMENT_TYPES if f["id"] == req.fragment_type), None)
        if not ft:
            raise HTTPException(404, "Tipo frammento non valido")
        user_frags = await db.user_fragments.find_one({"user_id": uid})
        if not user_frags or user_frags.get(req.fragment_type, 0) < ft["required"]:
            raise HTTPException(400, f"Servono {ft['required']} frammenti {ft['name']}!")
        # Deduct fragments
        await db.user_fragments.update_one({"user_id": uid}, {"$inc": {req.fragment_type: -ft["required"]}})
        # Give random hero of that rarity
        heroes = await db.heroes.find({"rarity": ft["hero_rarity"]}).to_list(100)
        if not heroes:
            heroes = await db.heroes.find({}).to_list(100)
        hero = random.choice(heroes)
        user_hero = {
            "id": str(uuid.uuid4()), "user_id": uid, "hero_id": hero["id"],
            "level": 1, "experience": 0, "stars": hero["rarity"],
            "obtained_at": datetime.utcnow(), "source": "fragments",
        }
        await db.user_heroes.insert_one(user_hero)
        return {
            "success": True,
            "hero": serialize_doc(hero),
            "hero_name": hero.get("name"),
            "rarity": hero.get("rarity"),
        }

    @router.post("/fragments/add")
    async def add_fragments(current_user: dict = Depends(get_current_user)):
        """Debug/reward endpoint to add fragments."""
        uid = current_user["id"]
        # Add some random fragments
        adds = {}
        for ft in FRAGMENT_TYPES:
            amount = random.randint(1, 5)
            adds[ft["id"]] = amount
        await db.user_fragments.update_one({"user_id": uid}, {"$inc": adds}, upsert=True)
        return {"success": True, "added": adds}

    # ==================== SHOP REINCARNATION ITEMS ====================
    @router.get("/shop/reincarnation")
    async def get_reincarnation_shop():
        return {"items": REINCARNATION_ITEMS}

    # ==================== HERO DETAIL WITH ALL SYSTEMS ====================
    @router.get("/hero/full-detail/{user_hero_id}")
    async def get_hero_full_detail(user_hero_id: str, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        uh = await db.user_heroes.find_one({"id": user_hero_id, "user_id": uid})
        if not uh:
            raise HTTPException(404, "Eroe non trovato")
        hero = await db.heroes.find_one({"id": uh["hero_id"]})
        if not hero:
            raise HTTPException(404, "Dati eroe non trovati")

        stars = uh.get("stars", hero.get("rarity", 1))
        level = uh.get("level", 1)
        level_cap = STAR_LEVEL_CAPS.get(stars, 30)
        is_reinc = uh.get("is_reincarnated", False)

        # Use boosted stats if reincarnated
        base_stats = uh.get("boosted_stats") if is_reinc and uh.get("boosted_stats") else hero.get("base_stats", {})

        # Apply level multiplier to stats
        level_mult = 1 + (level - 1) * 0.05
        effective_stats = {}
        for k, v in base_stats.items():
            if isinstance(v, int):
                effective_stats[k] = int(v * level_mult)
            elif isinstance(v, float):
                effective_stats[k] = round(v * (1 + (level - 1) * 0.01), 3)
            else:
                effective_stats[k] = v

        skills = get_hero_skills(
            hero.get("element", "fire"),
            hero.get("hero_class", "DPS"),
            stars,
            is_reinc,
        )

        can_reincarnate = level >= level_cap and stars >= 6

        return {
            "hero_id": hero.get("id"),
            "user_hero_id": uh["id"],
            "name": hero.get("name"),
            "element": hero.get("element"),
            "hero_class": hero.get("hero_class"),
            "rarity": hero.get("rarity"),
            "stars": stars,
            "level": level,
            "level_cap": level_cap,
            "experience": uh.get("experience", 0),
            "exp_to_next": exp_for_level(level) if level < level_cap else 0,
            "exp_progress": min(1.0, uh.get("experience", 0) / max(1, exp_for_level(level))),
            "is_reincarnated": is_reinc,
            "reincarnation_count": uh.get("reincarnation_count", 0),
            "can_reincarnate": can_reincarnate,
            "image": hero.get("image_url") or hero.get("image_base64") or hero.get("image"),
            "base_stats": base_stats,
            "effective_stats": effective_stats,
            "skills": skills,
            "power": calculate_hero_power(hero, uh),
        }

    # ==================== ENCYCLOPEDIA (catalog base hero, not instance) ====================
    @router.get("/hero/encyclopedia/{hero_id}")
    async def get_hero_encyclopedia(hero_id: str):
        """Encyclopedia-style view for the Hero Collection.
        Returns BOTH a 'base' (Lv 1, base stars) and 'max' (Lv 100 ref, max stars
        actually reachable for this hero's base rarity) projection.
        No user_heroes instance required — works for unowned heroes too.
        """
        hero = await db.heroes.find_one({"id": hero_id})
        if not hero:
            raise HTTPException(status_code=404, detail="Eroe non trovato")

        base_rarity = hero.get("rarity", 1)
        base_stats = hero.get("base_stats", {}) or {}
        element = hero.get("element", "fire")
        hero_class = hero.get("hero_class", "DPS")

        # ---- BASE projection ----
        base_level = 1
        base_stars = base_rarity
        base_level_cap = STAR_LEVEL_CAPS.get(base_stars, 30)
        base_effective_stats = dict(base_stats)  # at lv 1, multiplier = 1
        base_skills = get_hero_skills(element, hero_class, base_stars, False)

        # ---- MAX projection ----
        # Target: Lv 100 reference, stelle = massimo realmente raggiungibile per la base rarity
        max_stars = MAX_STARS_BY_BASE.get(base_rarity, 6)
        max_star_cap = STAR_LEVEL_CAPS.get(max_stars, 30)
        # L'utente ha chiesto Lv 100 come riferimento, limitato al cap reale
        max_level = min(100, max_star_cap)
        level_mult_int = 1 + (max_level - 1) * 0.05
        max_effective_stats = {}
        for k, v in base_stats.items():
            if isinstance(v, bool):
                max_effective_stats[k] = v
            elif isinstance(v, int):
                max_effective_stats[k] = int(v * level_mult_int)
            elif isinstance(v, float):
                max_effective_stats[k] = round(v * (1 + (max_level - 1) * 0.01), 3)
            else:
                max_effective_stats[k] = v
        max_skills = get_hero_skills(element, hero_class, max_stars, False)

        # Power preview (usa stars+level del profilo MAX)
        try:
            max_power = calculate_hero_power(hero, {"stars": max_stars, "level": max_level})
        except Exception:
            max_power = None
        try:
            base_power = calculate_hero_power(hero, {"stars": base_stars, "level": base_level})
        except Exception:
            base_power = None

        return {
            "hero_id": hero.get("id"),
            "name": hero.get("name"),
            "description": hero.get("description"),
            "element": element,
            "hero_class": hero_class,
            "rarity": base_rarity,
            "faction": hero.get("faction"),
            "image": hero.get("image_url") or hero.get("image_base64") or hero.get("image"),
            "base": {
                "level": base_level,
                "level_cap": base_level_cap,
                "stars": base_stars,
                "stats": base_effective_stats,
                "skills": base_skills,
                "power": base_power,
            },
            "max": {
                "level": max_level,
                "level_cap": max_star_cap,
                "stars": max_stars,
                "stats": max_effective_stats,
                "skills": max_skills,
                "power": max_power,
            },
        }

    # ==================== STAR FUSION SYSTEM (Hokage Crisis style) ====================
    @router.get("/fusion/info/{user_hero_id}")
    async def get_fusion_info(user_hero_id: str, current_user: dict = Depends(get_current_user)):
        """Get fusion requirements for upgrading a hero's stars."""
        uid = current_user["id"]
        uh = await db.user_heroes.find_one({"id": user_hero_id, "user_id": uid})
        if not uh:
            raise HTTPException(404, "Eroe non trovato")
        hero = await db.heroes.find_one({"id": uh["hero_id"]})
        if not hero:
            raise HTTPException(404, "Dati eroe non trovati")

        current_stars = uh.get("stars", hero.get("rarity", 1))
        base_rarity = hero.get("rarity", 1)
        max_reachable = MAX_STARS_BY_BASE.get(base_rarity, 6)
        target_stars = current_stars + 1

        if current_stars >= max_reachable:
            return {
                "can_fuse": False,
                "reason": f"Stelle massime raggiunte ({max_reachable}\u2B50) per un eroe base {base_rarity}\u2B50",
                "current_stars": current_stars,
                "max_stars": max_reachable,
                "hero_name": hero.get("name"),
            }

        # Get requirements
        if target_stars <= 6:
            reqs = LOW_STAR_FUSION_REQS.get(target_stars)
            if not reqs:
                return {"can_fuse": False, "reason": "Requisiti non trovati"}
            same_needed = reqs["same_copies"]
            any_needed = reqs["any_copies"]
            gold_needed = reqs["gold"]
            material_name = None
            material_count = 0
            any_5plus = 0
        else:
            reqs = STAR_FUSION_REQS.get(target_stars)
            if not reqs:
                return {"can_fuse": False, "reason": "Requisiti non trovati"}
            same_needed = reqs["same_copies"]
            any_needed = 0
            any_5plus = reqs.get("any_5plus", 0)
            gold_needed = reqs["gold"]
            material_name = reqs.get("material")
            material_count = reqs.get("material_count", 0)

        # Count available duplicates
        same_copies = await db.user_heroes.count_documents({
            "user_id": uid, "hero_id": hero["id"], "id": {"$ne": user_hero_id}
        })

        # Count available 5★+ heroes (excluding base)
        five_plus_count = await db.user_heroes.count_documents({
            "user_id": uid, "stars": {"$gte": 5}, "id": {"$ne": user_hero_id}
        })

        # Count any heroes for fodder (low star fusions)
        any_hero_count = await db.user_heroes.count_documents({
            "user_id": uid, "id": {"$ne": user_hero_id}
        })

        # Check user gold
        user = await db.users.find_one({"id": uid})
        user_gold = user.get("gold", 0)

        # Check materials
        user_mats = await db.user_materials.find_one({"user_id": uid}) or {}
        user_mat_count = user_mats.get(material_name, 0) if material_name else 0

        # Build requirements list
        requirements = []
        requirements.append({
            "type": "same_hero", "name": f"Copie di {hero.get('name')}", "icon": "\U0001F465",
            "needed": same_needed, "have": same_copies, "met": same_copies >= same_needed,
        })
        if any_needed > 0:
            requirements.append({
                "type": "any_hero", "name": "Eroi qualsiasi (sacrificio)", "icon": "\U0001F464",
                "needed": any_needed, "have": any_hero_count, "met": any_hero_count >= any_needed,
            })
        if any_5plus > 0:
            requirements.append({
                "type": "five_plus", "name": "Eroi 5\u2B50+ (sacrificio)", "icon": "\u2B50",
                "needed": any_5plus, "have": five_plus_count, "met": five_plus_count >= any_5plus,
            })
        requirements.append({
            "type": "gold", "name": "Oro", "icon": "\U0001F4B0",
            "needed": gold_needed, "have": user_gold, "met": user_gold >= gold_needed,
        })
        if material_name and material_count > 0:
            mat_info = FUSION_MATERIALS.get(material_name, {})
            requirements.append({
                "type": "material", "name": mat_info.get("name", material_name), "icon": mat_info.get("icon", "\u2728"),
                "needed": material_count, "have": user_mat_count, "met": user_mat_count >= material_count,
            })

        can_fuse = all(r["met"] for r in requirements)

        return {
            "can_fuse": can_fuse,
            "hero_name": hero.get("name"),
            "current_stars": current_stars,
            "target_stars": target_stars,
            "max_stars": max_reachable,
            "base_rarity": base_rarity,
            "requirements": requirements,
            "materials_info": FUSION_MATERIALS,
        }

    class StarFusionRequest(BaseModel):
        user_hero_id: str
        fodder_same_ids: list = []  # IDs of same-hero duplicates to sacrifice
        fodder_any_ids: list = []   # IDs of any heroes to sacrifice (for low star fusions)
        fodder_5plus_ids: list = [] # IDs of 5★+ heroes to sacrifice

    @router.post("/fusion/star-up")
    async def star_fusion(req: StarFusionRequest, current_user: dict = Depends(get_current_user)):
        """Fuse heroes to increase stars (Hokage Crisis style)."""
        uid = current_user["id"]
        uh = await db.user_heroes.find_one({"id": req.user_hero_id, "user_id": uid})
        if not uh:
            raise HTTPException(404, "Eroe non trovato")
        hero = await db.heroes.find_one({"id": uh["hero_id"]})
        if not hero:
            raise HTTPException(404, "Dati eroe non trovati")

        current_stars = uh.get("stars", hero.get("rarity", 1))
        base_rarity = hero.get("rarity", 1)
        max_reachable = MAX_STARS_BY_BASE.get(base_rarity, 6)
        target_stars = current_stars + 1

        if current_stars >= max_reachable:
            raise HTTPException(400, f"Stelle massime ({max_reachable}) raggiunte!")

        # Get requirements
        if target_stars <= 6:
            reqs = LOW_STAR_FUSION_REQS.get(target_stars)
            if not reqs:
                raise HTTPException(400, "Fusione non disponibile")
            same_needed = reqs["same_copies"]
            any_needed = reqs["any_copies"]
            gold_needed = reqs["gold"]
            any_5plus = 0
            material_name = None
            material_count = 0
        else:
            reqs = STAR_FUSION_REQS.get(target_stars)
            if not reqs:
                raise HTTPException(400, "Fusione non disponibile")
            same_needed = reqs["same_copies"]
            any_needed = 0
            any_5plus = reqs.get("any_5plus", 0)
            gold_needed = reqs["gold"]
            material_name = reqs.get("material")
            material_count = reqs.get("material_count", 0)

        # Auto-select fodder if not provided (Hokage Crisis style - automatic)
        if not req.fodder_same_ids and same_needed > 0:
            same_copies = await db.user_heroes.find({
                "user_id": uid,
                "hero_id": hero["id"],
                "id": {"$ne": req.user_hero_id}
            }).sort("level", 1).to_list(length=same_needed)
            req.fodder_same_ids = [c["id"] for c in same_copies]
        
        if not req.fodder_any_ids and any_needed > 0:
            exclude_ids = [req.user_hero_id] + req.fodder_same_ids
            any_heroes = await db.user_heroes.find({
                "user_id": uid,
                "id": {"$nin": exclude_ids}
            }).sort("stars", 1).to_list(length=any_needed)
            req.fodder_any_ids = [c["id"] for c in any_heroes]
        
        if not req.fodder_5plus_ids and any_5plus > 0:
            exclude_ids = [req.user_hero_id] + req.fodder_same_ids + req.fodder_any_ids
            five_plus = await db.user_heroes.find({
                "user_id": uid,
                "id": {"$nin": exclude_ids},
                "stars": {"$gte": 5}
            }).sort("stars", 1).to_list(length=any_5plus)
            req.fodder_5plus_ids = [c["id"] for c in five_plus]

        # Validate fodder - same hero copies
        if len(req.fodder_same_ids) < same_needed:
            raise HTTPException(400, f"Servono {same_needed} copie dello stesso eroe!")
        for fid in req.fodder_same_ids[:same_needed]:
            fodder = await db.user_heroes.find_one({"id": fid, "user_id": uid})
            if not fodder:
                raise HTTPException(404, f"Copia {fid} non trovata")
            if fodder.get("hero_id") != hero["id"]:
                raise HTTPException(400, "Le copie devono essere dello STESSO eroe!")
            if fid == req.user_hero_id:
                raise HTTPException(400, "Non puoi sacrificare l'eroe base!")

        # Validate fodder - any heroes (low star)
        if any_needed > 0 and len(req.fodder_any_ids) < any_needed:
            raise HTTPException(400, f"Servono {any_needed} eroi qualsiasi da sacrificare!")
        for fid in req.fodder_any_ids[:any_needed]:
            fodder = await db.user_heroes.find_one({"id": fid, "user_id": uid})
            if not fodder:
                raise HTTPException(404, f"Eroe {fid} non trovato")
            if fid == req.user_hero_id:
                raise HTTPException(400, "Non puoi sacrificare l'eroe base!")

        # Validate fodder - 5★+ heroes
        if any_5plus > 0 and len(req.fodder_5plus_ids) < any_5plus:
            raise HTTPException(400, f"Servono {any_5plus} eroi 5\u2B50+ da sacrificare!")
        for fid in req.fodder_5plus_ids[:any_5plus]:
            fodder = await db.user_heroes.find_one({"id": fid, "user_id": uid, "stars": {"$gte": 5}})
            if not fodder:
                raise HTTPException(400, f"Eroe 5\u2B50+ {fid} non trovato o non qualificato!")
            if fid == req.user_hero_id:
                raise HTTPException(400, "Non puoi sacrificare l'eroe base!")

        # Check gold
        user = await db.users.find_one({"id": uid})
        if user.get("gold", 0) < gold_needed:
            raise HTTPException(400, f"Servono {gold_needed:,} oro!")

        # Check materials
        if material_name and material_count > 0:
            user_mats = await db.user_materials.find_one({"user_id": uid}) or {}
            if user_mats.get(material_name, 0) < material_count:
                mat_info = FUSION_MATERIALS.get(material_name, {})
                raise HTTPException(400, f"Servono {material_count}x {mat_info.get('name', material_name)}!")

        # === Execute fusion ===
        # Remove fodder heroes
        all_fodder = req.fodder_same_ids[:same_needed] + req.fodder_any_ids[:any_needed] + req.fodder_5plus_ids[:any_5plus]
        for fid in all_fodder:
            await db.user_heroes.delete_one({"id": fid, "user_id": uid})

        # Deduct gold
        await db.users.update_one({"id": uid}, {"$inc": {"gold": -gold_needed}})

        # Deduct materials
        if material_name and material_count > 0:
            await db.user_materials.update_one(
                {"user_id": uid},
                {"$inc": {material_name: -material_count}}
            )

        # Upgrade stars
        await db.user_heroes.update_one(
            {"id": req.user_hero_id},
            {"$set": {"stars": target_stars, "fused_at": datetime.utcnow()}}
        )

        # Calculate new level cap
        new_level_cap = STAR_LEVEL_CAPS.get(target_stars, 350)

        return {
            "success": True,
            "hero_name": hero.get("name"),
            "old_stars": current_stars,
            "new_stars": target_stars,
            "new_level_cap": new_level_cap,
            "max_stars": max_reachable,
            "fodder_consumed": len(all_fodder),
            "gold_spent": gold_needed,
            "material_spent": {material_name: material_count} if material_name else {},
        }

    # ==================== FUSION MATERIALS SHOP ====================
    @router.get("/materials")
    async def get_materials(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        user_mats = await db.user_materials.find_one({"user_id": uid})
        if not user_mats:
            user_mats = {"user_id": uid}
            await db.user_materials.insert_one(user_mats)
        result = []
        for mat_id, mat_info in FUSION_MATERIALS.items():
            result.append({
                "id": mat_id,
                **mat_info,
                "owned": user_mats.get(mat_id, 0),
            })
        return {"materials": result}

    class BuyMaterialRequest(BaseModel):
        material_id: str
        quantity: int = 1

    @router.post("/materials/buy")
    async def buy_material(req: BuyMaterialRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        mat = FUSION_MATERIALS.get(req.material_id)
        if not mat:
            raise HTTPException(404, "Materiale non trovato")
        total_cost = mat["shop_cost_gems"] * req.quantity
        user = await db.users.find_one({"id": uid})
        if user.get("gems", 0) < total_cost:
            raise HTTPException(400, f"Servono {total_cost} gemme!")
        await db.users.update_one({"id": uid}, {"$inc": {"gems": -total_cost}})
        await db.user_materials.update_one(
            {"user_id": uid},
            {"$inc": {req.material_id: req.quantity}},
            upsert=True
        )
        return {"success": True, "material": mat["name"], "quantity": req.quantity, "gems_spent": total_cost}

    # ==================== STAR FUSION GUIDE ====================
    @router.get("/fusion/guide")
    async def get_fusion_guide():
        """Get the full star fusion requirements table."""
        guide = {
            "max_stars_by_base": MAX_STARS_BY_BASE,
            "low_star_requirements": {},
            "high_star_requirements": {},
            "materials": FUSION_MATERIALS,
        }
        for star, reqs in LOW_STAR_FUSION_REQS.items():
            guide["low_star_requirements"][str(star)] = {
                "target": f"{star}\u2B50",
                "same_copies": reqs["same_copies"],
                "any_fodder": reqs["any_copies"],
                "gold": reqs["gold"],
            }
        for star, reqs in STAR_FUSION_REQS.items():
            mat = FUSION_MATERIALS.get(reqs.get("material", ""), {})
            guide["high_star_requirements"][str(star)] = {
                "target": f"{star}\u2B50",
                "same_copies": reqs["same_copies"],
                "five_plus_fodder": reqs.get("any_5plus", 0),
                "gold": reqs["gold"],
                "material": mat.get("name") if reqs.get("material") else None,
                "material_count": reqs.get("material_count", 0),
            }
        return guide

