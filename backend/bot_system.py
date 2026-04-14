"""
Divine Waifus - Bot System
Intelligent bots that play, compete, and chat like real players.
4 AI tiers: low, medium, medium-high, high
Each bot has personality, resource level, and play style.
"""
import os
import random
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from motor.motor_asyncio import AsyncIOMotorClient
from emergentintegrations.llm.chat import LlmChat, UserMessage

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "divine_waifus")
LLM_KEY = os.getenv("EMERGENT_LLM_KEY", "")

# ===================== BOT NAMES =====================
ITALIAN_NAMES = [
    "Luna_Divina", "ShadowKitsune", "AkemiStar", "DragonHime", "SakuraBlaze",
    "NightFury99", "CrystalMage", "ThunderGirl", "IcePhoenix", "FireLotus",
    "MysticRose", "BladeDancer", "CosmicNinja", "SilverWolf", "GoldenEagle",
    "DarkAngel_X", "LightBringer", "StormQueen", "VoidWalker", "SunGoddess",
    "MoonSlayer", "StarHunter", "DiamondFist", "RubyHeart", "SapphireEye",
    "EmeraldBlade", "OnyxShadow", "PlatinumKing", "BronzeWarrior", "IronMaiden",
    "CelestialOne", "InfernoKid", "AquaMarine", "TerraForce", "WindRider",
    "xXDivineXx", "ProGamer_IT", "WaifuLover", "GachaKing99", "Leggendario",
]

PERSONALITIES = {
    "competitive": "Sei un giocatore competitivo, parli di classifiche, PvP e strategie. Sei diretto e un po' arrogante.",
    "friendly": "Sei un giocatore socievole e amichevole, aiuti i nuovi, fai complimenti e parli di team building.",
    "whale": "Sei un giocatore che spende molto, parli dei tuoi eroi rari, pull fortunate e equipaggiamenti leggendari.",
    "casual": "Sei un giocatore casual, fai domande, commenti divertenti, parli di eventi e della storia del gioco.",
    "veteran": "Sei un veterano del gioco, dai consigli, parli di meta, sinergie e formazioni ottimali.",
    "newbie": "Sei un nuovo giocatore, fai domande da principiante, ti entusiasmi per ogni cosa, chiedi consigli.",
}

# ===================== AI TIER CONFIG =====================
AI_TIERS = {
    "low": {
        "gems_range": (500, 2000),
        "gold_range": (10000, 50000),
        "max_rarity": 4,
        "gacha_banner": "standard",
        "pvp_skill": 0.4,
        "tower_max": 15,
        "chat_frequency": 0.15,  # chance per cycle
        "personality_pool": ["newbie", "casual"],
    },
    "medium": {
        "gems_range": (2000, 8000),
        "gold_range": (50000, 200000),
        "max_rarity": 5,
        "gacha_banner": "standard",
        "pvp_skill": 0.55,
        "tower_max": 35,
        "chat_frequency": 0.25,
        "personality_pool": ["casual", "friendly", "competitive"],
    },
    "medium_high": {
        "gems_range": (8000, 25000),
        "gold_range": (200000, 800000),
        "max_rarity": 5,
        "gacha_banner": "elemental",
        "pvp_skill": 0.70,
        "tower_max": 60,
        "chat_frequency": 0.30,
        "personality_pool": ["competitive", "veteran", "friendly"],
    },
    "high": {
        "gems_range": (25000, 100000),
        "gold_range": (800000, 5000000),
        "max_rarity": 6,
        "gacha_banner": "premium",
        "pvp_skill": 0.85,
        "tower_max": 100,
        "chat_frequency": 0.20,
        "personality_pool": ["whale", "competitive", "veteran"],
    },
}


async def get_db():
    client = AsyncIOMotorClient(MONGO_URL)
    return client[DB_NAME]


