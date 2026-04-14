"""
Divine Waifus - Multi-Currency System & Soul Forge (Fucina delle Anime)
Inspired by Hokage Crisis: multiple currencies, specialized shops, hero retirement.

CURRENCIES:
- Gold (Oro) - Basic, from battles/events
- Gems (Gemme) - Premium, from gacha/shop
- Honor (Onore) - PvP Arena rewards
- Guild Points (Punti Gilda) - Guild activities
- Prana - Hero retirement (Soul Forge)
- Soul Seals (Sigilli dell'Anima) - Rare hero retirement currency
- Mission Coins (Monete Missione) - Daily quests
- Dimension Fragments (Frammenti Dimensionali) - Raids/events
- Star Dust (Polvere Stellare) - Star fusion byproduct
"""
import random
import uuid
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel

# ===================== CURRENCY DEFINITIONS =====================
CURRENCIES = {
    "gold": {"name": "Oro", "icon": "\U0001F4B0", "color": "#ffd700", "description": "Valuta base. Guadagnata da battaglie, eventi e missioni."},
    "gems": {"name": "Gemme", "icon": "\U0001F48E", "color": "#44ddff", "description": "Valuta premium. Acquistabile o ottenuta da ricompense."},
    "honor": {"name": "Onore", "icon": "\u2694\uFE0F", "color": "#ff4444", "description": "Guadagnato in Arena PvP e GvG. Spendibile nel Negozio Onore."},
    "guild_points": {"name": "Punti Gilda", "icon": "\U0001F3DB\uFE0F", "color": "#6644ff", "description": "Guadagnati da attivita di gilda, territori e GvG."},
    "prana": {"name": "Prana", "icon": "\U0001F4AB", "color": "#44ff88", "description": "Energia vitale degli eroi ritirati. Spendibile nella Fucina delle Anime."},
    "soul_seals": {"name": "Sigilli dell'Anima", "icon": "\U0001F47B", "color": "#9944ff", "description": "Rara essenza da eroi 4*+ ritirati. Per oggetti leggendari."},
    "mission_coins": {"name": "Monete Missione", "icon": "\U0001F3AF", "color": "#ff8844", "description": "Ottenute completando missioni giornaliere e settimanali."},
    "dimension_frags": {"name": "Frammenti Dimensionali", "icon": "\U0001F300", "color": "#ff44ff", "description": "Ottenuti da Raid e eventi speciali. Per il Negozio Dimensionale."},
    "star_dust": {"name": "Polvere Stellare", "icon": "\u2728", "color": "#ffd700", "description": "Residuo delle fusioni stellari. Per il Negozio Stellare."},
}

# ===================== HERO RETIREMENT REWARDS =====================
# Prana and Soul Seals earned by retiring a hero based on stars
RETIREMENT_REWARDS = {
    1: {"prana": 10, "soul_seals": 0, "star_dust": 5},
    2: {"prana": 25, "soul_seals": 0, "star_dust": 10},
    3: {"prana": 60, "soul_seals": 1, "star_dust": 20},
    4: {"prana": 150, "soul_seals": 3, "star_dust": 50},
    5: {"prana": 400, "soul_seals": 8, "star_dust": 120},
    6: {"prana": 1000, "soul_seals": 20, "star_dust": 300},
    7: {"prana": 1500, "soul_seals": 30, "star_dust": 500},
    8: {"prana": 2000, "soul_seals": 40, "star_dust": 700},
    9: {"prana": 2800, "soul_seals": 55, "star_dust": 1000},
    10: {"prana": 4000, "soul_seals": 80, "star_dust": 1500},
    11: {"prana": 5500, "soul_seals": 110, "star_dust": 2000},
    12: {"prana": 7500, "soul_seals": 150, "star_dust": 3000},
    13: {"prana": 10000, "soul_seals": 200, "star_dust": 4000},
    14: {"prana": 15000, "soul_seals": 300, "star_dust": 6000},
    15: {"prana": 25000, "soul_seals": 500, "star_dust": 10000},
}

