"""
Divine Waifus - Achievement System
20+ achievements with tiers, progress tracking, and claimable rewards.
"""
import uuid
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel

# Only using BMP-safe emoji (no surrogate pairs)
ACHIEVEMENTS = [
    {"id": "battle_wins", "name": "Guerriero", "icon": "\u2694\uFE0F", "category": "combat",
     "description": "Vinci battaglie nella storia",
     "tiers": [
         {"target": 10, "reward": {"gold": 5000}},
         {"target": 50, "reward": {"gold": 20000, "gems": 20}},
         {"target": 200, "reward": {"gold": 100000, "gems": 50}, "title": "Guerriero"},
         {"target": 1000, "reward": {"gold": 500000, "gems": 200}, "title": "Veterano"},
     ], "track_field": "battle_wins"},
    {"id": "pvp_wins", "name": "Gladiatore", "icon": "\u2694\uFE0F", "category": "combat",
     "description": "Vinci battaglie in Arena PvP",
     "tiers": [
         {"target": 5, "reward": {"gold": 3000}},
         {"target": 30, "reward": {"gold": 15000}},
         {"target": 100, "reward": {"gems": 100}, "title": "Gladiatore"},
         {"target": 500, "reward": {"gems": 500}, "title": "Campione Arena"},
     ], "track_field": "pvp_wins"},
    {"id": "tower_floors", "name": "Scalatore", "icon": "\u26F0\uFE0F", "category": "combat",
     "description": "Raggiungi piani nella Torre",
     "tiers": [
         {"target": 10, "reward": {"gold": 10000}},
         {"target": 30, "reward": {"gold": 50000, "gems": 30}},
         {"target": 50, "reward": {"gems": 100}, "title": "Scalatore"},
         {"target": 100, "reward": {"gems": 300}, "title": "Conquistatore Torre"},
     ], "track_field": "tower_floors"},
    {"id": "raid_kills", "name": "Ammazza Boss", "icon": "\u2620\uFE0F", "category": "combat",
     "description": "Sconfiggi boss nei Raid",
     "tiers": [
         {"target": 1, "reward": {"gold": 10000}},
         {"target": 5, "reward": {"gems": 50}},
         {"target": 20, "reward": {"gems": 200}, "title": "Ammazza Boss"},
     ], "track_field": "raid_kills"},
    {"id": "gvg_wins", "name": "Stratega", "icon": "\u265F\uFE0F", "category": "combat",
     "description": "Vinci guerre tra gilde",
     "tiers": [
         {"target": 1, "reward": {"gold": 20000}},
         {"target": 5, "reward": {"gems": 100}, "title": "Stratega"},
         {"target": 20, "reward": {"gems": 500}, "title": "Conquistatore"},
     ], "track_field": "gvg_wins"},
    {"id": "heroes_owned", "name": "Collezionista", "icon": "\u2605", "category": "collection",
     "description": "Possiedi eroi diversi",
     "tiers": [
         {"target": 5, "reward": {"gold": 5000}},
         {"target": 15, "reward": {"gold": 30000, "gems": 30}},
         {"target": 25, "reward": {"gems": 100}, "title": "Collezionista"},
         {"target": 30, "reward": {"gems": 300}, "title": "Maestro Collezionista"},
     ], "track_field": "heroes_owned"},
    {"id": "six_star_heroes", "name": "Cacciatore di Stelle", "icon": "\u2B50", "category": "collection",
     "description": "Possiedi eroi a 6+ stelle",
     "tiers": [
         {"target": 1, "reward": {"gems": 50}},
         {"target": 3, "reward": {"gems": 150}},
         {"target": 6, "reward": {"gems": 300}, "title": "Cacciatore di Stelle"},
         {"target": 10, "reward": {"gems": 1000}, "title": "Signore delle Stelle"},
     ], "track_field": "six_star_heroes"},
    {"id": "artifacts_owned", "name": "Archeologo", "icon": "\u2660\uFE0F", "category": "collection",
     "description": "Sblocca artefatti",
     "tiers": [
         {"target": 3, "reward": {"gold": 10000}},
         {"target": 8, "reward": {"gems": 50}},
         {"target": 15, "reward": {"gems": 200}, "title": "Archeologo"},
     ], "track_field": "artifacts_owned"},
    {"id": "constellations_owned", "name": "Astronomo", "icon": "\u264C", "category": "collection",
     "description": "Sblocca costellazioni",
     "tiers": [
         {"target": 2, "reward": {"gems": 30}},
         {"target": 6, "reward": {"gems": 100}},
         {"target": 12, "reward": {"gems": 500}, "title": "Astronomo"},
     ], "track_field": "constellations_owned"},
    {"id": "max_hero_level", "name": "Allenatore", "icon": "\u26A1", "category": "progression",
     "description": "Porta un eroe al livello massimo",
     "tiers": [
         {"target": 30, "reward": {"gold": 10000}},
         {"target": 70, "reward": {"gold": 50000, "gems": 30}},
         {"target": 130, "reward": {"gems": 200}, "title": "Allenatore Esperto"},
         {"target": 200, "reward": {"gems": 500}, "title": "Maestro Allenatore"},
     ], "track_field": "max_hero_level"},
    {"id": "reincarnations", "name": "Rinascita", "icon": "\u2728", "category": "progression",
     "description": "Reincarna eroi",
     "tiers": [
         {"target": 1, "reward": {"gems": 100}, "title": "Rinato"},
         {"target": 3, "reward": {"gems": 300}},
         {"target": 5, "reward": {"gems": 800}, "title": "Trascendente"},
     ], "track_field": "reincarnations"},
    {"id": "total_power", "name": "Potenza", "icon": "\u26A1", "category": "progression",
     "description": "Raggiungi potenza team totale",
     "tiers": [
         {"target": 10000, "reward": {"gold": 10000}},
         {"target": 50000, "reward": {"gold": 50000, "gems": 50}},
         {"target": 200000, "reward": {"gems": 200}, "title": "Potente"},
         {"target": 1000000, "reward": {"gems": 1000}, "title": "Onnipotente"},
     ], "track_field": "total_power"},
    {"id": "gacha_pulls", "name": "Evocatore", "icon": "\u2606", "category": "progression",
     "description": "Effettua evocazioni gacha",
     "tiers": [
         {"target": 10, "reward": {"gold": 5000}},
         {"target": 50, "reward": {"gems": 30}},
         {"target": 200, "reward": {"gems": 100}, "title": "Evocatore"},
         {"target": 1000, "reward": {"gems": 500}, "title": "Gran Evocatore"},
     ], "track_field": "gacha_pulls"},
    {"id": "friends_count", "name": "Socievole", "icon": "\u263A\uFE0F", "category": "social",
     "description": "Aggiungi amici",
     "tiers": [
         {"target": 3, "reward": {"gold": 5000}},
         {"target": 10, "reward": {"gold": 20000, "gems": 20}},
         {"target": 20, "reward": {"gems": 100}, "title": "Socievole"},
     ], "track_field": "friends_count"},
    {"id": "guild_joined", "name": "Compagno", "icon": "\u2605", "category": "social",
     "description": "Unisciti a una gilda",
     "tiers": [
         {"target": 1, "reward": {"gold": 10000}, "title": "Compagno"},
     ], "track_field": "guild_joined"},
    {"id": "chat_messages", "name": "Chiacchierone", "icon": "\u2709\uFE0F", "category": "social",
     "description": "Invia messaggi nella piazza",
     "tiers": [
         {"target": 10, "reward": {"gold": 3000}},
         {"target": 50, "reward": {"gold": 15000}},
         {"target": 200, "reward": {"gems": 50}, "title": "Chiacchierone"},
     ], "track_field": "chat_messages"},
    {"id": "gold_earned", "name": "Ricco", "icon": "\u2605", "category": "economy",
     "description": "Accumula oro totale",
     "tiers": [
         {"target": 50000, "reward": {"gems": 10}},
         {"target": 500000, "reward": {"gems": 50}},
         {"target": 5000000, "reward": {"gems": 200}, "title": "Ricco"},
         {"target": 50000000, "reward": {"gems": 1000}, "title": "Miliardario"},
     ], "track_field": "gold_earned"},
    {"id": "heroes_retired", "name": "Boia delle Anime", "icon": "\u2620\uFE0F", "category": "economy",
     "description": "Ritira eroi nella Fucina delle Anime",
     "tiers": [
         {"target": 5, "reward": {"gold": 10000}},
         {"target": 20, "reward": {"gems": 50}},
         {"target": 50, "reward": {"gems": 200}, "title": "Boia delle Anime"},
     ], "track_field": "heroes_retired"},
    {"id": "equipment_forged", "name": "Fabbro", "icon": "\u2692\uFE0F", "category": "economy",
     "description": "Potenzia equipaggiamento nella Fucina",
     "tiers": [
         {"target": 5, "reward": {"gold": 10000}},
         {"target": 20, "reward": {"gold": 50000, "gems": 30}},
         {"target": 50, "reward": {"gems": 100}, "title": "Maestro Fabbro"},
     ], "track_field": "equipment_forged"},
    {"id": "territories_conquered", "name": "Conquistatore", "icon": "\u2690", "category": "economy",
     "description": "Conquista territori",
     "tiers": [
         {"target": 1, "reward": {"gold": 10000}},
         {"target": 5, "reward": {"gems": 50}},
         {"target": 15, "reward": {"gems": 200}, "title": "Conquistatore di Terre"},
     ], "track_field": "territories_conquered"},
]

