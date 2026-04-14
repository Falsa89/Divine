"""
Divine Waifus - Artifacts & Constellations System
Artifacts: passive team buffs on unlock, level up via duplicate fusion
Constellations: equippable, give team buff + unique skill every 3 turns
"""
import random
import uuid
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel

# ===================== ARTIFACT DEFINITIONS =====================
ARTIFACTS = [
    {"id": "holy_grail", "name": "Santo Graal", "rarity": 6, "buff": {"hp": 0.15, "defense": 0.10}, "icon": "\U0001F3C6", "description": "Il calice sacro che dona vitalita eterna ai guerrieri.", "set": "divino"},
    {"id": "mjolnir_frag", "name": "Frammento di Mjolnir", "rarity": 6, "buff": {"attack": 0.18, "crit_damage": 0.15}, "icon": "\U0001F528", "description": "Un frammento del martello del tuono, carico di energia divina.", "set": "nordico"},
    {"id": "aegis_shard", "name": "Scheggia dell'Egida", "rarity": 6, "buff": {"defense": 0.20, "hp": 0.08}, "icon": "\U0001F6E1\uFE0F", "description": "Scheggia dello scudo di Zeus, impenetrabile.", "set": "olimpico"},
    {"id": "ambrosia", "name": "Ambrosia Divina", "rarity": 5, "buff": {"hp": 0.12, "attack": 0.08}, "icon": "\U0001F36F", "description": "Il cibo degli dei che rinforza corpo e spirito.", "set": "olimpico"},
    {"id": "yata_mirror", "name": "Specchio di Yata", "rarity": 5, "buff": {"defense": 0.10, "speed": 0.10}, "icon": "\U0001FA9E", "description": "Lo specchio sacro che rivela la verita e protegge.", "set": "giapponese"},
    {"id": "golden_apple", "name": "Mela d'Oro di Idunn", "rarity": 5, "buff": {"hp": 0.15, "crit_rate": 0.05}, "icon": "\U0001F34E", "description": "La mela che dona eterna giovinezza agli Aesir.", "set": "nordico"},
    {"id": "eye_of_ra", "name": "Occhio di Ra", "rarity": 5, "buff": {"attack": 0.12, "crit_rate": 0.08}, "icon": "\U0001F441\uFE0F", "description": "L'occhio infuocato del dio sole, brucia i nemici.", "set": "egizio"},
    {"id": "lotus_jade", "name": "Loto di Giada", "rarity": 4, "buff": {"hp": 0.10, "defense": 0.06}, "icon": "\U0001F338", "description": "Un fiore mistico che emana energia protettiva.", "set": "orientale"},
    {"id": "phoenix_feather", "name": "Piuma di Fenice", "rarity": 4, "buff": {"attack": 0.08, "speed": 0.08}, "icon": "\U0001FAB6", "description": "Una piuma ardente che rinnova le forze.", "set": "mitico"},
    {"id": "dragon_scale", "name": "Scaglia di Drago", "rarity": 4, "buff": {"defense": 0.10, "crit_damage": 0.08}, "icon": "\U0001F432", "description": "Una scaglia impenetrabile di un drago ancestrale.", "set": "mitico"},
    {"id": "star_dust", "name": "Polvere di Stelle", "rarity": 4, "buff": {"speed": 0.10, "crit_rate": 0.05}, "icon": "\u2728", "description": "Polvere cosmica che accelera i movimenti.", "set": "celeste"},
    {"id": "moon_crystal", "name": "Cristallo Lunare", "rarity": 3, "buff": {"hp": 0.06, "defense": 0.04}, "icon": "\U0001F319", "description": "Un cristallo infuso con l'energia della luna.", "set": "celeste"},
    {"id": "sun_stone", "name": "Pietra Solare", "rarity": 3, "buff": {"attack": 0.06, "crit_rate": 0.03}, "icon": "\u2600\uFE0F", "description": "Una pietra calda che brucia di energia solare.", "set": "celeste"},
    {"id": "wind_chime", "name": "Campana del Vento", "rarity": 3, "buff": {"speed": 0.06, "attack": 0.03}, "icon": "\U0001F514", "description": "Una campana che risuona con la forza del vento.", "set": "orientale"},
    {"id": "earth_rune", "name": "Runa della Terra", "rarity": 2, "buff": {"defense": 0.04, "hp": 0.03}, "icon": "\U0001FAA8", "description": "Una runa antica che protegge chi la porta.", "set": "nordico"},
    {"id": "flame_shard", "name": "Frammento di Fiamma", "rarity": 2, "buff": {"attack": 0.04}, "icon": "\U0001F525", "description": "Un frammento incandescente di fuoco eterno.", "set": "mitico"},
    {"id": "water_drop", "name": "Goccia Primordiale", "rarity": 1, "buff": {"hp": 0.02}, "icon": "\U0001F4A7", "description": "Una goccia d'acqua dalle origini del mondo.", "set": "mitico"},
    {"id": "iron_coin", "name": "Moneta di Ferro", "rarity": 1, "buff": {"defense": 0.02}, "icon": "\U0001FA99", "description": "Una moneta antica dal potere modesto.", "set": "classico"},
]

