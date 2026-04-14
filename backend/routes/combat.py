"""
Divine Waifus - Combat Routes (Story, Tower, PvP, Events, Hero LevelUp, Titles)
"""
import random
import uuid
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from .game_data import STORY_CHAPTERS, EQUIPMENT_SLOTS, EQUIPMENT_TEMPLATES, DAILY_EVENTS


def register_combat_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    # ==================== STORY MODE ====================
    @router.get("/story/chapters")
    async def get_story_chapters(current_user: dict = Depends(get_current_user)):
        progress = await db.story_progress.find_one({"user_id": current_user["id"]})
        if not progress:
            progress = {"user_id": current_user["id"], "completed": {}, "current_chapter": 1, "current_stage": 1}
            await db.story_progress.insert_one(progress)
        chapters = []
        for ch in STORY_CHAPTERS:
            completed_stages = progress.get("completed", {}).get(str(ch["id"]), 0)
            chapters.append({
                **ch,
                "completed_stages": completed_stages,
                "unlocked": ch["id"] <= progress.get("current_chapter", 1),
                "fully_completed": completed_stages >= ch["stages"],
            })
        return {"chapters": chapters, "progress": {"current_chapter": progress.get("current_chapter", 1), "current_stage": progress.get("current_stage", 1)}}

    class StoryBattleRequest(BaseModel):
        chapter_id: int
        stage: int = 1

    @router.post("/story/battle")
    async def story_battle(req: StoryBattleRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        chapter = next((c for c in STORY_CHAPTERS if c["id"] == req.chapter_id), None)
        if not chapter:
            raise HTTPException(404, "Capitolo non trovato")
        progress = await db.story_progress.find_one({"user_id": uid})
        if not progress:
            progress = {"user_id": uid, "completed": {}, "current_chapter": 1, "current_stage": 1}
        if req.chapter_id > progress.get("current_chapter", 1):
            raise HTTPException(400, "Capitolo non ancora sbloccato!")
        user = await db.users.find_one({"id": uid})
        if user.get("stamina", 0) < 6:
            raise HTTPException(400, "Stamina insufficiente!")
        await db.users.update_one({"id": uid}, {"$inc": {"stamina": -6}})
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        team_power = team.get("total_power", 5000) if team else 5000
        stage_mult = 1 + (req.stage - 1) * 0.15
        enemy_power = int(chapter["enemy_power"] * stage_mult)
        victory = team_power * random.uniform(0.7, 1.3) > enemy_power * random.uniform(0.6, 1.0)
        rewards = {}
        if victory:
            mult = chapter["difficulty"] * stage_mult
            rewards = {
                "gold": int(chapter["rewards"]["gold"] * mult),
                "exp": int(chapter["rewards"]["exp"] * mult),
                "gems": chapter["rewards"]["gems"] if req.stage == chapter["stages"] else 0,
            }
            await db.users.update_one({"id": uid}, {"$inc": {"gold": rewards["gold"], "experience": rewards["exp"], "gems": rewards.get("gems", 0)}})
            completed_key = str(req.chapter_id)
            current_completed = progress.get("completed", {}).get(completed_key, 0)
            if req.stage > current_completed:
                await db.story_progress.update_one(
                    {"user_id": uid},
                    {"$set": {
                        f"completed.{completed_key}": req.stage,
                        "current_chapter": req.chapter_id + 1 if req.stage >= chapter["stages"] else req.chapter_id,
                        "current_stage": 1 if req.stage >= chapter["stages"] else req.stage + 1,
                    }},
                    upsert=True
                )
            if random.random() < 0.3 * chapter["difficulty"]:
                slot = random.choice(EQUIPMENT_SLOTS)
                templates = [t for t in EQUIPMENT_TEMPLATES[slot] if t["rarity"] <= chapter["difficulty"] + 1]
                if templates:
                    tmpl = random.choice(templates)
                    equip = {
                        "id": str(uuid.uuid4()), "user_id": uid, "name": tmpl["name"],
                        "slot": slot, "rarity": tmpl["rarity"], "stats": tmpl["stats"],
                        "level": 1, "obtained_at": datetime.utcnow(),
                    }
                    await db.user_equipment.insert_one(equip)
                    rewards["equipment"] = {"name": tmpl["name"], "rarity": tmpl["rarity"], "slot": slot}
        return {"victory": victory, "rewards": rewards, "chapter": chapter["name"], "stage": req.stage, "enemy_power": enemy_power, "team_power": team_power}

    # ==================== TOWER ====================
    @router.get("/tower/status")
    async def get_tower_status(current_user: dict = Depends(get_current_user)):
        tower = await db.tower_progress.find_one({"user_id": current_user["id"]})
        if not tower:
            tower = {"user_id": current_user["id"], "floor": 1, "highest_floor": 1, "rewards_claimed": []}
            await db.tower_progress.insert_one(tower)
        return serialize_doc(tower)

    @router.post("/tower/battle")
    async def tower_battle(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        tower = await db.tower_progress.find_one({"user_id": uid})
        if not tower:
            tower = {"user_id": uid, "floor": 1, "highest_floor": 1, "rewards_claimed": []}
            await db.tower_progress.insert_one(tower)
        floor = tower.get("floor", 1)
        user = await db.users.find_one({"id": uid})
        if user.get("stamina", 0) < 8:
            raise HTTPException(400, "Stamina insufficiente!")
        await db.users.update_one({"id": uid}, {"$inc": {"stamina": -8}})
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        team_power = team.get("total_power", 5000) if team else 5000
        enemy_power = int(2000 + floor * 800 + (floor ** 1.5) * 200)
        victory = team_power * random.uniform(0.7, 1.3) > enemy_power * random.uniform(0.6, 1.0)
        rewards = {}
        if victory:
            rewards = {
                "gold": int(floor * 300 + floor ** 1.3 * 100),
                "exp": int(floor * 150 + floor ** 1.2 * 50),
                "gems": 5 if floor % 5 == 0 else 0,
            }
            if floor % 10 == 0:
                rewards["gems"] += 20
            await db.users.update_one({"id": uid}, {"$inc": {"gold": rewards["gold"], "experience": rewards["exp"], "gems": rewards.get("gems", 0)}})
            new_floor = floor + 1
            highest = max(tower.get("highest_floor", 1), new_floor)
            await db.tower_progress.update_one({"user_id": uid}, {"$set": {"floor": new_floor, "highest_floor": highest}})
            if floor % 5 == 0:
                slot = random.choice(EQUIPMENT_SLOTS)
                max_rarity = min(6, 1 + floor // 10)
                templates = [t for t in EQUIPMENT_TEMPLATES[slot] if t["rarity"] <= max_rarity]
                if templates:
                    tmpl = random.choice(templates)
                    equip = {
                        "id": str(uuid.uuid4()), "user_id": uid, "name": tmpl["name"],
                        "slot": slot, "rarity": tmpl["rarity"], "stats": tmpl["stats"],
                        "level": 1, "obtained_at": datetime.utcnow(),
                    }
                    await db.user_equipment.insert_one(equip)
                    rewards["equipment"] = {"name": tmpl["name"], "rarity": tmpl["rarity"]}
        return {"victory": victory, "floor": floor, "rewards": rewards, "enemy_power": enemy_power, "team_power": team_power, "next_floor": floor + 1 if victory else floor}

    # ==================== PVP ARENA ====================
    @router.get("/pvp/status")
    async def get_pvp_status(current_user: dict = Depends(get_current_user)):
        pvp = await db.pvp_data.find_one({"user_id": current_user["id"]})
        if not pvp:
            pvp = {"user_id": current_user["id"], "rank": 0, "trophies": 0, "wins": 0, "losses": 0, "streak": 0, "daily_battles": 0, "last_battle_date": None}
            await db.pvp_data.insert_one(pvp)
        top10 = await db.pvp_data.find({}).sort("trophies", -1).limit(10).to_list(10)
        leaderboard = []
        for i, entry in enumerate(top10):
            user = await db.users.find_one({"id": entry["user_id"]})
            if user:
                leaderboard.append({"rank": i + 1, "username": user.get("username", "???"), "trophies": entry.get("trophies", 0), "wins": entry.get("wins", 0)})
        return {**serialize_doc(pvp), "leaderboard": leaderboard}

    @router.post("/pvp/battle")
    async def pvp_battle(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        pvp = await db.pvp_data.find_one({"user_id": uid})
        if not pvp:
            pvp = {"user_id": uid, "rank": 0, "trophies": 0, "wins": 0, "losses": 0, "streak": 0, "daily_battles": 0}
            await db.pvp_data.insert_one(pvp)
        if pvp.get("daily_battles", 0) >= 10:
            raise HTTPException(400, "Hai raggiunto il limite di 10 battaglie PvP giornaliere!")
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        team_power = team.get("total_power", 5000) if team else 5000
        opp_power = int(team_power * random.uniform(0.7, 1.3))
        opp_name = random.choice(["ShadowNinja", "DivineFighter", "StarGazer", "MoonKnight", "FireLord", "IceQueen", "ThunderGod", "NightBlade"])
        victory = team_power * random.uniform(0.75, 1.25) > opp_power * random.uniform(0.75, 1.25)
        trophy_change = 0
        rewards = {}
        if victory:
            trophy_change = random.randint(15, 30)
            rewards = {"gold": int(1000 + pvp.get("trophies", 0) * 2), "exp": 500}
            await db.users.update_one({"id": uid}, {"$inc": {"gold": rewards["gold"], "experience": rewards["exp"]}})
            await db.pvp_data.update_one({"user_id": uid}, {"$inc": {"trophies": trophy_change, "wins": 1, "streak": 1, "daily_battles": 1}})
        else:
            trophy_change = -random.randint(8, 15)
            await db.pvp_data.update_one({"user_id": uid}, {"$inc": {"trophies": trophy_change, "losses": 1, "daily_battles": 1}, "$set": {"streak": 0}})
        return {
            "victory": victory, "opponent": opp_name, "opponent_power": opp_power,
            "trophy_change": trophy_change, "rewards": rewards,
            "new_trophies": max(0, pvp.get("trophies", 0) + trophy_change),
        }

    # ==================== EVENTS ====================
    @router.get("/events/daily")
    async def get_daily_events(current_user: dict = Depends(get_current_user)):
        today = datetime.utcnow().weekday()
        available = [e for e in DAILY_EVENTS if today in e["available_days"]]
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        completions = await db.event_completions.find({"user_id": current_user["id"], "date": today_str}).to_list(100)
        completed_ids = [c["event_id"] for c in completions]
        for e in available:
            e["completed_today"] = e["id"] in completed_ids
        return {"events": available, "date": today_str}

    class EventBattleRequest(BaseModel):
        event_id: str

    @router.post("/events/battle")
    async def event_battle(req: EventBattleRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        event = next((e for e in DAILY_EVENTS if e["id"] == req.event_id), None)
        if not event:
            raise HTTPException(404, "Evento non trovato")
        user = await db.users.find_one({"id": uid})
        if user.get("stamina", 0) < event["stamina_cost"]:
            raise HTTPException(400, "Stamina insufficiente!")
        await db.users.update_one({"id": uid}, {"$inc": {"stamina": -event["stamina_cost"]}})
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        team_power = team.get("total_power", 5000) if team else 5000
        victory = random.random() < 0.8
        rewards = {}
        if victory:
            if event["reward_type"] == "gold":
                rewards["gold"] = int(2000 * event["reward_mult"])
                await db.users.update_one({"id": uid}, {"$inc": {"gold": rewards["gold"]}})
            elif event["reward_type"] == "exp":
                rewards["exp"] = int(1000 * event["reward_mult"])
                await db.users.update_one({"id": uid}, {"$inc": {"experience": rewards["exp"]}})
            elif event["reward_type"] == "gems":
                rewards["gems"] = random.randint(5, 15)
                await db.users.update_one({"id": uid}, {"$inc": {"gems": rewards["gems"]}})
            elif event["reward_type"] == "equipment":
                slot = random.choice(EQUIPMENT_SLOTS)
                tmpl = random.choice(EQUIPMENT_TEMPLATES[slot][:4])
                equip = {"id": str(uuid.uuid4()), "user_id": uid, "name": tmpl["name"], "slot": slot, "rarity": tmpl["rarity"], "stats": tmpl["stats"], "level": 1, "obtained_at": datetime.utcnow()}
                await db.user_equipment.insert_one(equip)
                rewards["equipment"] = {"name": tmpl["name"], "rarity": tmpl["rarity"]}
            elif event["reward_type"] == "mixed":
                rewards = {"gold": 5000, "exp": 2000, "gems": 10}
                await db.users.update_one({"id": uid}, {"$inc": {"gold": 5000, "experience": 2000, "gems": 10}})
            today_str = datetime.utcnow().strftime("%Y-%m-%d")
            await db.event_completions.insert_one({"user_id": uid, "event_id": req.event_id, "date": today_str})
        return {"victory": victory, "rewards": rewards, "event": event["name"]}

    # ==================== HERO LEVEL UP ====================
    class LevelUpRequest(BaseModel):
        user_hero_id: str

    @router.post("/hero/levelup")
    async def level_up_hero(req: LevelUpRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        uh = await db.user_heroes.find_one({"id": req.user_hero_id, "user_id": uid})
        if not uh:
            raise HTTPException(404, "Eroe non trovato")
        user = await db.users.find_one({"id": uid})
        level = uh.get("level", 1)
        cost = level * 200
        if user.get("gold", 0) < cost:
            raise HTTPException(400, f"Servono {cost} oro!")
        if level >= 100:
            raise HTTPException(400, "Livello massimo raggiunto!")
        await db.users.update_one({"id": uid}, {"$inc": {"gold": -cost}})
        await db.user_heroes.update_one({"id": req.user_hero_id}, {"$inc": {"level": 1}})
        return {"success": True, "new_level": level + 1, "gold_spent": cost}

    # ==================== TITLES ====================
    @router.get("/titles")
    async def get_titles(current_user: dict = Depends(get_current_user)):
        all_titles = [
            {"id": "novizio", "name": "Novizio", "condition": "Inizia il gioco"},
            {"id": "guerriero", "name": "Guerriero", "condition": "Vinci 10 battaglie"},
            {"id": "collezionista", "name": "Collezionista", "condition": "Possiedi 10 eroi"},
            {"id": "leggenda", "name": "Leggenda", "condition": "Raggiungi piano 50 in Torre"},
            {"id": "campione", "name": "Campione", "condition": "Raggiungi 1000 trofei PvP"},
            {"id": "divino", "name": "Divino", "condition": "Possiedi un eroe 6 stelle"},
        ]
        return {"titles": all_titles, "user_titles": current_user.get("titles", ["Novizio"]), "active": current_user.get("active_title", "Novizio")}

    class SetTitleRequest(BaseModel):
        title: str

    @router.post("/title/set")
    async def set_title(req: SetTitleRequest, current_user: dict = Depends(get_current_user)):
        if req.title not in current_user.get("titles", []):
            raise HTTPException(400, "Non possiedi questo titolo!")
        await db.users.update_one({"id": current_user["id"]}, {"$set": {"active_title": req.title}})
        return {"success": True}