async def generate_bot_chat(bot_name: str, personality: str, context: str = "") -> str:
    """Generate a chat message using LLM that sounds like a real player."""
    if not LLM_KEY:
        return _fallback_chat(personality)
    
    try:
        system_msg = f"""Sei '{bot_name}', un giocatore del gioco mobile 'Divine Waifus' (RPG gacha con dee mitologiche anime).
{PERSONALITIES.get(personality, PERSONALITIES['casual'])}

REGOLE IMPORTANTI:
- Scrivi SOLO in italiano informale/slang da gamer
- Messaggi BREVI (max 15 parole)
- NO emoji eccessivi (max 1-2)
- Parla come un vero giocatore su chat di gioco
- Puoi menzionare: eroi (Amaterasu, Tsukuyomi, Athena, Freya, etc), rarita (5 stelle, 6 stelle), banner, PvP arena, torre, territori, gilda
- A volte fai errori di battitura minori per sembrare reale
- NON rivelare mai di essere un bot
{context}"""

        chat = LlmChat(
            api_key=LLM_KEY,
            session_id=f"bot_{bot_name}_{random.randint(1,9999)}",
            system_message=system_msg,
        ).with_model("openai", "gpt-4.1-nano")

        user_message = UserMessage(text="Scrivi UN messaggio breve nella chat del gioco. Solo il messaggio, niente altro.")
        response = await chat.send_message(user_message)
        
        # Clean up response
        msg = response.strip().strip('"').strip("'")
        if len(msg) > 150:
            msg = msg[:150]
        return msg
    except Exception as e:
        print(f"LLM chat error for {bot_name}: {e}")
        return _fallback_chat(personality)


def _fallback_chat(personality: str) -> str:
    """Fallback messages if LLM fails."""
    messages = {
        "competitive": [
            "chi vuole fare arena? sono top 10", "la mia Amaterasu one-shotta tutto lol",
            "appena salito di 200 trofei in arena", "qualcuno ha consigli per team PvP?",
            "primo nella torre, chi mi sfida?", "ho appena conquistato l'Olimpo 💪",
        ],
        "friendly": [
            "ciao a tutti! come va?", "qualcuno vuole fare gilda insieme?",
            "bel team! che formazione usi?", "buona fortuna con i pull ragazzi",
            "benvenuto al nuovo! chiedi pure", "gg a tutti per l'evento di oggi",
        ],
        "whale": [
            "6 stelle al primo pull 😎", "ho tutti i divini finalmente",
            "il banner premium è troppo forte", "Tsukuyomi 6* è un mostro",
            "ho speso un po ma ne vale la pena", "equipment leggendario droppato!",
        ],
        "casual": [
            "che bello questo gioco", "qualcuno sa come funziona la torre?",
            "ho pullato Athena! è forte?", "gli eventi di oggi sono fighi",
            "quanto costa il banner premium?", "la storia è troppo bella",
        ],
        "veteran": [
            "meta attuale: fuoco + luce è OP", "per la torre serve almeno 1 healer",
            "Freya è la miglior DPS wind", "sinergize vento-terra sono sottovalutate",
            "consiglio: salvate gemme per il prossimo banner", "formazione 2-2-2 è la più bilanciata",
        ],
        "newbie": [
            "raga come si evocano i personaggi?", "sono nuovo, consigli?",
            "wow ho preso un 4 stelle!!", "come funziona la gilda?",
            "che bello questo gioco lo ho scoperto ora", "qualcuno mi spiega l'arena?",
        ],
    }
    pool = messages.get(personality, messages["casual"])
    return random.choice(pool)