# Set bonuses (activate when you own N artifacts of the same set)
ARTIFACT_SETS = {
    "divino": {"name": "Set Divino", "bonuses": {1: {"hp": 0.05}, 2: {"hp": 0.10, "attack": 0.05}}},
    "nordico": {"name": "Set Nordico", "bonuses": {1: {"attack": 0.05}, 2: {"attack": 0.10, "crit_damage": 0.10}, 3: {"attack": 0.15, "crit_damage": 0.15}}},
    "olimpico": {"name": "Set Olimpico", "bonuses": {1: {"defense": 0.05}, 2: {"defense": 0.10, "hp": 0.08}, 3: {"defense": 0.15, "hp": 0.12}}},
    "giapponese": {"name": "Set Giapponese", "bonuses": {1: {"speed": 0.05}, 2: {"speed": 0.10, "defense": 0.05}}},
    "egizio": {"name": "Set Egizio", "bonuses": {1: {"crit_rate": 0.03}, 2: {"crit_rate": 0.06, "attack": 0.08}}},
    "orientale": {"name": "Set Orientale", "bonuses": {1: {"hp": 0.03}, 2: {"hp": 0.06, "speed": 0.05}}},
    "mitico": {"name": "Set Mitico", "bonuses": {1: {"attack": 0.03}, 2: {"attack": 0.06, "defense": 0.04}, 3: {"attack": 0.10, "defense": 0.08, "hp": 0.05}}},
    "celeste": {"name": "Set Celeste", "bonuses": {1: {"speed": 0.03}, 2: {"speed": 0.06, "crit_rate": 0.04}, 3: {"speed": 0.10, "crit_rate": 0.08}}},
    "classico": {"name": "Set Classico", "bonuses": {1: {"defense": 0.02}}},
}