# Bonus for reincarnated heroes
REINC_BONUS_MULT = 1.5

# ===================== SPECIALIZED SHOP ITEMS =====================
SOUL_FORGE_SHOP = [
    {"id": "sf_gacha_ticket", "name": "Biglietto Evocazione Premium", "icon": "\U0001F3AB", "cost": {"prana": 500}, "reward": {"premium_pull": 1}, "description": "1 pull premium gratuita", "stock": 5},
    {"id": "sf_stella_divina", "name": "Stella Divina", "icon": "\u2B50", "cost": {"prana": 800}, "reward": {"stella_divina": 1}, "description": "Materiale per fusione 9-12\u2B50", "stock": 3},
    {"id": "sf_fragment_gold", "name": "Frammento Dorato x10", "icon": "\U0001F7E1", "cost": {"soul_seals": 50}, "reward": {"gold_fragments": 10}, "description": "10 frammenti dorati per eroe 6\u2B50", "stock": 2},
    {"id": "sf_rune_premium", "name": "Runa Leggendaria", "icon": "\U0001F4A5", "cost": {"soul_seals": 100}, "reward": {"legendary_rune": 1}, "description": "Runa garantita 5-6\u2B50", "stock": 1},
    {"id": "sf_exp_tome", "name": "Tomo EXP Massimo", "icon": "\U0001F4DA", "cost": {"prana": 300}, "reward": {"exp": 5000}, "description": "+5000 EXP a un eroe", "stock": 10},
    {"id": "sf_gold_pack", "name": "Lingotto d'Oro", "icon": "\U0001F4B0", "cost": {"prana": 100}, "reward": {"gold": 100000}, "description": "100.000 Oro", "stock": 20},
    {"id": "sf_cristallo_astrale", "name": "Cristallo Astrale", "icon": "\U0001F48E", "cost": {"soul_seals": 200}, "reward": {"cristallo_astrale": 1}, "description": "Materiale per fusione 12-14\u2B50", "stock": 2},
    {"id": "sf_essenza_trasc", "name": "Essenza Trascendente", "icon": "\U0001F451", "cost": {"soul_seals": 500}, "reward": {"essenza_trascendente": 1}, "description": "Materiale per fusione 15\u2B50", "stock": 1},
    {"id": "sf_reinc_crystal", "name": "Cristallo Reincarnazione", "icon": "\U0001F4AB", "cost": {"soul_seals": 150}, "reward": {"reinc_crystal": 1}, "description": "Per la reincarnazione senza gemme", "stock": 2},
]

HONOR_SHOP = [
    {"id": "hs_gacha_ticket", "name": "Biglietto Evocazione", "icon": "\U0001F3AB", "cost": {"honor": 200}, "reward": {"standard_pull": 1}, "description": "1 pull standard", "stock": 5},
    {"id": "hs_gems_small", "name": "50 Gemme", "icon": "\U0001F48E", "cost": {"honor": 500}, "reward": {"gems": 50}, "description": "50 gemme", "stock": 3},
    {"id": "hs_stamina", "name": "Pozione Stamina", "icon": "\u26A1", "cost": {"honor": 100}, "reward": {"stamina": 50}, "description": "+50 Stamina", "stock": 5},
    {"id": "hs_rune_box", "name": "Scatola Rune", "icon": "\U0001F381", "cost": {"honor": 300}, "reward": {"rune_box": 1}, "description": "Runa casuale 3-5\u2B50", "stock": 3},
    {"id": "hs_pvp_frame", "name": "Cornice Gladiatore", "icon": "\U0001F5E1\uFE0F", "cost": {"honor": 1000}, "reward": {"frame": "gladiator"}, "description": "Cornice esclusiva PvP", "stock": 1},
]

