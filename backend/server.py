"""
Divine Waifus - Main Backend Server
FastAPI + MongoDB + JWT Auth
"""
import os
import uuid
import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, Header, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient

from battle_engine import create_battle_routes, ELEMENT_SKILLS, PASSIVE_SKILLS, POSITION_BUFFS
from game_systems import create_game_routes
from routes.sprites import register_sprite_routes
from routes.items import register_items_routes, BATTLE_DROPS

# ===================== CONFIG =====================
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "divine_waifus")
JWT_SECRET = os.getenv("JWT_SECRET", "divine_waifus_secret_key_2025")

app = FastAPI(title="Divine Waifus API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== DATABASE =====================
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

# ===================== AUTH =====================
def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=30),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token mancante")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = await db.users.find_one({"id": payload["user_id"]})
        if not user:
            raise HTTPException(status_code=401, detail="Utente non trovato")
        return serialize_doc(user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token scaduto")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token non valido")

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str = ""

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/register")
async def register(req: RegisterRequest):
    existing = await db.users.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email gia registrata")
    
    hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    user_id = str(uuid.uuid4())
    username = req.username or req.email.split("@")[0]
    
    user = {
        "id": user_id,
        "email": req.email,
        "password": hashed,
        "username": username,
        "level": 1,
        "experience": 0,
        "gold": 5000,
        "gems": 100,
        "stamina": 100,
        "max_stamina": 100,
        "titles": ["Novizio"],
        "active_title": "Novizio",
        "aura": "none",
        "faction": None,
        "guild_id": None,
        "created_at": datetime.utcnow(),
    }
    await db.users.insert_one(user)
    
    # Give starter heroes (3 random 1-2 star heroes)
    all_heroes = await db.heroes.find({"rarity": {"$lte": 2}}).to_list(100)
    if all_heroes:
        starters = random.sample(all_heroes, min(3, len(all_heroes)))
        for hero in starters:
            user_hero = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "hero_id": hero["id"],
                "level": 1,
                "experience": 0,
                "stars": hero["rarity"],
                "obtained_at": datetime.utcnow(),
            }
            await db.user_heroes.insert_one(user_hero)
    
    token = create_token(user_id)
    return {"token": token, "user": {k: v for k, v in user.items() if k != "password" and k != "_id"}}