async def create_bot_profile(db, tier: str, server_id: str = "default") -> dict:
    """Create a new bot player with full profile."""
    config = AI_TIERS[tier]
    name = random.choice(ITALIAN_NAMES) + str(random.randint(1, 999))
    personality = random.choice(config["personality_pool"])
    
    bot_id = str(uuid.uuid4())
    gems = random.randint(*config["gems_range"])
    gold = random.randint(*config["gold_range"])
    
    # Create user
    bot_user = {
        "id": bot_id,
        "email": f"bot_{bot_id[:8]}@divine.bot",
        "password": "bot_no_login",
        "username": name,
        "level": random.randint(5 if tier == "low" else 15 if tier == "medium" else 30 if tier == "medium_high" else 50, 
                                20 if tier == "low" else 40 if tier == "medium" else 65 if tier == "medium_high" else 99),
        "experience": 0,
        "gold": gold,
        "gems": gems,
        "stamina": 100,
        "max_stamina": 100,
        "titles": ["Novizio"],
        "active_title": random.choice(["Novizio", "Guerriero", "Collezionista"] if tier != "high" else ["Leggenda", "Campione", "Divino"]),
        "faction": random.choice(["olympus", "asgard", "yomi", "nirvana"]),
        "guild_id": None,
        "is_bot": True,
        "bot_tier": tier,
        "bot_personality": personality,
        "bot_server": server_id,
        "bot_last_action": datetime.utcnow(),
        "bot_chat_cooldown": datetime.utcnow(),
        "created_at": datetime.utcnow(),
    }
    await db.users.insert_one(bot_user)
    
    # Give heroes based on tier
    all_heroes = await db.heroes.find({}).to_list(100)
    max_rarity = config["max_rarity"]
    eligible = [h for h in all_heroes if h["rarity"] <= max_rarity]
    
    num_heroes = random.randint(5, 12) if tier == "low" else random.randint(10, 20) if tier == "medium" else random.randint(15, 25) if tier == "medium_high" else random.randint(20, 30)
    
    selected = random.sample(eligible, min(num_heroes, len(eligible)))
    # High tier gets guaranteed 6-stars
    if tier == "high":
        divine_heroes = [h for h in all_heroes if h["rarity"] == 6]
        selected.extend(random.sample(divine_heroes, min(3, len(divine_heroes))))
    if tier in ["medium_high", "high"]:
        mythic_heroes = [h for h in all_heroes if h["rarity"] == 5]
        selected.extend(random.sample(mythic_heroes, min(4, len(mythic_heroes))))
    
    bot_heroes = []
    for hero in selected:
        level = random.randint(1, 15) if tier == "low" else random.randint(10, 40) if tier == "medium" else random.randint(25, 70) if tier == "medium_high" else random.randint(50, 100)
        uh = {
            "id": str(uuid.uuid4()),
            "user_id": bot_id,
            "hero_id": hero["id"],
            "level": level,
            "experience": 0,
            "stars": hero["rarity"],
            "obtained_at": datetime.utcnow(),
        }
        await db.user_heroes.insert_one(uh)
        bot_heroes.append(uh)
    
    # Set up team
    team_heroes = sorted(bot_heroes, key=lambda x: x.get("level", 1), reverse=True)[:6]
    formation = []
    for i, uh in enumerate(team_heroes):
        row = i // 2
        col = i % 2
        formation.append({"x": 3 if col == 0 else 5, "y": [1, 4, 7][row], "user_hero_id": uh["id"]})
    
    total_power = 0
    for uh in team_heroes:
        hero = next((h for h in all_heroes if h["id"] == uh["hero_id"]), None)
        if hero:
            stats = hero.get("base_stats", {})
            power = (stats.get("attack", 100) + stats.get("defense", 50) + stats.get("hp", 1000) // 10 + stats.get("speed", 10))
            power = int(power * (1 + (uh["level"] - 1) * 0.05) * (1 + hero["rarity"] * 0.2))
            total_power += power
    
    await db.teams.update_one(
        {"user_id": bot_id, "is_active": True},
        {"$set": {"user_id": bot_id, "is_active": True, "formation": formation, "total_power": total_power}},
        upsert=True
    )
    
    # PvP data
    trophies = random.randint(50, 300) if tier == "low" else random.randint(200, 800) if tier == "medium" else random.randint(600, 1500) if tier == "medium_high" else random.randint(1200, 3000)
    await db.pvp_data.insert_one({
        "user_id": bot_id, "trophies": trophies,
        "wins": random.randint(10, trophies // 3), "losses": random.randint(5, trophies // 5),
        "streak": random.randint(0, 5), "daily_battles": 0,
    })
    
    # Cosmetics for high tier
    if tier in ["medium_high", "high"]:
        auras = random.sample(["flame", "ice", "thunder", "shadow", "divine"], random.randint(1, 3))
        frames = random.sample(["silver", "gold", "diamond", "legendary"], random.randint(1, 2))
        await db.user_cosmetics.insert_one({
            "user_id": bot_id,
            "owned_auras": auras, "owned_frames": ["bronze"] + frames,
            "active_aura": random.choice(auras), "active_frame": random.choice(frames),
        })
    
    print(f"Created bot: {name} (tier={tier}, personality={personality}, heroes={len(selected)}, power={total_power})")
    return bot_user


async def bot_action_cycle(db, bot_user: dict):
    """Execute one action cycle for a bot."""
    bot_id = bot_user["id"]
    tier = bot_user.get("bot_tier", "low")
    config = AI_TIERS[tier]
    
    actions_done = []
    
    # Random action selection based on tier
    action_roll = random.random()
    
    if action_roll < 0.25:
        # PvP battle
        pvp = await db.pvp_data.find_one({"user_id": bot_id})
        if pvp and pvp.get("daily_battles", 0) < 10:
            trophy_change = random.randint(10, 25) if random.random() < config["pvp_skill"] else -random.randint(5, 15)
            await db.pvp_data.update_one({"user_id": bot_id}, {
                "$inc": {"trophies": trophy_change, "wins": 1 if trophy_change > 0 else 0, "losses": 0 if trophy_change > 0 else 1, "daily_battles": 1}
            })
            actions_done.append(f"PvP: {'+' if trophy_change > 0 else ''}{trophy_change} trofei")
    
    elif action_roll < 0.45:
        # Tower climb
        tower = await db.tower_progress.find_one({"user_id": bot_id})
        if not tower:
            tower = {"user_id": bot_id, "floor": 1, "highest_floor": 1}
            await db.tower_progress.insert_one(tower)
        if tower.get("floor", 1) < config["tower_max"]:
            if random.random() < config["pvp_skill"]:
                new_floor = tower["floor"] + 1
                await db.tower_progress.update_one({"user_id": bot_id}, {"$set": {"floor": new_floor, "highest_floor": max(tower.get("highest_floor", 1), new_floor)}})
                actions_done.append(f"Torre: piano {new_floor}")
    
    elif action_roll < 0.60:
        # Gacha pull (if has gems)
        user = await db.users.find_one({"id": bot_id})
        banner = config["gacha_banner"]
        cost = 100 if banner == "standard" else 120 if banner == "elemental" else 200
        if user and user.get("gems", 0) >= cost:
            all_heroes = await db.heroes.find({}).to_list(100)
            max_r = config["max_rarity"]
            rarity = random.choices([1,2,3,4,5,6], weights=[0.3,0.3,0.2,0.12,0.06,0.02])[0]
            rarity = min(rarity, max_r)
            eligible = [h for h in all_heroes if h["rarity"] == rarity]
            if not eligible:
                eligible = [h for h in all_heroes if h["rarity"] <= max_r]
            if eligible:
                hero = random.choice(eligible)
                uh = {"id": str(uuid.uuid4()), "user_id": bot_id, "hero_id": hero["id"], "level": 1, "experience": 0, "stars": hero["rarity"], "obtained_at": datetime.utcnow()}
                await db.user_heroes.insert_one(uh)
                await db.users.update_one({"id": bot_id}, {"$inc": {"gems": -cost}})
                actions_done.append(f"Gacha: {hero['name']} ({hero['rarity']}★)")
    
    elif action_roll < 0.75:
        # Territory attack
        user = await db.users.find_one({"id": bot_id})
        if user and user.get("guild_id"):
            territories = ["volcano", "ocean", "forest", "skylands", "sanctum", "abyss", "olympus"]
            target = random.choice(territories)
            if random.random() < config["pvp_skill"]:
                await db.territory_control.update_one(
                    {"territory_id": target},
                    {"$set": {"guild_id": user["guild_id"], "defense_power": random.randint(5000, 50000), "captured_at": datetime.utcnow(), "captured_by": bot_id}},
                    upsert=True
                )
                actions_done.append(f"Territorio: conquistato {target}")
    
    # Chat message (based on frequency)
    if random.random() < config["chat_frequency"]:
        cooldown = bot_user.get("bot_chat_cooldown", datetime.min)
        if isinstance(cooldown, str):
            cooldown = datetime.min
        if datetime.utcnow() - cooldown > timedelta(minutes=random.randint(10, 40)):
            personality = bot_user.get("bot_personality", "casual")
            context = f"Ultime azioni: {', '.join(actions_done)}" if actions_done else ""
            message = await generate_bot_chat(bot_user["username"], personality, context)
            
            await db.plaza_chat.insert_one({
                "id": str(uuid.uuid4()),
                "user_id": bot_id,
                "username": bot_user["username"],
                "message": message,
                "timestamp": datetime.utcnow(),
            })
            await db.users.update_one({"id": bot_id}, {"$set": {"bot_chat_cooldown": datetime.utcnow()}})
            actions_done.append(f"Chat: '{message[:40]}...'")
    
    # Update last action
    await db.users.update_one({"id": bot_id}, {"$set": {"bot_last_action": datetime.utcnow()}})
    
    return actions_done


async def run_bot_cycle(server_id: str = "default"):
    """Run one cycle of bot actions for all bots on a server."""
    db = await get_db()
    bots = await db.users.find({"is_bot": True, "bot_server": server_id}).to_list(100)
    
    if not bots:
        print(f"No bots found for server {server_id}")
        return
    
    # Pick random subset of bots to act this cycle (not all at once)
    active_count = random.randint(max(1, len(bots) // 4), max(2, len(bots) // 2))
    active_bots = random.sample(bots, min(active_count, len(bots)))
    
    print(f"Bot cycle: {len(active_bots)}/{len(bots)} bots acting on server {server_id}")
    
    for bot in active_bots:
        try:
            actions = await bot_action_cycle(db, bot)
            if actions:
                print(f"  {bot['username']}: {', '.join(actions)}")
        except Exception as e:
            print(f"  Error for {bot['username']}: {e}")
        
        # Small delay between bots
        await asyncio.sleep(random.uniform(0.5, 2.0))


async def initialize_bots(server_id: str = "default", count: int = 20):
    """Initialize bots for a server with balanced tier distribution."""
    db = await get_db()
    
    # Check existing bots
    existing = await db.users.count_documents({"is_bot": True, "bot_server": server_id})
    if existing >= count:
        print(f"Server {server_id} already has {existing} bots")
        return existing
    
    to_create = count - existing
    
    # Distribution: 30% low, 30% medium, 25% medium_high, 15% high
    distribution = {
        "low": int(to_create * 0.30),
        "medium": int(to_create * 0.30),
        "medium_high": int(to_create * 0.25),
        "high": to_create - int(to_create * 0.30) - int(to_create * 0.30) - int(to_create * 0.25),
    }
    
    created = 0
    for tier, num in distribution.items():
        for _ in range(num):
            await create_bot_profile(db, tier, server_id)
            created += 1
    
    # Create a bot guild
    guild_exists = await db.guilds.find_one({"name": f"BotGuild_{server_id}"})
    if not guild_exists:
        guild_id = str(uuid.uuid4())
        bot_users = await db.users.find({"is_bot": True, "bot_server": server_id}).to_list(100)
        member_ids = [b["id"] for b in bot_users[:15]]
        await db.guilds.insert_one({
            "id": guild_id, "name": f"Legion_{random.randint(100,999)}",
            "leader_id": member_ids[0] if member_ids else "", "members": member_ids,
            "level": random.randint(3, 10), "exp": 0, "created_at": datetime.utcnow(),
        })
        for mid in member_ids:
            await db.users.update_one({"id": mid}, {"$set": {"guild_id": guild_id}})
    
    print(f"Initialized {created} bots for server {server_id} (total: {existing + created})")
    return existing + created


if __name__ == "__main__":
    async def main():
        await initialize_bots("default", 20)
        print("\nRunning bot cycle...")
        await run_bot_cycle("default")
    
    asyncio.run(main())