GUILD_SHOP = [
    {"id": "gs_premium_ticket", "name": "Biglietto Premium", "icon": "\U0001F3AB", "cost": {"guild_points": 300}, "reward": {"premium_pull": 1}, "description": "1 pull premium", "stock": 3},
    {"id": "gs_stella_divina", "name": "Stella Divina", "icon": "\u2B50", "cost": {"guild_points": 500}, "reward": {"stella_divina": 1}, "description": "Materiale fusione", "stock": 2},
    {"id": "gs_territory_boost", "name": "Buff Territorio", "icon": "\U0001F3F0", "cost": {"guild_points": 200}, "reward": {"territory_boost": 1}, "description": "+50% ricompense territorio per 24h", "stock": 1},
    {"id": "gs_guild_exp", "name": "EXP Gilda", "icon": "\U0001F4DA", "cost": {"guild_points": 150}, "reward": {"guild_exp": 500}, "description": "+500 EXP Gilda", "stock": 5},
    {"id": "gs_gold_pack", "name": "Forziere d'Oro", "icon": "\U0001F4B0", "cost": {"guild_points": 100}, "reward": {"gold": 50000}, "description": "50.000 Oro", "stock": 10},
]

DIMENSION_SHOP = [
    {"id": "ds_fragment_purple", "name": "Frammento Viola x10", "icon": "\U0001F7E3", "cost": {"dimension_frags": 100}, "reward": {"purple_fragments": 10}, "description": "10 frammenti viola per eroe 4\u2B50", "stock": 5},
    {"id": "ds_fragment_orange", "name": "Frammento Arancio x5", "icon": "\U0001F7E0", "cost": {"dimension_frags": 200}, "reward": {"orange_fragments": 5}, "description": "5 frammenti arancio per eroe 5\u2B50", "stock": 3},
    {"id": "ds_exclusive_mat", "name": "Materiale Esclusivo", "icon": "\U0001F31F", "cost": {"dimension_frags": 500}, "reward": {"exclusive_material": 1}, "description": "Per craftare armi uniche", "stock": 2},
    {"id": "ds_constellation_ticket", "name": "Biglietto Costellazione", "icon": "\u264C", "cost": {"dimension_frags": 800}, "reward": {"constellation_pull": 1}, "description": "1 pull costellazione", "stock": 1},
    {"id": "ds_rune_legendary", "name": "Runa Leggendaria", "icon": "\U0001F4A5", "cost": {"dimension_frags": 1000}, "reward": {"legendary_rune": 1}, "description": "Runa garantita 5-6\u2B50", "stock": 1},
]

STAR_DUST_SHOP = [
    {"id": "sd_gold", "name": "200K Oro", "icon": "\U0001F4B0", "cost": {"star_dust": 50}, "reward": {"gold": 200000}, "description": "200.000 Oro", "stock": 20},
    {"id": "sd_gems", "name": "30 Gemme", "icon": "\U0001F48E", "cost": {"star_dust": 100}, "reward": {"gems": 30}, "description": "30 Gemme", "stock": 5},
    {"id": "sd_stella", "name": "Stella Divina", "icon": "\u2B50", "cost": {"star_dust": 300}, "reward": {"stella_divina": 1}, "description": "Materiale fusione", "stock": 3},
    {"id": "sd_fragment_green", "name": "Frammento Verde x20", "icon": "\U0001F7E2", "cost": {"star_dust": 30}, "reward": {"green_fragments": 20}, "description": "20 frammenti verdi", "stock": 10},
    {"id": "sd_fragment_blue", "name": "Frammento Blu x15", "icon": "\U0001F535", "cost": {"star_dust": 60}, "reward": {"blue_fragments": 15}, "description": "15 frammenti blu", "stock": 5},
    {"id": "sd_stamina_full", "name": "Stamina Completa", "icon": "\u26A1", "cost": {"star_dust": 80}, "reward": {"stamina_full": True}, "description": "Ricarica stamina al 100%", "stock": 3},
]

