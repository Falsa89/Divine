"""
Divine Waifus - Unique Items System
Each hero 5★+ unlocks an exclusive item only they can equip.
Items boost stats significantly and enhance abilities.
"""
import uuid
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel

# ===================== UNIQUE ITEMS FOR ALL 30 HEROES =====================
UNIQUE_ITEMS = {
    # 6★ heroes - Legendary items
    "Amaterasu": {
        "name": "Specchio Sacro di Yata", "icon": "\U0001FA9E", "rarity": 6,
        "stats": {"magic_damage": 800, "crit_chance": 0.15, "crit_damage": 0.5, "hit_rate": 0.08},
        "skill_boost": {"active_1_mult": 1.3, "ultimate_mult": 1.25},
        "description": "Lo specchio che riflette la verita divina. Potenzia enormemente la magia di Amaterasu.",
    },
    "Tsukuyomi": {
        "name": "Lama della Luna Eterna", "icon": "\U0001F319", "rarity": 6,
        "stats": {"physical_damage": 900, "crit_chance": 0.20, "penetration": 0.12, "speed": 25},
        "skill_boost": {"active_1_mult": 1.35, "ultimate_mult": 1.3},
        "description": "Una lama forgiata nell'oscurita eterna della luna. Letale e precisa.",
    },
    "Susanoo": {
        "name": "Kusanagi no Tsurugi", "icon": "\u2694\uFE0F", "rarity": 6,
        "stats": {"physical_damage": 600, "physical_defense": 400, "hp": 3000, "block_rate": 0.10},
        "skill_boost": {"active_1_mult": 1.25, "ultimate_mult": 1.2},
        "description": "La leggendaria spada che taglia anche le tempeste.",
    },
    "Izanami": {
        "name": "Velo dell'Oltretomba", "icon": "\U0001F47B", "rarity": 6,
        "stats": {"healing": 800, "magic_defense": 400, "hp": 2500, "healing_received": 0.20},
        "skill_boost": {"active_1_mult": 1.3, "passive_boost": 0.15},
        "description": "Un velo che connette il mondo dei vivi e dei morti.",
    },
    # 5★ heroes
    "Athena": {
        "name": "Egida Impenetrabile", "icon": "\U0001F6E1\uFE0F", "rarity": 5,
        "stats": {"physical_defense": 500, "magic_defense": 350, "hp": 2000, "block_rate": 0.12},
        "skill_boost": {"passive_boost": 0.20},
        "description": "Lo scudo della dea della saggezza, impenetrabile.",
    },
    "Aphrodite": {
        "name": "Cintura dell'Amore", "icon": "\U0001F49D", "rarity": 5,
        "stats": {"healing": 700, "speed": 30, "hp": 1800, "healing_received": 0.15},
        "skill_boost": {"active_1_mult": 1.25},
        "description": "La cintura che incanta e guarisce.",
    },
    "Artemis": {
        "name": "Arco d'Argento Lunare", "icon": "\U0001F3F9", "rarity": 5,
        "stats": {"physical_damage": 600, "crit_chance": 0.18, "speed": 35, "combo_rate": 0.10},
        "skill_boost": {"active_1_mult": 1.3},
        "description": "L'arco della cacciatrice, non manca mai il bersaglio.",
    },
    "Freya": {
        "name": "Collana Brisingamen", "icon": "\U0001F4FF", "rarity": 5,
        "stats": {"magic_damage": 500, "crit_damage": 0.40, "crit_chance": 0.12, "combo_rate": 0.08},
        "skill_boost": {"active_1_mult": 1.25},
        "description": "Il gioiello piu prezioso di tutti i nove mondi.",
    },
    "Valkyrie": {
        "name": "Lancia del Valhalla", "icon": "\U0001F531", "rarity": 5,
        "stats": {"physical_damage": 400, "hp": 2500, "physical_defense": 300, "damage_rate": 0.10},
        "skill_boost": {"active_1_mult": 1.2},
        "description": "La lancia che sceglie i guerrieri degni del Valhalla.",
    },
    "Medusa": {
        "name": "Sguardo Pietrificante", "icon": "\U0001F440", "rarity": 5,
        "stats": {"magic_damage": 550, "penetration": 0.15, "crit_chance": 0.10, "dodge": 0.08},
        "skill_boost": {"active_1_mult": 1.3},
        "description": "Il potere di trasformare in pietra con lo sguardo.",
    },
    # 4★ heroes
    "Hera": {
        "name": "Corona della Regina", "icon": "\U0001F451", "rarity": 4,
        "stats": {"healing": 500, "magic_defense": 250, "hp": 1500, "speed": 15},
        "skill_boost": {"passive_boost": 0.15},
        "description": "La corona della regina degli dei, fonte di potere curativo.",
    },
    "Persephone": {
        "name": "Melograno degli Inferi", "icon": "\U0001F34E", "rarity": 4,
        "stats": {"magic_damage": 400, "penetration": 0.10, "crit_chance": 0.08, "hp": 800},
        "skill_boost": {"active_1_mult": 1.2},
        "description": "Il frutto proibito che dona potere dall'oltretomba.",
    },
    "Nyx": {
        "name": "Mantello della Notte", "icon": "\U0001F30C", "rarity": 4,
        "stats": {"magic_damage": 450, "dodge": 0.12, "speed": 20, "crit_damage": 0.20},
        "skill_boost": {"active_1_mult": 1.2},
        "description": "Il mantello stellato della notte, avvolge nell'ombra.",
    },
    "Demeter": {
        "name": "Falce della Mietitura", "icon": "\U0001F33E", "rarity": 4,
        "stats": {"healing": 450, "hp": 1200, "physical_defense": 200, "healing_received": 0.12},
        "skill_boost": {"passive_boost": 0.12},
        "description": "La falce che porta vita e raccolto abbondante.",
    },
    "Hecate": {
        "name": "Torcia Triforme", "icon": "\U0001F525", "rarity": 4,
        "stats": {"magic_damage": 420, "crit_damage": 0.25, "penetration": 0.08, "hit_rate": 0.05},
        "skill_boost": {"active_1_mult": 1.2},
        "description": "La torcia magica che illumina tre mondi.",
    },
    "Selene": {
        "name": "Tiara Lunare", "icon": "\U0001F319", "rarity": 4,
        "stats": {"healing": 400, "speed": 20, "magic_defense": 200, "dodge": 0.06},
        "skill_boost": {"passive_boost": 0.12},
        "description": "La tiara della luna, fonte di luce curativa.",
    },
    # 3★ heroes
    "Sakuya": {
        "name": "Ventaglio dei Fiori", "icon": "\U0001F338", "rarity": 3,
        "stats": {"healing": 300, "speed": 15, "dodge": 0.08, "magic_defense": 150},
        "skill_boost": {"passive_boost": 0.10},
        "description": "Un ventaglio che disperde petali curativi.",
    },
    "Kaguya": {
        "name": "Gioiello Lunare", "icon": "\U0001F48E", "rarity": 3,
        "stats": {"magic_damage": 300, "crit_chance": 0.08, "hit_rate": 0.05, "speed": 10},
        "skill_boost": {"active_1_mult": 1.15},
        "description": "Il gioiello della principessa della luna.",
    },
    "Inari": {
        "name": "Zanna della Volpe", "icon": "\U0001F98A", "rarity": 3,
        "stats": {"physical_damage": 280, "combo_rate": 0.12, "speed": 15, "crit_chance": 0.06},
        "skill_boost": {"active_1_mult": 1.15},
        "description": "Una zanna incantata della volpe divina.",
    },
    "Benzaiten": {
        "name": "Biwa Celeste", "icon": "\U0001F3B6", "rarity": 3,
        "stats": {"healing": 280, "magic_damage": 150, "speed": 12, "healing_received": 0.08},
        "skill_boost": {"passive_boost": 0.10},
        "description": "Lo strumento sacro della dea della musica.",
    },
    "Raijin": {
        "name": "Tamburo del Tuono", "icon": "\U0001F941", "rarity": 3,
        "stats": {"physical_damage": 320, "speed": 18, "combo_rate": 0.10, "damage_rate": 0.06},
        "skill_boost": {"active_1_mult": 1.15},
        "description": "Il tamburo che scatena tempeste elettriche.",
    },
    "Fujin": {
        "name": "Sacco dei Venti", "icon": "\U0001F4A8", "rarity": 3,
        "stats": {"speed": 25, "dodge": 0.10, "physical_defense": 180, "hp": 800},
        "skill_boost": {"passive_boost": 0.10},
        "description": "Il sacco che contiene tutti i venti del mondo.",
    },
    # 2★ heroes
    "Iris": {
        "name": "Arcobaleno Messaggero", "icon": "\U0001F308", "rarity": 2,
        "stats": {"healing": 200, "speed": 15, "magic_defense": 100, "hp": 500},
        "skill_boost": {"passive_boost": 0.08},
        "description": "L'arcobaleno che porta messaggi divini e guarigione.",
    },
    "Echo": {
        "name": "Eco Risonante", "icon": "\U0001F50A", "rarity": 2,
        "stats": {"speed": 18, "combo_rate": 0.10, "physical_damage": 180, "dodge": 0.06},
        "skill_boost": {"active_1_mult": 1.10},
        "description": "Un cristallo che amplifica ogni suono in attacco.",
    },
    "Daphne": {
        "name": "Radici di Alloro", "icon": "\U0001F333", "rarity": 2,
        "stats": {"hp": 800, "physical_defense": 150, "block_rate": 0.08, "healing_received": 0.06},
        "skill_boost": {"passive_boost": 0.08},
        "description": "Le radici eterne dell'alloro sacro.",
    },
    "Chloris": {
        "name": "Seme Primordiale", "icon": "\U0001F331", "rarity": 2,
        "stats": {"healing": 180, "hp": 600, "magic_defense": 80, "healing_received": 0.06},
        "skill_boost": {"passive_boost": 0.08},
        "description": "Il seme da cui nasce ogni forma di vita.",
    },
    # 1★ heroes
    "Aura": {
        "name": "Brezza Leggera", "icon": "\U0001F343", "rarity": 1,
        "stats": {"speed": 12, "dodge": 0.06, "physical_damage": 100},
        "skill_boost": {"active_1_mult": 1.08},
        "description": "Una brezza che accelera i movimenti.",
    },
    "Hestia": {
        "name": "Fiamma del Focolare", "icon": "\U0001F56F\uFE0F", "rarity": 1,
        "stats": {"healing": 120, "hp": 400, "magic_defense": 60},
        "skill_boost": {"passive_boost": 0.06},
        "description": "La fiamma eterna del focolare domestico.",
    },
    "Nike": {
        "name": "Ali della Vittoria", "icon": "\U0001F3C6", "rarity": 1,
        "stats": {"physical_defense": 100, "block_rate": 0.06, "hp": 350},
        "skill_boost": {"passive_boost": 0.06},
        "description": "Le ali che portano alla vittoria.",
    },
    "Psyche": {
        "name": "Farfalla dell'Anima", "icon": "\U0001F98B", "rarity": 1,
        "stats": {"healing": 100, "speed": 8, "healing_received": 0.05},
        "skill_boost": {"passive_boost": 0.06},
        "description": "Una farfalla mistica che cura l'anima.",
    },
}