CATEGORIES = {
    "combat": {"name": "Combattimento", "icon": "\u2694\uFE0F", "color": "#ff4444"},
    "collection": {"name": "Collezione", "icon": "\u2605", "color": "#ffd700"},
    "progression": {"name": "Progressione", "icon": "\u26A1", "color": "#44cc44"},
    "social": {"name": "Sociale", "icon": "\u263A\uFE0F", "color": "#4488ff"},
    "economy": {"name": "Economia", "icon": "\u2605", "color": "#ff8844"},
}


def register_achievement_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    async def _get_progress(uid: str) -> dict:
        progress = {}
        user = await db.users.find_one({"id": uid})
        progress["battle_wins"] = user.get("battle_wins", 0) if user else 0
        progress["gold_earned"] = user.get("gold_earned", user.get("gold", 0)) if user else 0
        progress["gacha_pulls"] = user.get("gacha_pulls", 0) if user else 0
        pvp = await db.pvp_data.find_one({"user_id": uid})
        progress["pvp_wins"] = pvp.get("wins", 0) if pvp else 0
        tower = await db.tower_progress.find_one({"user_id": uid})
        progress["tower_floors"] = tower.get("highest_floor", 0) if tower else 0
        progress["raid_kills"] = await db.active_raids.count_documents({"participants": uid, "status": "completed"})
        progress["gvg_wins"] = await db.gvg_wars.count_documents({"winner_guild_id": user.get("guild_id", "none")}) if user and user.get("guild_id") else 0
        unique_list = await db.user_heroes.find({"user_id": uid}, {"hero_id": 1}).to_list(500)
        progress["heroes_owned"] = len(set(h["hero_id"] for h in unique_list))
        progress["six_star_heroes"] = await db.user_heroes.count_documents({"user_id": uid, "stars": {"$gte": 6}})
        top_hero = await db.user_heroes.find({"user_id": uid}).sort("level", -1).limit(1).to_list(1)
        progress["max_hero_level"] = top_hero[0].get("level", 0) if top_hero else 0
        progress["reincarnations"] = await db.user_heroes.count_documents({"user_id": uid, "is_reincarnated": True})
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        progress["total_power"] = team.get("total_power", 0) if team else 0
        progress["artifacts_owned"] = await db.user_artifacts.count_documents({"user_id": uid})
        progress["constellations_owned"] = await db.user_constellations.count_documents({"user_id": uid})
        friends = await db.friends.find_one({"user_id": uid})
        progress["friends_count"] = len(friends.get("friends", [])) if friends else 0
        progress["guild_joined"] = 1 if user and user.get("guild_id") else 0
        progress["chat_messages"] = await db.plaza_chat.count_documents({"user_id": uid})
        progress["heroes_retired"] = await db.retirement_history.count_documents({"user_id": uid})
        progress["equipment_forged"] = user.get("equipment_forged", 0) if user else 0
        progress["territories_conquered"] = await db.territory_control.count_documents({"captured_by": uid})
        return progress

    @router.get("/achievements")
    async def get_achievements(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        progress = await _get_progress(uid)
        claimed = await db.achievement_claims.find({"user_id": uid}).to_list(500)
        claimed_set = {f"{c['achievement_id']}_{c['tier_index']}" for c in claimed}
        result = []
        total_completed = 0
        total_tiers = 0
        for ach in ACHIEVEMENTS:
            current_val = progress.get(ach["track_field"], 0)
            tiers_info = []
            for i, tier in enumerate(ach["tiers"]):
                total_tiers += 1
                completed = current_val >= tier["target"]
                is_claimed = f"{ach['id']}_{i}" in claimed_set
                if completed: total_completed += 1
                tiers_info.append({"target": tier["target"], "reward": tier["reward"], "title": tier.get("title"), "completed": completed, "claimed": is_claimed, "can_claim": completed and not is_claimed})
            current_tier = 0
            for i, t in enumerate(tiers_info):
                if not t["completed"]: current_tier = i; break
                current_tier = i
            ct = ach["tiers"][min(current_tier, len(ach["tiers"])-1)]
            pct = min(1.0, current_val / max(1, ct["target"]))
            result.append({"id": ach["id"], "name": ach["name"], "icon": ach["icon"], "category": ach["category"], "description": ach["description"], "current_value": current_val, "current_tier": current_tier, "progress_pct": round(pct, 3), "tiers": tiers_info})
        return {"achievements": result, "categories": CATEGORIES, "stats": {"total_achievements": len(ACHIEVEMENTS), "total_tiers": total_tiers, "completed_tiers": total_completed, "completion_pct": round(total_completed / max(1, total_tiers), 3)}}

    class ClaimAchievementRequest(BaseModel):
        achievement_id: str
        tier_index: int

    @router.post("/achievements/claim")
    async def claim_achievement(req: ClaimAchievementRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        ach = next((a for a in ACHIEVEMENTS if a["id"] == req.achievement_id), None)
        if not ach: raise HTTPException(404, "Achievement non trovato")
        if req.tier_index < 0 or req.tier_index >= len(ach["tiers"]): raise HTTPException(400, "Tier non valido")
        existing = await db.achievement_claims.find_one({"user_id": uid, "achievement_id": req.achievement_id, "tier_index": req.tier_index})
        if existing: raise HTTPException(400, "Gia riscosso!")
        progress = await _get_progress(uid)
        current_val = progress.get(ach["track_field"], 0)
        tier = ach["tiers"][req.tier_index]
        if current_val < tier["target"]: raise HTTPException(400, f"Non hai raggiunto l'obiettivo ({current_val}/{tier['target']})!")
        reward = tier["reward"]
        user_inc = {}
        for rk, rv in reward.items():
            if rk in ("gold", "gems", "stamina"): user_inc[rk] = rv
        if user_inc: await db.users.update_one({"id": uid}, {"$inc": user_inc})
        if tier.get("title"): await db.users.update_one({"id": uid}, {"$addToSet": {"titles": tier["title"]}})
        await db.achievement_claims.insert_one({"user_id": uid, "achievement_id": req.achievement_id, "tier_index": req.tier_index, "claimed_at": datetime.utcnow()})
        return {"success": True, "achievement": ach["name"], "tier": req.tier_index + 1, "reward": reward, "title_earned": tier.get("title")}