MISSION_SHOP = [
    {"id": "ms_gold", "name": "50K Oro", "icon": "\U0001F4B0", "cost": {"mission_coins": 20}, "reward": {"gold": 50000}, "description": "50.000 Oro", "stock": 20},
    {"id": "ms_stamina", "name": "Pozione Stamina", "icon": "\u26A1", "cost": {"mission_coins": 15}, "reward": {"stamina": 30}, "description": "+30 Stamina", "stock": 5},
    {"id": "ms_exp_tome", "name": "Tomo EXP", "icon": "\U0001F4DA", "cost": {"mission_coins": 30}, "reward": {"exp": 2000}, "description": "+2000 EXP", "stock": 5},
    {"id": "ms_rune_basic", "name": "Runa Base", "icon": "\U0001F4A5", "cost": {"mission_coins": 50}, "reward": {"rune_basic": 1}, "description": "Runa casuale 1-3\u2B50", "stock": 3},
    {"id": "ms_fragment_green", "name": "Frammento Verde x5", "icon": "\U0001F7E2", "cost": {"mission_coins": 10}, "reward": {"green_fragments": 5}, "description": "5 frammenti verdi", "stock": 10},
]

ALL_SHOPS = {
    "soul_forge": {"name": "Fucina delle Anime", "icon": "\U0001F47B", "color": "#9944ff", "items": SOUL_FORGE_SHOP, "currencies": ["prana", "soul_seals"]},
    "honor": {"name": "Negozio Onore", "icon": "\u2694\uFE0F", "color": "#ff4444", "items": HONOR_SHOP, "currencies": ["honor"]},
    "guild": {"name": "Negozio Gilda", "icon": "\U0001F3DB\uFE0F", "color": "#6644ff", "items": GUILD_SHOP, "currencies": ["guild_points"]},
    "dimension": {"name": "Negozio Dimensionale", "icon": "\U0001F300", "color": "#ff44ff", "items": DIMENSION_SHOP, "currencies": ["dimension_frags"]},
    "star_dust": {"name": "Negozio Stellare", "icon": "\u2728", "color": "#ffd700", "items": STAR_DUST_SHOP, "currencies": ["star_dust"]},
    "mission": {"name": "Negozio Missioni", "icon": "\U0001F3AF", "color": "#ff8844", "items": MISSION_SHOP, "currencies": ["mission_coins"]},
}