# ===================== CONSTELLATION DEFINITIONS (strongest to weakest) =====================
CONSTELLATIONS = [
    {
        "id": "leo", "name": "Leone", "rank": 1, "rarity": 6,
        "icon": "\u264C", "element": "fire", "color": "#ff6600",
        "buff": {"attack": 0.20, "crit_damage": 0.15},
        "skill": {"name": "Ruggito Solare", "description": "AoE fuoco devastante che infligge 250% ATK a tutti i nemici", "damage_mult": 2.5, "target": "all_enemies", "type": "fire"},
        "description": "La costellazione piu potente. Il Leone regna supremo nei cieli.",
    },
    {
        "id": "scorpio", "name": "Scorpione", "rank": 2, "rarity": 6,
        "icon": "\u264F", "element": "dark", "color": "#9944ff",
        "buff": {"crit_rate": 0.15, "crit_damage": 0.20},
        "skill": {"name": "Pungiglione Velenoso", "description": "Colpo critico garantito + veleno che infligge 80% ATK per 3 turni", "damage_mult": 2.0, "target": "single", "type": "dark"},
        "description": "Mortale e preciso. Lo Scorpione non manca mai il bersaglio.",
    },
    {
        "id": "aries", "name": "Ariete", "rank": 3, "rarity": 5,
        "icon": "\u2648", "element": "fire", "color": "#ff4444",
        "buff": {"attack": 0.15, "defense": 0.10},
        "skill": {"name": "Carica dell'Ariete", "description": "Carica devastante che infligge 200% ATK e stordisce 1 turno", "damage_mult": 2.0, "target": "single", "type": "fire"},
        "description": "Inarrestabile in battaglia. L'Ariete carica senza paura.",
    },
    {
        "id": "sagittarius", "name": "Sagittario", "rank": 4, "rarity": 5,
        "icon": "\u2650", "element": "wind", "color": "#44cc88",
        "buff": {"speed": 0.20, "attack": 0.08},
        "skill": {"name": "Freccia Stellare", "description": "Freccia perforante che ignora 50% difesa, 180% ATK", "damage_mult": 1.8, "target": "single", "type": "wind"},
        "description": "Veloce come il vento. Il Sagittario colpisce prima di tutti.",
    },
    {
        "id": "aquarius", "name": "Acquario", "rank": 5, "rarity": 5,
        "icon": "\u2652", "element": "water", "color": "#4488ff",
        "buff": {"hp": 0.20, "defense": 0.05},
        "skill": {"name": "Diluvio Celeste", "description": "Cura 30% HP max a tutto il team + 120% ATK AoE acqua", "damage_mult": 1.2, "target": "all_enemies", "type": "water"},
        "description": "Le acque celesti curano e distruggono. L'Acquario domina le maree.",
    },
    {
        "id": "capricorn", "name": "Capricorno", "rank": 6, "rarity": 5,
        "icon": "\u2651", "element": "earth", "color": "#aa8844",
        "buff": {"defense": 0.20, "hp": 0.08},
        "skill": {"name": "Barriera di Pietra", "description": "Scudo a tutto il team che assorbe 25% HP max danni per 2 turni", "damage_mult": 0, "target": "all_allies", "type": "earth"},
        "description": "Solido come la montagna. Il Capricorno protegge chi lo segue.",
    },
    {
        "id": "taurus", "name": "Toro", "rank": 7, "rarity": 4,
        "icon": "\u2649", "element": "earth", "color": "#886644",
        "buff": {"hp": 0.15, "attack": 0.10},
        "skill": {"name": "Terremoto", "description": "AoE terra che infligge 150% ATK + 30% stordimento", "damage_mult": 1.5, "target": "all_enemies", "type": "earth"},
        "description": "La forza bruta del Toro scuote la terra stessa.",
    },
    {
        "id": "gemini", "name": "Gemelli", "rank": 8, "rarity": 4,
        "icon": "\u264A", "element": "wind", "color": "#88ccff",
        "buff": {"speed": 0.15, "crit_rate": 0.10},
        "skill": {"name": "Doppio Attacco", "description": "Due colpi rapidi da 100% ATK ciascuno al bersaglio", "damage_mult": 2.0, "target": "single", "type": "wind"},
        "description": "Due anime, due colpi. I Gemelli non danno tregua.",
    },
    {
        "id": "virgo", "name": "Vergine", "rank": 9, "rarity": 4,
        "icon": "\u264D", "element": "light", "color": "#ffd700",
        "buff": {"attack": 0.08, "defense": 0.08, "speed": 0.08, "hp": 0.08},
        "skill": {"name": "Purificazione", "description": "Rimuove debuff dal team + cura 15% HP max", "damage_mult": 0, "target": "all_allies", "type": "light"},
        "description": "L'equilibrio perfetto. La Vergine armonizza ogni aspetto.",
    },
    {
        "id": "libra", "name": "Bilancia", "rank": 10, "rarity": 3,
        "icon": "\u264E", "element": "light", "color": "#ddbb44",
        "buff": {"defense": 0.10, "speed": 0.08},
        "skill": {"name": "Equilibrio Cosmico", "description": "Riduce le stats piu alte del nemico del 15% per 2 turni", "damage_mult": 0, "target": "all_enemies", "type": "light"},
        "description": "La giustizia cosmica ristabilisce l'equilibrio.",
    },
    {
        "id": "pisces", "name": "Pesci", "rank": 11, "rarity": 3,
        "icon": "\u2653", "element": "water", "color": "#66aadd",
        "buff": {"hp": 0.12, "defense": 0.06},
        "skill": {"name": "Corrente Mistica", "description": "Cura 10% HP max a tutto il team per 3 turni", "damage_mult": 0, "target": "all_allies", "type": "water"},
        "description": "Le correnti mistiche dei Pesci rinnovano le forze.",
    },
    {
        "id": "cancer", "name": "Cancro", "rank": 12, "rarity": 3,
        "icon": "\u264B", "element": "water", "color": "#5599aa",
        "buff": {"defense": 0.12, "hp": 0.08},
        "skill": {"name": "Guscio Protettivo", "description": "Riduce danni subiti del 30% per tutto il team per 2 turni", "damage_mult": 0, "target": "all_allies", "type": "water"},
        "description": "Il Cancro si ritira nella sua corazza impenetrabile.",
    },
]