def register_unique_items_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    @router.get("/unique-items")
    async def get_all_unique_items(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        user_heroes = await db.user_heroes.find({"user_id": uid}).to_list(500)
        hero_ids = [uh["hero_id"] for uh in user_heroes]
        heroes = await db.heroes.find({"id": {"$in": hero_ids}}).to_list(100)
        hero_map = {h["id"]: h for h in heroes}
        # Get hero names the user owns
        owned_names = set()
        hero_stars = {}
        for uh in user_heroes:
            h = hero_map.get(uh["hero_id"])
            if h:
                name = h["name"]
                owned_names.add(name)
                stars = uh.get("stars", h.get("rarity", 1))
                hero_stars[name] = max(hero_stars.get(name, 0), stars)
        # Get crafted items
        crafted = await db.unique_items_crafted.find({"user_id": uid}).to_list(100)
        crafted_names = {c["hero_name"] for c in crafted}
        equipped = await db.unique_items_equipped.find({"user_id": uid}).to_list(100)
        equipped_map = {e["hero_name"]: e for e in equipped}

        result = []
        for hero_name, item in UNIQUE_ITEMS.items():
            owned = hero_name in owned_names
            stars = hero_stars.get(hero_name, 0)
            can_unlock = owned and stars >= 5
            is_crafted = hero_name in crafted_names
            is_equipped = hero_name in equipped_map
            result.append({
                "hero_name": hero_name,
                **item,
                "hero_owned": owned,
                "hero_stars": stars,
                "can_unlock": can_unlock and not is_crafted,
                "is_crafted": is_crafted,
                "is_equipped": is_equipped,
                "unlock_requirement": "Eroe a 5\u2B50+ posseduto",
            })
        return {"items": result, "total": len(UNIQUE_ITEMS), "crafted": len(crafted_names)}

    class CraftUniqueRequest(BaseModel):
        hero_name: str

    @router.post("/unique-items/craft")
    async def craft_unique_item(req: CraftUniqueRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        item = UNIQUE_ITEMS.get(req.hero_name)
        if not item:
            raise HTTPException(404, "Oggetto unico non trovato per questo eroe")
        # Check hero ownership and stars
        hero = await db.heroes.find_one({"name": req.hero_name})
        if not hero:
            raise HTTPException(404, "Eroe non trovato")
        user_heroes = await db.user_heroes.find({"user_id": uid, "hero_id": hero["id"]}).to_list(10)
        if not user_heroes:
            raise HTTPException(400, f"Non possiedi {req.hero_name}!")
        max_stars = max(uh.get("stars", 1) for uh in user_heroes)
        if max_stars < 5:
            raise HTTPException(400, f"{req.hero_name} deve essere almeno 5\u2B50! (attuale: {max_stars}\u2B50)")
        # Check not already crafted
        existing = await db.unique_items_crafted.find_one({"user_id": uid, "hero_name": req.hero_name})
        if existing:
            raise HTTPException(400, "Gia sbloccato!")
        # Cost based on rarity
        cost_gold = {1: 10000, 2: 20000, 3: 50000, 4: 100000, 5: 200000, 6: 500000}.get(item["rarity"], 50000)
        cost_gems = {1: 10, 2: 20, 3: 50, 4: 100, 5: 200, 6: 500}.get(item["rarity"], 50)
        user = await db.users.find_one({"id": uid})
        if user.get("gold", 0) < cost_gold or user.get("gems", 0) < cost_gems:
            raise HTTPException(400, f"Servono {cost_gold:,} oro e {cost_gems} gemme!")
        await db.users.update_one({"id": uid}, {"$inc": {"gold": -cost_gold, "gems": -cost_gems}})
        # Craft
        await db.unique_items_crafted.insert_one({
            "user_id": uid, "hero_name": req.hero_name, "item_name": item["name"],
            "crafted_at": datetime.utcnow(),
        })
        return {"success": True, "item": item, "hero_name": req.hero_name}

    class EquipUniqueRequest(BaseModel):
        hero_name: str
        user_hero_id: str

    @router.post("/unique-items/equip")
    async def equip_unique_item(req: EquipUniqueRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        item = UNIQUE_ITEMS.get(req.hero_name)
        if not item:
            raise HTTPException(404, "Oggetto non trovato")
        crafted = await db.unique_items_crafted.find_one({"user_id": uid, "hero_name": req.hero_name})
        if not crafted:
            raise HTTPException(400, "Oggetto non ancora sbloccato!")
        uh = await db.user_heroes.find_one({"id": req.user_hero_id, "user_id": uid})
        if not uh:
            raise HTTPException(404, "Eroe non trovato")
        hero = await db.heroes.find_one({"id": uh["hero_id"]})
        if not hero or hero.get("name") != req.hero_name:
            raise HTTPException(400, f"Questo oggetto puo essere equipaggiato SOLO da {req.hero_name}!")
        # Equip
        await db.unique_items_equipped.update_one(
            {"user_id": uid, "hero_name": req.hero_name},
            {"$set": {"user_hero_id": req.user_hero_id, "equipped_at": datetime.utcnow()}},
            upsert=True,
        )
        return {"success": True, "item": item["name"], "hero": req.hero_name}