def register_soul_forge_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    # ==================== CURRENCY WALLET ====================
    @router.get("/wallet")
    async def get_wallet(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        user = await db.users.find_one({"id": uid})
        wallet = await db.wallets.find_one({"user_id": uid})
        if not wallet:
            wallet = {"user_id": uid, "honor": 0, "guild_points": 0, "prana": 0, "soul_seals": 0, "mission_coins": 0, "dimension_frags": 0, "star_dust": 0}
            await db.wallets.insert_one(wallet)
        return {
            "currencies": {
                "gold": {"amount": user.get("gold", 0), **CURRENCIES["gold"]},
                "gems": {"amount": user.get("gems", 0), **CURRENCIES["gems"]},
                "honor": {"amount": wallet.get("honor", 0), **CURRENCIES["honor"]},
                "guild_points": {"amount": wallet.get("guild_points", 0), **CURRENCIES["guild_points"]},
                "prana": {"amount": wallet.get("prana", 0), **CURRENCIES["prana"]},
                "soul_seals": {"amount": wallet.get("soul_seals", 0), **CURRENCIES["soul_seals"]},
                "mission_coins": {"amount": wallet.get("mission_coins", 0), **CURRENCIES["mission_coins"]},
                "dimension_frags": {"amount": wallet.get("dimension_frags", 0), **CURRENCIES["dimension_frags"]},
                "star_dust": {"amount": wallet.get("star_dust", 0), **CURRENCIES["star_dust"]},
            }
        }

    # ==================== SOUL FORGE - HERO RETIREMENT ====================
    @router.get("/soul-forge")
    async def get_soul_forge(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        wallet = await db.wallets.find_one({"user_id": uid}) or {}
        # Get retirement history
        history = await db.retirement_history.find({"user_id": uid}).sort("retired_at", -1).limit(20).to_list(20)
        return {
            "prana": wallet.get("prana", 0),
            "soul_seals": wallet.get("soul_seals", 0),
            "star_dust": wallet.get("star_dust", 0),
            "reward_table": RETIREMENT_REWARDS,
            "reinc_bonus": f"x{REINC_BONUS_MULT}",
            "history": [serialize_doc(h) for h in history],
            "shop": SOUL_FORGE_SHOP,
        }

    class RetireHeroRequest(BaseModel):
        user_hero_ids: list  # Can retire multiple at once

    @router.post("/soul-forge/retire")
    async def retire_heroes(req: RetireHeroRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        if not req.user_hero_ids:
            raise HTTPException(400, "Seleziona almeno un eroe!")
        total_prana = 0
        total_seals = 0
        total_dust = 0
        retired_names = []
        for uhid in req.user_hero_ids:
            uh = await db.user_heroes.find_one({"id": uhid, "user_id": uid})
            if not uh:
                continue
            hero = await db.heroes.find_one({"id": uh["hero_id"]})
            stars = uh.get("stars", hero.get("rarity", 1) if hero else 1)
            is_reinc = uh.get("is_reincarnated", False)
            # Check not in active team
            team = await db.teams.find_one({"user_id": uid, "is_active": True})
            if team:
                in_team = any(p.get("user_hero_id") == uhid for p in team.get("formation", []))
                if in_team:
                    continue  # Skip heroes in active team
            rewards = RETIREMENT_REWARDS.get(min(stars, 15), RETIREMENT_REWARDS[1])
            mult = REINC_BONUS_MULT if is_reinc else 1.0
            # Level bonus: +1% per level
            level_bonus = 1 + uh.get("level", 1) * 0.01
            prana = int(rewards["prana"] * mult * level_bonus)
            seals = int(rewards["soul_seals"] * mult)
            dust = int(rewards["star_dust"] * mult * level_bonus)
            total_prana += prana
            total_seals += seals
            total_dust += dust
            hero_name = hero.get("name", "?") if hero else "?"
            retired_names.append(f"{hero_name} ({stars}\u2B50)")
            # Log retirement
            await db.retirement_history.insert_one({
                "user_id": uid, "hero_name": hero_name,
                "stars": stars, "level": uh.get("level", 1),
                "prana": prana, "soul_seals": seals, "star_dust": dust,
                "was_reincarnated": is_reinc,
                "retired_at": datetime.utcnow(),
            })
            # Delete hero
            await db.user_heroes.delete_one({"id": uhid, "user_id": uid})
            # Also remove from equipment/runes
            await db.user_equipment.update_many({"equipped_to": uhid}, {"$unset": {"equipped_to": ""}})
            await db.user_runes.update_many({"equipped_to": uhid}, {"$unset": {"equipped_to": "", "equipped_slot": ""}})
        # Award currencies
        if total_prana > 0 or total_seals > 0 or total_dust > 0:
            await db.wallets.update_one(
                {"user_id": uid},
                {"$inc": {"prana": total_prana, "soul_seals": total_seals, "star_dust": total_dust}},
                upsert=True,
            )
        return {
            "success": True,
            "retired_count": len(retired_names),
            "retired_heroes": retired_names,
            "rewards": {"prana": total_prana, "soul_seals": total_seals, "star_dust": total_dust},
        }

    # ==================== ALL SHOPS ====================
    @router.get("/shops")
    async def get_all_shops(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        user = await db.users.find_one({"id": uid})
        wallet = await db.wallets.find_one({"user_id": uid}) or {}
        # Get daily purchase counts
        today = datetime.utcnow().strftime("%Y-%m-%d")
        purchases = await db.shop_purchases_special.find({"user_id": uid, "date": today}).to_list(200)
        purchase_counts = {}
        for p in purchases:
            purchase_counts[p["item_id"]] = purchase_counts.get(p["item_id"], 0) + 1
        balances = {
            "gold": user.get("gold", 0), "gems": user.get("gems", 0),
            "honor": wallet.get("honor", 0), "guild_points": wallet.get("guild_points", 0),
            "prana": wallet.get("prana", 0), "soul_seals": wallet.get("soul_seals", 0),
            "mission_coins": wallet.get("mission_coins", 0), "dimension_frags": wallet.get("dimension_frags", 0),
            "star_dust": wallet.get("star_dust", 0),
        }
        shops = {}
        for shop_id, shop in ALL_SHOPS.items():
            items = []
            for item in shop["items"]:
                bought = purchase_counts.get(item["id"], 0)
                can_afford = all(balances.get(curr, 0) >= amount for curr, amount in item["cost"].items())
                items.append({
                    **item,
                    "purchased_today": bought,
                    "remaining_stock": max(0, item["stock"] - bought),
                    "can_afford": can_afford,
                })
            shops[shop_id] = {**shop, "items": items}
        return {"shops": shops, "balances": balances, "currency_info": CURRENCIES}

    class ShopPurchaseRequest(BaseModel):
        shop_id: str
        item_id: str

    @router.post("/shops/buy")
    async def buy_from_shop(req: ShopPurchaseRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        shop = ALL_SHOPS.get(req.shop_id)
        if not shop:
            raise HTTPException(404, "Negozio non trovato")
        item = next((i for i in shop["items"] if i["id"] == req.item_id), None)
        if not item:
            raise HTTPException(404, "Oggetto non trovato")
        # Check stock
        today = datetime.utcnow().strftime("%Y-%m-%d")
        bought = await db.shop_purchases_special.count_documents({"user_id": uid, "item_id": req.item_id, "date": today})
        if bought >= item["stock"]:
            raise HTTPException(400, "Stock esaurito oggi!")
        # Check and deduct currencies
        user = await db.users.find_one({"id": uid})
        wallet = await db.wallets.find_one({"user_id": uid}) or {}
        for curr, amount in item["cost"].items():
            if curr in ("gold", "gems"):
                if user.get(curr, 0) < amount:
                    raise HTTPException(400, f"{CURRENCIES[curr]['name']} insufficiente! Servono {amount}")
            else:
                if wallet.get(curr, 0) < amount:
                    raise HTTPException(400, f"{CURRENCIES[curr]['name']} insufficiente! Servono {amount}")
        # Deduct costs
        for curr, amount in item["cost"].items():
            if curr in ("gold", "gems"):
                await db.users.update_one({"id": uid}, {"$inc": {curr: -amount}})
            else:
                await db.wallets.update_one({"user_id": uid}, {"$inc": {curr: -amount}})
        # Give rewards
        reward = item["reward"]
        user_inc = {}
        wallet_inc = {}
        for rk, rv in reward.items():
            if rk in ("gold", "gems", "stamina", "experience"):
                user_inc[rk] = rv
            elif rk in ("stella_divina", "cristallo_astrale", "essenza_trascendente"):
                await db.user_materials.update_one({"user_id": uid}, {"$inc": {rk: rv}}, upsert=True)
            elif rk.endswith("_fragments"):
                frag_type = rk.replace("_fragments", "")
                await db.user_fragments.update_one({"user_id": uid}, {"$inc": {frag_type: rv}}, upsert=True)
        if user_inc:
            await db.users.update_one({"id": uid}, {"$inc": user_inc})
        if wallet_inc:
            await db.wallets.update_one({"user_id": uid}, {"$inc": wallet_inc})
        # Record purchase
        await db.shop_purchases_special.insert_one({
            "user_id": uid, "shop_id": req.shop_id, "item_id": req.item_id,
            "date": today, "timestamp": datetime.utcnow(),
        })
        return {"success": True, "item": item["name"], "reward": reward, "cost": item["cost"]}

    # ==================== CURRENCY EARNING HOOKS ====================
    @router.post("/currency/earn-pvp")
    async def earn_pvp_honor(current_user: dict = Depends(get_current_user)):
        """Award honor from PvP (called after PvP battles)."""
        uid = current_user["id"]
        honor = random.randint(15, 40)
        await db.wallets.update_one({"user_id": uid}, {"$inc": {"honor": honor}}, upsert=True)
        return {"honor_earned": honor}

    @router.post("/currency/earn-guild")
    async def earn_guild_points(current_user: dict = Depends(get_current_user)):
        """Award guild points from guild activities."""
        uid = current_user["id"]
        points = random.randint(10, 30)
        await db.wallets.update_one({"user_id": uid}, {"$inc": {"guild_points": points}}, upsert=True)
        return {"guild_points_earned": points}

    @router.post("/currency/earn-mission")
    async def earn_mission_coins(current_user: dict = Depends(get_current_user)):
        """Award mission coins from daily tasks."""
        uid = current_user["id"]
        coins = random.randint(5, 15)
        await db.wallets.update_one({"user_id": uid}, {"$inc": {"mission_coins": coins}}, upsert=True)
        return {"mission_coins_earned": coins}

    @router.post("/currency/earn-dimension")
    async def earn_dimension_frags(current_user: dict = Depends(get_current_user)):
        """Award dimension fragments from raids."""
        uid = current_user["id"]
        frags = random.randint(5, 25)
        await db.wallets.update_one({"user_id": uid}, {"$inc": {"dimension_frags": frags}}, upsert=True)
        return {"dimension_frags_earned": frags}

    # ==================== SOUL FORGE - ESSENCE SYSTEM ====================
    SOUL_ESSENCE_VALUES = {1: 5, 2: 10, 3: 25, 4: 100, 5: 300}
    LEVEL_BONUS_RATE = 0.02  # +2% per livello

    class SoulForgeRequest(BaseModel):
        hero_ids: list

    @router.post("/soul/forge")
    async def soul_forge(req: SoulForgeRequest, current_user: dict = Depends(get_current_user)):
        """Sacrifice heroes to gain soul_essence."""
        uid = current_user["id"]
        if not req.hero_ids:
            raise HTTPException(400, "Seleziona almeno un eroe!")
        # Deduplicate
        unique_ids = list(dict.fromkeys(req.hero_ids))
        total_essence = 0
        for uhid in unique_ids:
            uh = await db.user_heroes.find_one({"id": uhid, "user_id": uid})
            if not uh:
                raise HTTPException(404, f"Eroe {uhid} non trovato o non tuo")
            # Skip heroes in active team
            team = await db.teams.find_one({"user_id": uid, "is_active": True})
            if team and any(p.get("user_hero_id") == uhid for p in team.get("formation", [])):
                raise HTTPException(400, "Non puoi sacrificare un eroe nel team attivo!")
            stars = uh.get("stars", 1)
            level = uh.get("level", 1)
            base_value = SOUL_ESSENCE_VALUES.get(min(stars, 5), 5)
            level_bonus = 1 + (level * LEVEL_BONUS_RATE)
            essence = int(base_value * level_bonus)
            total_essence += essence
            await db.user_heroes.delete_one({"id": uhid, "user_id": uid})
        # Add soul_essence to user
        await db.users.update_one(
            {"id": uid},
            {"$inc": {"soul_essence": total_essence}},
        )
        user = await db.users.find_one({"id": uid})
        return {
            "gained_essence": total_essence,
            "new_balance": user.get("soul_essence", 0),
        }