@app.post("/api/login")
async def login(req: LoginRequest):
    user = await db.users.find_one({"email": req.email})
    if not user:
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    if not bcrypt.checkpw(req.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    
    token = create_token(user["id"])
    return {"token": token, "user": {k: v for k, v in user.items() if k != "password" and k != "_id"}}

@app.get("/api/user/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    safe_user = {k: v for k, v in current_user.items() if k != "password"}
    return safe_user

# ===================== HEROES =====================
@app.get("/api/heroes")
async def get_all_heroes():
    heroes = await db.heroes.find({}, {"image_base64": 0}).to_list(100)
    for h in heroes:
        if not h.get("image_url"):
            h["image_url"] = None
    return [serialize_doc(h) for h in heroes]

@app.get("/api/heroes/{hero_id}")
async def get_hero(hero_id: str):
    hero = await db.heroes.find_one({"id": hero_id})
    if not hero:
        raise HTTPException(status_code=404, detail="Eroe non trovato")
    return serialize_doc(hero)

@app.get("/api/user/heroes")
async def get_user_heroes(current_user: dict = Depends(get_current_user)):
    user_heroes = await db.user_heroes.find({"user_id": current_user["id"]}).to_list(1000)
    result = []
    for uh in user_heroes:
        hero = await db.heroes.find_one({"id": uh["hero_id"]})
        if hero:
            merged = {
                **serialize_doc(uh),
                "hero_name": hero.get("name"),
                "hero_element": hero.get("element"),
                "hero_rarity": hero.get("rarity"),
                "hero_image": hero.get("image_url") or hero.get("image_base64") or hero.get("image"),
                "hero_stats": hero.get("base_stats"),
                "hero_class": hero.get("hero_class"),
            }
            result.append(merged)
    return result

# ===================== GACHA =====================
GACHA_BANNERS = {
    "standard": {
        "name": "Banner Standard",
        "cost_single": 100,
        "cost_multi": 900,
        "rates": {1: 0.30, 2: 0.30, 3: 0.20, 4: 0.12, 5: 0.06, 6: 0.02},
        "guarantee_10": 4,
        "filter": None,
    },
    "elemental": {
        "name": "Banner Elementale",
        "cost_single": 120,
        "cost_multi": 1000,
        "rates": {1: 0.15, 2: 0.25, 3: 0.28, 4: 0.18, 5: 0.10, 6: 0.04},
        "guarantee_10": 4,
        "filter": None,  # will pick random element focus
    },
    "premium": {
        "name": "Banner Premium",
        "cost_single": 200,
        "cost_multi": 1800,
        "rates": {1: 0.05, 2: 0.15, 3: 0.25, 4: 0.25, 5: 0.20, 6: 0.10},
        "guarantee_10": 5,
        "filter": None,
    },
}

class GachaPullRequest(BaseModel):
    banner: str = "standard"

async def _do_gacha_pull(user_id: str, banner_id: str):
    banner = GACHA_BANNERS.get(banner_id, GACHA_BANNERS["standard"])
    rates = banner["rates"]
    roll = random.random()
    cumulative = 0
    rarity = 1
    for r, rate in rates.items():
        cumulative += rate
        if roll <= cumulative:
            rarity = r
            break
    query: dict = {"rarity": rarity}
    if banner_id == "elemental":
        focus = random.choice(["fire", "water", "earth", "wind", "light", "dark"])
        if random.random() < 0.6:
            query["element"] = focus
    heroes = await db.heroes.find(query).to_list(100)
    if not heroes:
        heroes = await db.heroes.find({"rarity": rarity}).to_list(100)
    if not heroes:
        heroes = await db.heroes.find({}).to_list(100)
    hero = random.choice(heroes)
    user_hero = {
        "id": str(uuid.uuid4()), "user_id": user_id, "hero_id": hero["id"],
        "level": 1, "experience": 0, "stars": hero["rarity"], "obtained_at": datetime.utcnow(),
    }
    await db.user_heroes.insert_one(user_hero)
    return hero, user_hero

@app.post("/api/gacha/pull")
async def gacha_pull(req: GachaPullRequest = GachaPullRequest(), current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    banner = GACHA_BANNERS.get(req.banner, GACHA_BANNERS["standard"])
    user = await db.users.find_one({"id": user_id})
    cost = banner["cost_single"]
    if user.get("gems", 0) < cost:
        raise HTTPException(status_code=400, detail=f"Gemme insufficienti! Servono {cost}")
    await db.users.update_one({"id": user_id}, {"$inc": {"gems": -cost}})
    hero, user_hero = await _do_gacha_pull(user_id, req.banner)
    updated_user = await db.users.find_one({"id": user_id})
    return {
        "hero": serialize_doc(hero), "user_hero_id": user_hero["id"],
        "is_new": True, "rarity": hero["rarity"],
        "remaining_gems": updated_user.get("gems", 0), "banner": req.banner,
    }

@app.post("/api/gacha/pull10")
async def gacha_pull_10(req: GachaPullRequest = GachaPullRequest(), current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    banner = GACHA_BANNERS.get(req.banner, GACHA_BANNERS["standard"])
    user = await db.users.find_one({"id": user_id})
    cost = banner["cost_multi"]
    if user.get("gems", 0) < cost:
        raise HTTPException(status_code=400, detail=f"Gemme insufficienti! Servono {cost}")
    await db.users.update_one({"id": user_id}, {"$inc": {"gems": -cost}})
    results = []
    for i in range(10):
        if i == 9:
            # Guaranteed minimum rarity on last pull
            g = banner["guarantee_10"]
            rarity = random.choices(list(range(g, 7)), weights=[0.65, 0.25, 0.10] if g == 4 else [0.70, 0.30])[0]
            query: dict = {"rarity": rarity}
            heroes = await db.heroes.find(query).to_list(100)
            if not heroes:
                heroes = await db.heroes.find({}).to_list(100)
            hero = random.choice(heroes)
            uh = {"id": str(uuid.uuid4()), "user_id": user_id, "hero_id": hero["id"], "level": 1, "experience": 0, "stars": hero["rarity"], "obtained_at": datetime.utcnow()}
            await db.user_heroes.insert_one(uh)
            results.append({"hero": serialize_doc(hero), "user_hero_id": uh["id"], "rarity": hero["rarity"]})
        else:
            hero, uh = await _do_gacha_pull(user_id, req.banner)
            results.append({"hero": serialize_doc(hero), "user_hero_id": uh["id"], "rarity": hero["rarity"]})
    updated_user = await db.users.find_one({"id": user_id})
    return {"results": results, "remaining_gems": updated_user.get("gems", 0), "banner": req.banner}

@app.get("/api/gacha/banners")
async def get_gacha_banners():
    return {k: {"name": v["name"], "cost_single": v["cost_single"], "cost_multi": v["cost_multi"],
                "rates": v["rates"], "guarantee_10": v["guarantee_10"]} for k, v in GACHA_BANNERS.items()}

# ===================== TEAM =====================
@app.get("/api/team")
async def get_team(current_user: dict = Depends(get_current_user)):
    team = await db.teams.find_one({"user_id": current_user["id"], "is_active": True})
    if team:
        return serialize_doc(team)
    return {"formation": [], "total_power": 0}

# ===================== UTILITY =====================
def calculate_hero_power(hero: dict, user_hero: dict = None) -> int:
    stats = hero.get("base_stats", {})
    level = user_hero.get("level", 1) if user_hero else 1
    rarity = hero.get("rarity", 1)
    power = (
        stats.get("physical_damage", stats.get("attack", 100)) +
        stats.get("magic_damage", 0) +
        stats.get("physical_defense", stats.get("defense", 50)) +
        stats.get("magic_defense", 0) +
        stats.get("hp", 1000) // 10 +
        stats.get("speed", 10) +
        stats.get("healing", 0) // 2
    )
    power = int(power * (1 + (level - 1) * 0.05) * (1 + rarity * 0.2))
    return power

# ===================== BATTLE ROUTES =====================
battle_router = create_battle_routes(db, get_current_user, serialize_doc, calculate_hero_power)
app.include_router(battle_router)

# ===================== GAME SYSTEMS ROUTES =====================
game_router = create_game_routes(db, get_current_user, serialize_doc, calculate_hero_power)
app.include_router(game_router)

# ===================== SPRITE ROUTES =====================
sprite_router = APIRouter(prefix="/api")
register_sprite_routes(sprite_router, db)
app.include_router(sprite_router)

# ===================== ITEMS & SKILL ROUTES =====================
items_router = APIRouter(prefix="/api")
register_items_routes(items_router, db, get_current_user)
app.include_router(items_router)

# ===================== SEED =====================
# Mappa nome eroe → faction canonica (valori che il resolver background
# accetta direttamente: greek/norse/egyptian/japanese/celtic).
# NON scrivere mai alias asset (nordic/egypt) nel DB — quelli restano
# SOLO nel registry di /app/frontend/components/ui/battleBackgrounds.ts.
HERO_FACTION_MAP: dict = {
    # --- Greek pantheon + nymph / minor ----------------------------------
    "Hoplite": "greek",
    "Athena": "greek", "Aphrodite": "greek", "Artemis": "greek",
    "Medusa": "greek", "Hera": "greek", "Persephone": "greek",
    "Nyx": "greek", "Demeter": "greek", "Hecate": "greek",
    "Selene": "greek", "Iris": "greek", "Echo": "greek",
    "Daphne": "greek", "Chloris": "greek", "Aura": "greek",
    "Hestia": "greek", "Nike": "greek", "Psyche": "greek",
    # --- Japanese pantheon (Shinto) --------------------------------------
    "Amaterasu": "japanese", "Tsukuyomi": "japanese",
    "Susanoo": "japanese", "Izanami": "japanese",
    "Sakuya": "japanese", "Kaguya": "japanese",
    "Inari": "japanese", "Benzaiten": "japanese",
    "Raijin": "japanese", "Fujin": "japanese",
    # --- Norse pantheon --------------------------------------------------
    "Freya": "norse", "Valkyrie": "norse",
    # Egyptian / Celtic: nessun eroe attualmente presente nel roster.
}

def resolve_hero_faction(name: str, existing: str | None = None) -> str | None:
    """Ritorna la faction per il nome eroe. Se esiste già un valore
    canonico lo preserva (evita di sovrascrivere eventuali fix manuali)."""
    if existing and str(existing).lower() in {"greek", "norse", "egyptian", "japanese", "celtic"}:
        return existing
    return HERO_FACTION_MAP.get(name)

@app.on_event("startup")
async def seed_database():
    """Seed heroes if not present"""
    count = await db.heroes.count_documents({})
    if count >= 30:
        # Migrazione one-shot: popola il campo faction sui record DB esistenti
        # che non ce l'hanno (o ce l'hanno nullo). Solo update mirati per
        # nome presente in HERO_FACTION_MAP. Nessun altro campo viene toccato.
        missing = await db.heroes.find(
            {"$or": [{"faction": None}, {"faction": {"$exists": False}}]},
            {"name": 1, "faction": 1},
        ).to_list(1000)
        updated = 0
        for h in missing:
            f = resolve_hero_faction(h.get("name", ""), h.get("faction"))
            if f:
                await db.heroes.update_one({"_id": h["_id"]}, {"$set": {"faction": f}})
                updated += 1
        if updated:
            print(f"[faction-migration] Populated faction on {updated} existing heroes")
        return
    
    await db.heroes.delete_many({})
    
    heroes_data = [
        {"id": "greek_hoplite", "name": "Hoplite", "rarity": 3, "element": "earth", "faction": "greek", "hero_class": "Tank", "image": "asset:greek_hoplite:splash", "base_stats": {"hp": 8500, "attack": 1200, "defense": 1100, "speed": 95, "crit_rate": 0.10, "crit_damage": 1.5}},
        {"name": "Amaterasu", "rarity": 6, "element": "fire", "hero_class": "DPS", "base_stats": {"hp": 12000, "attack": 2800, "defense": 900, "speed": 130, "crit_rate": 0.25, "crit_damage": 2.0}},
        {"name": "Tsukuyomi", "rarity": 6, "element": "dark", "hero_class": "DPS", "base_stats": {"hp": 11000, "attack": 3000, "defense": 800, "speed": 140, "crit_rate": 0.30, "crit_damage": 2.2}},
        {"name": "Susanoo", "rarity": 6, "element": "wind", "hero_class": "Tank", "base_stats": {"hp": 15000, "attack": 2200, "defense": 1400, "speed": 110, "crit_rate": 0.15, "crit_damage": 1.6}},
        {"name": "Izanami", "rarity": 6, "element": "dark", "hero_class": "Support", "base_stats": {"hp": 13000, "attack": 2000, "defense": 1100, "speed": 125, "crit_rate": 0.18, "crit_damage": 1.7}},
        {"name": "Athena", "rarity": 5, "element": "light", "hero_class": "Tank", "base_stats": {"hp": 14000, "attack": 1800, "defense": 1300, "speed": 105, "crit_rate": 0.12, "crit_damage": 1.5}},
        {"name": "Aphrodite", "rarity": 5, "element": "water", "hero_class": "Support", "base_stats": {"hp": 11500, "attack": 1600, "defense": 1000, "speed": 120, "crit_rate": 0.15, "crit_damage": 1.5}},
        {"name": "Artemis", "rarity": 5, "element": "wind", "hero_class": "DPS", "base_stats": {"hp": 10000, "attack": 2400, "defense": 750, "speed": 145, "crit_rate": 0.28, "crit_damage": 1.9}},
        {"name": "Freya", "rarity": 5, "element": "light", "hero_class": "DPS", "base_stats": {"hp": 10500, "attack": 2500, "defense": 800, "speed": 135, "crit_rate": 0.22, "crit_damage": 1.8}},
        {"name": "Valkyrie", "rarity": 5, "element": "wind", "hero_class": "Tank", "base_stats": {"hp": 13000, "attack": 1900, "defense": 1200, "speed": 115, "crit_rate": 0.14, "crit_damage": 1.5}},
        {"name": "Medusa", "rarity": 5, "element": "earth", "hero_class": "DPS", "base_stats": {"hp": 10800, "attack": 2300, "defense": 850, "speed": 125, "crit_rate": 0.20, "crit_damage": 1.8}},
        {"name": "Hera", "rarity": 4, "element": "light", "hero_class": "Support", "base_stats": {"hp": 10000, "attack": 1500, "defense": 900, "speed": 110, "crit_rate": 0.12, "crit_damage": 1.5}},
        {"name": "Persephone", "rarity": 4, "element": "dark", "hero_class": "DPS", "base_stats": {"hp": 9500, "attack": 2000, "defense": 700, "speed": 130, "crit_rate": 0.20, "crit_damage": 1.7}},
        {"name": "Nyx", "rarity": 4, "element": "dark", "hero_class": "DPS", "base_stats": {"hp": 9000, "attack": 2100, "defense": 650, "speed": 135, "crit_rate": 0.22, "crit_damage": 1.7}},
        {"name": "Demeter", "rarity": 4, "element": "earth", "hero_class": "Support", "base_stats": {"hp": 11000, "attack": 1400, "defense": 950, "speed": 100, "crit_rate": 0.10, "crit_damage": 1.4}},
        {"name": "Hecate", "rarity": 4, "element": "dark", "hero_class": "DPS", "base_stats": {"hp": 9200, "attack": 1950, "defense": 720, "speed": 128, "crit_rate": 0.18, "crit_damage": 1.6}},
        {"name": "Selene", "rarity": 4, "element": "light", "hero_class": "Support", "base_stats": {"hp": 10500, "attack": 1550, "defense": 880, "speed": 112, "crit_rate": 0.13, "crit_damage": 1.5}},
        {"name": "Sakuya", "rarity": 3, "element": "water", "hero_class": "Support", "base_stats": {"hp": 9000, "attack": 1300, "defense": 800, "speed": 108, "crit_rate": 0.10, "crit_damage": 1.4}},
        {"name": "Kaguya", "rarity": 3, "element": "light", "hero_class": "DPS", "base_stats": {"hp": 8500, "attack": 1700, "defense": 650, "speed": 120, "crit_rate": 0.16, "crit_damage": 1.5}},
        {"name": "Inari", "rarity": 3, "element": "fire", "hero_class": "DPS", "base_stats": {"hp": 8000, "attack": 1800, "defense": 600, "speed": 125, "crit_rate": 0.18, "crit_damage": 1.6}},
        {"name": "Benzaiten", "rarity": 3, "element": "water", "hero_class": "Support", "base_stats": {"hp": 9500, "attack": 1200, "defense": 850, "speed": 105, "crit_rate": 0.10, "crit_damage": 1.3}},
        {"name": "Raijin", "rarity": 3, "element": "wind", "hero_class": "DPS", "base_stats": {"hp": 8200, "attack": 1750, "defense": 620, "speed": 135, "crit_rate": 0.15, "crit_damage": 1.5}},
        {"name": "Fujin", "rarity": 3, "element": "wind", "hero_class": "Tank", "base_stats": {"hp": 10000, "attack": 1400, "defense": 900, "speed": 110, "crit_rate": 0.10, "crit_damage": 1.4}},
        {"name": "Iris", "rarity": 2, "element": "light", "hero_class": "Support", "base_stats": {"hp": 7500, "attack": 1100, "defense": 700, "speed": 105, "crit_rate": 0.08, "crit_damage": 1.3}},
        {"name": "Echo", "rarity": 2, "element": "wind", "hero_class": "DPS", "base_stats": {"hp": 7000, "attack": 1400, "defense": 550, "speed": 115, "crit_rate": 0.12, "crit_damage": 1.4}},
        {"name": "Daphne", "rarity": 2, "element": "earth", "hero_class": "Tank", "base_stats": {"hp": 8500, "attack": 1000, "defense": 800, "speed": 95, "crit_rate": 0.08, "crit_damage": 1.3}},
        {"name": "Chloris", "rarity": 2, "element": "earth", "hero_class": "Support", "base_stats": {"hp": 8000, "attack": 1050, "defense": 750, "speed": 100, "crit_rate": 0.08, "crit_damage": 1.3}},
        {"name": "Aura", "rarity": 1, "element": "wind", "hero_class": "DPS", "base_stats": {"hp": 6000, "attack": 1200, "defense": 450, "speed": 110, "crit_rate": 0.10, "crit_damage": 1.3}},
        {"name": "Hestia", "rarity": 1, "element": "fire", "hero_class": "Support", "base_stats": {"hp": 6500, "attack": 900, "defense": 600, "speed": 95, "crit_rate": 0.06, "crit_damage": 1.2}},
        {"name": "Nike", "rarity": 1, "element": "light", "hero_class": "Tank", "base_stats": {"hp": 7000, "attack": 850, "defense": 700, "speed": 90, "crit_rate": 0.05, "crit_damage": 1.2}},
        {"name": "Psyche", "rarity": 1, "element": "water", "hero_class": "Support", "base_stats": {"hp": 6200, "attack": 950, "defense": 550, "speed": 100, "crit_rate": 0.07, "crit_damage": 1.2}},
    ]
    
    for hero in heroes_data:
        if "id" not in hero:
            hero["id"] = str(uuid.uuid4())
        # Popolamento faction: preserva eventuale valore già presente (es.
        # greek_hoplite nel seed), altrimenti risolve via HERO_FACTION_MAP.
        hero["faction"] = resolve_hero_faction(hero.get("name", ""), hero.get("faction"))
        hero["created_at"] = datetime.utcnow()
        await db.heroes.insert_one(hero)
    
    print(f"Seeded {len(heroes_data)} heroes into database")

# ===================== BOT SYSTEM =====================
from bot_system import initialize_bots, run_bot_cycle

bot_task_handle = None

@app.on_event("startup")
async def start_bot_system():
    """Initialize bots and start background cycle."""
    global bot_task_handle
    # Wait for DB to be ready
    await asyncio.sleep(5)
    try:
        count = await initialize_bots("default", 20)
        print(f"Bot system ready: {count} bots on server 'default'")
    except Exception as e:
        print(f"Bot init error: {e}")
    
    # Start background task
    bot_task_handle = asyncio.create_task(bot_background_loop())

async def bot_background_loop():
    """Run bot actions every 3-5 minutes."""
    while True:
        try:
            await asyncio.sleep(random.randint(180, 300))  # 3-5 min
            await run_bot_cycle("default")
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Bot cycle error: {e}")
            await asyncio.sleep(60)

@app.post("/api/admin/bots/run-cycle")
async def admin_run_bot_cycle(current_user: dict = Depends(get_current_user)):
    """Manually trigger a bot cycle (for testing)."""
    try:
        await run_bot_cycle("default")
        return {"success": True, "message": "Bot cycle completed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/admin/bots/status")
async def admin_bot_status(current_user: dict = Depends(get_current_user)):
    """Get status of all bots."""
    bots = await db.users.find({"is_bot": True}, {"password": 0}).to_list(200)
    tiers = {}
    for b in bots:
        tier = b.get("bot_tier", "unknown")
        tiers[tier] = tiers.get(tier, 0) + 1
    return {
        "total_bots": len(bots),
        "tier_distribution": tiers,
        "bots": [{
            "username": b["username"], "tier": b.get("bot_tier"), "personality": b.get("bot_personality"),
            "level": b.get("level"), "last_action": str(b.get("bot_last_action", "")),
        } for b in bots[:30]],
    }

@app.get("/api/health")
async def health():
    bot_count = await db.users.count_documents({"is_bot": True})
    return {"status": "ok", "game": "Divine Waifus", "version": "1.0.0", "bots": bot_count}

# ===================== HOPLITE REEL (DEV VISUAL VALIDATION) =====================
# Pagina helper: mostra i frame catturati in /app/tmp/hop/ come reel visuale
# per validazione rapida delle animazioni Hoplite. Serve inline via img base64.
@app.get("/api/hoplite-reel")
async def hoplite_reel(crop: bool = False, curated: bool = False, v2: bool = False):
    from fastapi.responses import HTMLResponse
    import base64, glob
    if v2:
        # V2: frames del nuovo rig (cartella /app/tmp/hop2), con label per fase.
        CURATED2 = [
            ("00_idle.png",         "IDLE baseline",    "Pose base — spear level, shield up, legs radicate"),
            ("01_windup.png",       "RITRAZIONE",       "Phase 1 (~80ms) — spear tirato indietro +70, rot +8°, torso +2°"),
            ("02_thrust_mid.png",   "AFFONDO mid",      "Phase 2 (~190ms) — spear in corsa, torso -4° lean forward"),
            ("03_impact.png",       "AFFONDO peak",     "Phase 2 end (~290ms) — spear thrust max -180, massima estensione"),
            ("04_impact_end.png",   "IMPATTO hold",     "Phase 3 (~370ms) — hold a -200, max thrust + body weight forward"),
            ("05_return.png",       "RITORNO guardia",  "Phase 4 (~550ms) — rientro easing out, torso si raddrizza"),
            ("06_idle_back.png",    "IDLE ripristino",  "Post-return (~850ms) — tutto a 0, home position recuperata"),
        ]
        imgs_html = ""
        for fname, label, caption in CURATED2:
            p = f"/app/tmp/hop2/{fname}"
            try:
                with open(p, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                imgs_html += f'<div class="cell"><div class="lbl">{label}</div><div class="cap">{caption}</div><img src="data:image/png;base64,{b64}"/></div>'
            except Exception:
                pass
        html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
body{{margin:0;padding:16px;background:#0a0a0a;color:#fff;font-family:monospace}}
.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}}
.cell{{position:relative;border:2px solid #FFB347;background:#0a0a0a;border-radius:8px;overflow:hidden}}
.cell img{{width:100%;display:block}}
.lbl{{position:absolute;top:0;left:0;background:#FF0055;color:#fff;padding:6px 14px;font-size:15px;font-weight:900;z-index:10;border-bottom-right-radius:10px;letter-spacing:1px}}
.cap{{position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,0.88);color:#FFD700;padding:8px 12px;font-size:12px;z-index:10}}
h1{{font-size:22px;margin:6px 0 18px 4px;color:#FFD700}}
.legend{{background:#1a1410;border:1px solid #FFB347;padding:14px;border-radius:6px;margin-bottom:20px;font-size:12px;color:#FFCC99;line-height:1.6}}
</style></head>
<body>
<h1>⚔️ HOPLITE — AFFONDO DI FALANGE (RIG-BASED LAYER ANIMATION)</h1>
<div class="legend">
<b>PIPELINE:</b> 7 layer PNG separati (hair / legs / skirt / torso / shield_arm / spear_arm / head_helmet) · pivot anatomici (bacino, spalla sx lancia, spalla dx scudo) · idle breathing SEMPRE attivo in background · combat deltas additivi on top · gambe FISSE (disciplina tank) · no drift dalla cella.
</div>
<div class="grid">{imgs_html}</div>
</body></html>"""
        return HTMLResponse(content=html)
    folder = "/app/tmp/hop/crop" if crop else "/app/tmp/hop"
    if curated:
        CURATED = [
            (0,  "IDLE",          "Hoplite in home position, spear relaxed"),
            (19, "ATTACK wind-up", "Inizio forward lean + spear raising"),
            (21, "ATTACK thrust",  "CONFIRMED: leaning forward, spear extended"),
            (23, "ATTACK follow",  "Mid-return, shield still forward"),
            (25, "SKILL AFTERMATH","Log: 'Hoplite Terremoto -> Mago Corotto' — post-impact"),
            (17, "HIT reaction",   "Red color shift + heal +1,517 floating (damaged then healed)"),
        ]
        items = CURATED
        cols = 2
    else:
        files = sorted(glob.glob(f"{folder}/f*.jpg"))
        items = [(i, f"f{i:03d}", "") for i in range(len(files))]
        cols = 3 if crop else 4
    imgs_html = ""
    for idx, label, caption in items:
        p = f"{folder}/f{idx:03d}.jpg"
        try:
            with open(p, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            imgs_html += f'<div class="cell"><div class="lbl">{label}</div><div class="cap">{caption}</div><img src="data:image/jpeg;base64,{b64}"/></div>'
        except Exception:
            pass
    extra = ""
    if curated:
        extra = """<div class="note"><b>NOTA DEATH:</b> non catturata in questa battaglia (team ha vinto 6/6 in 2 turni, nessun player KO).
        Per validare l'animazione death serve un combattimento dove Hoplite muore — es. PvP contro avversario più forte,
        oppure Tower of Infinity stage avanzato. Posso orchestrarlo in un run successivo se confermi.</div>"""
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
body{{margin:0;padding:10px;background:#000;color:#fff;font-family:monospace}}
.grid{{display:grid;grid-template-columns:repeat({cols},1fr);gap:12px}}
.cell{{position:relative;border:2px solid #FFB347;background:#111;border-radius:6px;overflow:hidden}}
.cell img{{width:100%;display:block}}
.lbl{{position:absolute;top:0;left:0;background:#FF0055;color:#fff;padding:5px 12px;font-size:15px;font-weight:900;z-index:10;border-bottom-right-radius:8px}}
.cap{{position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,0.85);color:#FFD700;padding:6px 10px;font-size:12px;z-index:10}}
h1{{font-size:18px;margin:6px 0 14px 4px;color:#FFD700}}
.note{{background:#2a1a1a;border:2px solid #FFB347;padding:14px;border-radius:6px;margin-top:20px;font-size:13px;color:#FFCC99;line-height:1.5}}
</style></head>
<body><h1>⚔️ HOPLITE ANIMATION VALIDATION — 1x speed</h1>
<div class="grid">{imgs_html}</div>
{extra}
</body></html>"""
    return HTMLResponse(content=html)

# ===================== EXPO GO CONNECT HELPER =====================
# Pagina HTML auto-contenuta: il dev apre questa URL dal browser del telefono
# e può toccare il pulsante "Open in Expo Go" (deep link exp://) per lanciare
# Expo Go direttamente con l'URL diretto (preview.emergentagent.com), senza
# passare dal proxy cluster-2.preview.emergentcf.cloud che al momento è 403.
# Include anche il QR code generato lato server in SVG (no dipendenze JS).
@app.get("/api/expo-connect")
async def expo_connect():
    from fastapi.responses import HTMLResponse
    import qrcode
    import qrcode.image.svg
    import io
    # Usa l'hostname del request per costruire l'URL — funziona sia in preview
    # che in locale. Default → preview.emergentagent.com.
    host = os.getenv("EXPO_PUBLIC_PREVIEW_HOST", "game-portal-327.preview.emergentagent.com")
    exp_url = f"exp://{host}"
    https_url = f"https://{host}"

    # Genera QR come SVG inline (nessuna dipendenza extra client-side)
    factory = qrcode.image.svg.SvgImage
    qr_img = qrcode.make(exp_url, image_factory=factory, box_size=10, border=2)
    buf = io.BytesIO()
    qr_img.save(buf)
    qr_svg = buf.getvalue().decode("utf-8")
    # Rimuove xml declaration per embedding inline
    qr_svg = qr_svg.replace('<?xml version="1.0" encoding="UTF-8"?>\n', '')

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Divine Waifus · Connect Expo Go</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #0D0D2B 0%, #1A0A2E 100%);
    color: #fff;
    min-height: 100vh;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
  }}
  h1 {{
    font-size: 22px; letter-spacing: 2px; margin: 0 0 8px 0; color: #FFD700;
    text-shadow: 0 0 20px rgba(255,215,0,0.4);
  }}
  .sub {{ font-size: 12px; color: #aaa; margin-bottom: 28px; text-align: center; }}
  .card {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,215,0,0.2);
    border-radius: 14px;
    padding: 22px;
    max-width: 380px;
    width: 100%;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
  }}
  .btn-open {{
    display: block; text-decoration: none;
    background: linear-gradient(135deg, #FF6B35 0%, #FF4444 100%);
    color: #fff;
    font-size: 18px; font-weight: 900; letter-spacing: 1px;
    text-align: center;
    padding: 18px 20px;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(255,107,53,0.4);
    margin-bottom: 18px;
    transition: transform 0.1s;
  }}
  .btn-open:active {{ transform: scale(0.97); }}
  .qr-wrap {{
    background: #fff; border-radius: 10px; padding: 14px;
    margin: 18px auto; width: fit-content;
  }}
  .qr-wrap svg {{ display: block; width: 220px; height: 220px; }}
  .url-box {{
    background: rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 10px 12px;
    font-family: monospace;
    font-size: 11px;
    color: #44AAFF;
    word-break: break-all;
    margin: 10px 0;
  }}
  .step {{
    background: rgba(68,170,255,0.08);
    border-left: 3px solid #44AAFF;
    padding: 10px 14px;
    border-radius: 6px;
    font-size: 13px;
    margin: 8px 0;
  }}
  .step strong {{ color: #FFD700; }}
  .footer {{
    font-size: 10px; color: #666; margin-top: 24px; text-align: center;
  }}
  .warn {{
    background: rgba(255,68,68,0.1);
    border: 1px solid rgba(255,68,68,0.3);
    border-radius: 8px;
    padding: 10px;
    font-size: 11px;
    color: #FF8888;
    margin-bottom: 16px;
  }}
</style>
</head>
<body>
  <h1>⚔️ DIVINE WAIFUS</h1>
  <div class="sub">Expo Go Connect · Dev Bypass</div>

  <div class="card">
    <div class="warn">
      Il proxy QR di default è al momento <b>offline</b>.
      Usa questa pagina per connettere Expo Go direttamente.
    </div>

    <a class="btn-open" href="{exp_url}">📱 Apri in Expo Go</a>

    <div class="step"><strong>Metodo 1:</strong> Tocca il pulsante qui sopra dal browser del telefono. Expo Go si aprirà automaticamente.</div>

    <div class="step"><strong>Metodo 2:</strong> Apri Expo Go → "Scan QR code" e inquadra il QR qui sotto.</div>

    <div class="qr-wrap">
      {qr_svg}
    </div>

    <div class="step"><strong>Metodo 3:</strong> Copia e incolla l'URL manualmente in Expo Go.</div>
    <div class="url-box">{exp_url}</div>
  </div>

  <div class="footer">Divine Waifus dev console · {host}</div>
</body>
</html>
"""
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