# Gacha rates for artifact banner
ARTIFACT_BANNER = {
    "name": "Banner Artefatti",
    "cost_single": 120,
    "cost_multi": 1000,
    "rates": {1: 0.20, 2: 0.25, 3: 0.25, 4: 0.18, 5: 0.09, 6: 0.03},
}

CONSTELLATION_BANNER = {
    "name": "Banner Costellazioni",
    "cost_single": 200,
    "cost_multi": 1800,
    "rates": {3: 0.30, 4: 0.30, 5: 0.28, 6: 0.12},
}


def register_artifacts_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    # ==================== ARTIFACTS ====================
    @router.get("/artifacts")
    async def get_artifacts(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        user_artifacts = await db.user_artifacts.find({"user_id": uid}).to_list(200)
        owned_ids = {ua["artifact_id"]: ua for ua in user_artifacts}

        # Calculate total buffs from all owned artifacts
        total_buffs = {}
        active_sets = {}
        artifacts_list = []

        for art in ARTIFACTS:
            ua = owned_ids.get(art["id"])
            owned = ua is not None
            level = ua.get("level", 1) if ua else 0
            # Level multiplier: each level adds 20% to base buff
            level_mult = 1 + (level - 1) * 0.2 if owned else 0

            art_info = {
                **art,
                "owned": owned,
                "level": level,
                "duplicates": ua.get("duplicates", 0) if ua else 0,
                "effective_buff": {k: round(v * level_mult, 4) for k, v in art["buff"].items()} if owned else {},
            }
            artifacts_list.append(art_info)

            if owned:
                for stat, val in art["buff"].items():
                    total_buffs[stat] = total_buffs.get(stat, 0) + val * level_mult
                # Track sets
                s = art["set"]
                active_sets[s] = active_sets.get(s, 0) + 1

        # Calculate set bonuses
        set_bonuses = {}
        for set_id, count in active_sets.items():
            s = ARTIFACT_SETS.get(set_id)
            if s:
                for threshold, bonus in sorted(s["bonuses"].items()):
                    if count >= threshold:
                        set_bonuses[set_id] = {"name": s["name"], "count": count, "threshold": threshold, "bonus": bonus}
                        for stat, val in bonus.items():
                            total_buffs[stat] = total_buffs.get(stat, 0) + val

        return {
            "artifacts": artifacts_list,
            "total_buffs": {k: round(v, 4) for k, v in total_buffs.items()},
            "set_bonuses": set_bonuses,
            "sets": {k: {"name": v["name"], "bonuses": v["bonuses"]} for k, v in ARTIFACT_SETS.items()},
            "owned_count": len(owned_ids),
            "total_count": len(ARTIFACTS),
        }

    class ArtifactFuseRequest(BaseModel):
        artifact_id: str

    @router.post("/artifacts/fuse")
    async def fuse_artifact(req: ArtifactFuseRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        ua = await db.user_artifacts.find_one({"user_id": uid, "artifact_id": req.artifact_id})
        if not ua:
            raise HTTPException(404, "Artefatto non posseduto")
        if ua.get("duplicates", 0) < 1:
            raise HTTPException(400, "Servono duplicati per potenziare! Evoca altri artefatti.")
        max_level = 10
        if ua.get("level", 1) >= max_level:
            raise HTTPException(400, f"Livello massimo ({max_level}) raggiunto!")
        await db.user_artifacts.update_one(
            {"user_id": uid, "artifact_id": req.artifact_id},
            {"$inc": {"level": 1, "duplicates": -1}}
        )
        new_level = ua.get("level", 1) + 1
        art = next((a for a in ARTIFACTS if a["id"] == req.artifact_id), None)
        level_mult = 1 + (new_level - 1) * 0.2
        new_buff = {k: round(v * level_mult, 4) for k, v in art["buff"].items()} if art else {}
        return {"success": True, "new_level": new_level, "new_buff": new_buff, "duplicates_remaining": ua.get("duplicates", 0) - 1}

    @router.post("/artifacts/pull")
    async def pull_artifact(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        user = await db.users.find_one({"id": uid})
        cost = ARTIFACT_BANNER["cost_single"]
        if user.get("gems", 0) < cost:
            raise HTTPException(400, f"Servono {cost} gemme!")
        await db.users.update_one({"id": uid}, {"$inc": {"gems": -cost}})
        # Roll rarity
        roll = random.random()
        cumul = 0
        rarity = 1
        for r, rate in ARTIFACT_BANNER["rates"].items():
            cumul += rate
            if roll <= cumul:
                rarity = r
                break
        # Pick artifact of that rarity
        pool = [a for a in ARTIFACTS if a["rarity"] == rarity]
        if not pool:
            pool = [a for a in ARTIFACTS if a["rarity"] <= rarity]
        art = random.choice(pool)
        # Check if already owned
        existing = await db.user_artifacts.find_one({"user_id": uid, "artifact_id": art["id"]})
        is_duplicate = existing is not None
        if existing:
            await db.user_artifacts.update_one(
                {"user_id": uid, "artifact_id": art["id"]},
                {"$inc": {"duplicates": 1}}
            )
        else:
            await db.user_artifacts.insert_one({
                "user_id": uid, "artifact_id": art["id"],
                "level": 1, "duplicates": 0, "obtained_at": datetime.utcnow(),
            })
        updated_user = await db.users.find_one({"id": uid})
        return {
            "artifact": art, "is_duplicate": is_duplicate,
            "remaining_gems": updated_user.get("gems", 0),
        }

    @router.post("/artifacts/pull10")
    async def pull_artifact_10(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        user = await db.users.find_one({"id": uid})
        cost = ARTIFACT_BANNER["cost_multi"]
        if user.get("gems", 0) < cost:
            raise HTTPException(400, f"Servono {cost} gemme!")
        await db.users.update_one({"id": uid}, {"$inc": {"gems": -cost}})
        results = []
        for i in range(10):
            roll = random.random()
            cumul = 0
            rarity = 1
            rates = ARTIFACT_BANNER["rates"]
            if i == 9:  # Guaranteed 4+ on last
                rates = {4: 0.55, 5: 0.30, 6: 0.15}
            for r, rate in rates.items():
                cumul += rate
                if roll <= cumul:
                    rarity = r
                    break
            pool = [a for a in ARTIFACTS if a["rarity"] == rarity]
            if not pool:
                pool = [a for a in ARTIFACTS if a["rarity"] <= rarity]
            art = random.choice(pool)
            existing = await db.user_artifacts.find_one({"user_id": uid, "artifact_id": art["id"]})
            is_dup = existing is not None
            if existing:
                await db.user_artifacts.update_one({"user_id": uid, "artifact_id": art["id"]}, {"$inc": {"duplicates": 1}})
            else:
                await db.user_artifacts.insert_one({"user_id": uid, "artifact_id": art["id"], "level": 1, "duplicates": 0, "obtained_at": datetime.utcnow()})
            results.append({"artifact": art, "is_duplicate": is_dup})
        updated_user = await db.users.find_one({"id": uid})
        return {"results": results, "remaining_gems": updated_user.get("gems", 0)}

    # ==================== CONSTELLATIONS ====================
    @router.get("/constellations")
    async def get_constellations(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        user_consts = await db.user_constellations.find({"user_id": uid}).to_list(50)
        owned_ids = {uc["constellation_id"]: uc for uc in user_consts}
        # Get equipped constellation
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        equipped_id = team.get("constellation_id") if team else None
        constellations_list = []
        for c in CONSTELLATIONS:
            uc = owned_ids.get(c["id"])
            owned = uc is not None
            level = uc.get("level", 1) if uc else 0
            level_mult = 1 + (level - 1) * 0.15 if owned else 0
            constellations_list.append({
                **c,
                "owned": owned,
                "level": level,
                "duplicates": uc.get("duplicates", 0) if uc else 0,
                "equipped": c["id"] == equipped_id,
                "effective_buff": {k: round(v * level_mult, 4) for k, v in c["buff"].items()} if owned else {},
                "skill_mult": round(c["skill"]["damage_mult"] * level_mult, 2) if owned and c["skill"]["damage_mult"] > 0 else c["skill"]["damage_mult"],
            })
        # Currently equipped buff
        equipped_buff = {}
        equipped_skill = None
        if equipped_id:
            ec = next((c for c in CONSTELLATIONS if c["id"] == equipped_id), None)
            uc = owned_ids.get(equipped_id)
            if ec and uc:
                level_mult = 1 + (uc.get("level", 1) - 1) * 0.15
                equipped_buff = {k: round(v * level_mult, 4) for k, v in ec["buff"].items()}
                equipped_skill = {**ec["skill"], "damage_mult": round(ec["skill"]["damage_mult"] * level_mult, 2)}
        return {
            "constellations": constellations_list,
            "equipped_id": equipped_id,
            "equipped_buff": equipped_buff,
            "equipped_skill": equipped_skill,
        }

    class EquipConstellationRequest(BaseModel):
        constellation_id: str

    @router.post("/constellations/equip")
    async def equip_constellation(req: EquipConstellationRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        uc = await db.user_constellations.find_one({"user_id": uid, "constellation_id": req.constellation_id})
        if not uc:
            raise HTTPException(404, "Costellazione non posseduta!")
        await db.teams.update_one(
            {"user_id": uid, "is_active": True},
            {"$set": {"constellation_id": req.constellation_id}},
            upsert=True
        )
        c = next((x for x in CONSTELLATIONS if x["id"] == req.constellation_id), None)
        return {"success": True, "constellation": c.get("name", "?") if c else "?"}

    @router.post("/constellations/fuse")
    async def fuse_constellation(req: EquipConstellationRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        uc = await db.user_constellations.find_one({"user_id": uid, "constellation_id": req.constellation_id})
        if not uc:
            raise HTTPException(404, "Costellazione non posseduta")
        if uc.get("duplicates", 0) < 1:
            raise HTTPException(400, "Servono duplicati per potenziare!")
        if uc.get("level", 1) >= 5:
            raise HTTPException(400, "Livello massimo raggiunto!")
        await db.user_constellations.update_one(
            {"user_id": uid, "constellation_id": req.constellation_id},
            {"$inc": {"level": 1, "duplicates": -1}}
        )
        new_level = uc.get("level", 1) + 1
        c = next((x for x in CONSTELLATIONS if x["id"] == req.constellation_id), None)
        level_mult = 1 + (new_level - 1) * 0.15
        return {
            "success": True, "new_level": new_level,
            "new_buff": {k: round(v * level_mult, 4) for k, v in c["buff"].items()} if c else {},
        }

    @router.post("/constellations/pull")
    async def pull_constellation(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        user = await db.users.find_one({"id": uid})
        cost = CONSTELLATION_BANNER["cost_single"]
        if user.get("gems", 0) < cost:
            raise HTTPException(400, f"Servono {cost} gemme!")
        await db.users.update_one({"id": uid}, {"$inc": {"gems": -cost}})
        roll = random.random()
        cumul = 0
        rarity = 3
        for r, rate in CONSTELLATION_BANNER["rates"].items():
            cumul += rate
            if roll <= cumul:
                rarity = r
                break
        pool = [c for c in CONSTELLATIONS if c["rarity"] == rarity]
        if not pool:
            pool = [c for c in CONSTELLATIONS if c["rarity"] <= rarity]
        const = random.choice(pool)
        existing = await db.user_constellations.find_one({"user_id": uid, "constellation_id": const["id"]})
        is_dup = existing is not None
        if existing:
            await db.user_constellations.update_one({"user_id": uid, "constellation_id": const["id"]}, {"$inc": {"duplicates": 1}})
        else:
            await db.user_constellations.insert_one({"user_id": uid, "constellation_id": const["id"], "level": 1, "duplicates": 0, "obtained_at": datetime.utcnow()})
        updated_user = await db.users.find_one({"id": uid})
        return {"constellation": const, "is_duplicate": is_dup, "remaining_gems": updated_user.get("gems", 0)}

    @router.post("/constellations/pull10")
    async def pull_constellation_10(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        user = await db.users.find_one({"id": uid})
        cost = CONSTELLATION_BANNER["cost_multi"]
        if user.get("gems", 0) < cost:
            raise HTTPException(400, f"Servono {cost} gemme!")
        await db.users.update_one({"id": uid}, {"$inc": {"gems": -cost}})
        results = []
        for i in range(10):
            roll = random.random()
            cumul = 0
            rarity = 3
            rates = CONSTELLATION_BANNER["rates"]
            if i == 9:
                rates = {4: 0.40, 5: 0.40, 6: 0.20}
            for r, rate in rates.items():
                cumul += rate
                if roll <= cumul:
                    rarity = r
                    break
            pool = [c for c in CONSTELLATIONS if c["rarity"] == rarity]
            if not pool:
                pool = [c for c in CONSTELLATIONS if c["rarity"] <= rarity]
            const = random.choice(pool)
            existing = await db.user_constellations.find_one({"user_id": uid, "constellation_id": const["id"]})
            is_dup = existing is not None
            if existing:
                await db.user_constellations.update_one({"user_id": uid, "constellation_id": const["id"]}, {"$inc": {"duplicates": 1}})
            else:
                await db.user_constellations.insert_one({"user_id": uid, "constellation_id": const["id"], "level": 1, "duplicates": 0, "obtained_at": datetime.utcnow()})
            results.append({"constellation": const, "is_duplicate": is_dup})
        updated_user = await db.users.find_one({"id": uid})
        return {"results": results, "remaining_gems": updated_user.get("gems", 0)}

    # ==================== BANNERS INFO ====================
    @router.get("/banners/special")
    async def get_special_banners():
        return {
            "artifact_banner": {**ARTIFACT_BANNER, "total_artifacts": len(ARTIFACTS)},
            "constellation_banner": {**CONSTELLATION_BANNER, "total_constellations": len(CONSTELLATIONS)},
        }
