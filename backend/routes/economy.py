"""
Divine Waifus - Economy Routes (Shop, Mail, Battle Pass, VIP, Multi-Server)
"""
import random
import uuid
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from .game_data import SHOP_ITEMS, DAILY_FREE, BATTLE_PASS_REWARDS, SERVERS, VIP_LEVELS


def register_economy_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    # ==================== SHOP / NEGOZIO ====================
    @router.get("/shop")
    async def get_shop(current_user: dict = Depends(get_current_user)):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        claimed = await db.daily_claims.find({"user_id": current_user["id"], "date": today}).to_list(10)
        claimed_ids = [c["item_id"] for c in claimed]
        purchases = await db.shop_purchases.find({"user_id": current_user["id"], "date": today}).to_list(50)
        purchase_counts = {}
        for p in purchases:
            purchase_counts[p["item_id"]] = purchase_counts.get(p["item_id"], 0) + 1
        return {
            "items": SHOP_ITEMS,
            "daily_free": [{"claimed": d["id"] in claimed_ids, **d} for d in DAILY_FREE],
            "purchase_counts": purchase_counts,
            "date": today,
        }

    class ShopBuyRequest(BaseModel):
        item_id: str

    @router.post("/shop/buy")
    async def shop_buy(req: ShopBuyRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        item = next((i for i in SHOP_ITEMS if i["id"] == req.item_id), None)
        if not item:
            raise HTTPException(404, "Oggetto non trovato")
        user = await db.users.find_one({"id": uid})
        currency = item["price_type"]
        if user.get(currency, 0) < item["price"]:
            raise HTTPException(400, f"{'Gemme' if currency == 'gems' else 'Oro'} insufficiente!")
        await db.users.update_one({"id": uid}, {"$inc": {currency: -item["price"]}})
        reward = item["reward"]
        inc = {}
        if "gems" in reward: inc["gems"] = reward["gems"]
        if "gold" in reward: inc["gold"] = reward["gold"]
        if "stamina" in reward: inc["stamina"] = reward["stamina"]
        if reward.get("stamina_full"):
            await db.users.update_one({"id": uid}, {"$set": {"stamina": user.get("max_stamina", 100)}})
        if inc:
            await db.users.update_one({"id": uid}, {"$inc": inc})
        today = datetime.utcnow().strftime("%Y-%m-%d")
        await db.shop_purchases.insert_one({"user_id": uid, "item_id": req.item_id, "date": today, "timestamp": datetime.utcnow()})
        return {"success": True, "item": item["name"], "reward": reward}

    @router.post("/shop/claim-daily/{item_id}")
    async def claim_daily(item_id: str, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        item = next((d for d in DAILY_FREE if d["id"] == item_id), None)
        if not item:
            raise HTTPException(404, "Non trovato")
        today = datetime.utcnow().strftime("%Y-%m-%d")
        already = await db.daily_claims.find_one({"user_id": uid, "item_id": item_id, "date": today})
        if already:
            raise HTTPException(400, "Gia riscosso oggi!")
        inc = {}
        if "gold" in item["reward"]: inc["gold"] = item["reward"]["gold"]
        if "stamina" in item["reward"]: inc["stamina"] = item["reward"]["stamina"]
        if inc:
            await db.users.update_one({"id": uid}, {"$inc": inc})
        await db.daily_claims.insert_one({"user_id": uid, "item_id": item_id, "date": today, "timestamp": datetime.utcnow()})
        return {"success": True, "reward": item["reward"]}

    # ==================== MAIL / POSTA IN-GAME ====================
    @router.get("/mail")
    async def get_mail(current_user: dict = Depends(get_current_user)):
        mails = await db.user_mail.find({"user_id": current_user["id"]}).sort("timestamp", -1).limit(50).to_list(50)
        return [serialize_doc(m) for m in mails]

    @router.post("/mail/claim/{mail_id}")
    async def claim_mail(mail_id: str, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        mail = await db.user_mail.find_one({"id": mail_id, "user_id": uid})
        if not mail:
            raise HTTPException(404, "Mail non trovata")
        if mail.get("claimed"):
            raise HTTPException(400, "Gia riscosso!")
        rewards = mail.get("rewards", {})
        inc = {}
        if "gold" in rewards: inc["gold"] = rewards["gold"]
        if "gems" in rewards: inc["gems"] = rewards["gems"]
        if "stamina" in rewards: inc["stamina"] = rewards["stamina"]
        if inc:
            await db.users.update_one({"id": uid}, {"$inc": inc})
        await db.user_mail.update_one({"id": mail_id}, {"$set": {"claimed": True}})
        return {"success": True, "rewards": rewards}

    # ==================== BATTLE PASS / STAGIONALE ====================
    @router.get("/battlepass")
    async def get_battle_pass(current_user: dict = Depends(get_current_user)):
        bp = await db.battle_pass.find_one({"user_id": current_user["id"]})
        if not bp:
            bp = {"user_id": current_user["id"], "exp": 0, "level": 1, "is_premium": False, "claimed_free": [], "claimed_premium": [], "season": 1}
            await db.battle_pass.insert_one(bp)
        return {
            "rewards": BATTLE_PASS_REWARDS,
            "current_level": bp.get("level", 1),
            "current_exp": bp.get("exp", 0),
            "exp_to_next": bp.get("level", 1) * 500,
            "is_premium": bp.get("is_premium", False),
            "claimed_free": bp.get("claimed_free", []),
            "claimed_premium": bp.get("claimed_premium", []),
            "season": bp.get("season", 1),
        }

    @router.post("/battlepass/claim/{level}")
    async def claim_bp_reward(level: int, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        bp = await db.battle_pass.find_one({"user_id": uid})
        if not bp:
            raise HTTPException(400, "Battle Pass non inizializzato")
        if level > bp.get("level", 1):
            raise HTTPException(400, "Non hai raggiunto questo livello!")
        reward_entry = next((r for r in BATTLE_PASS_REWARDS if r["level"] == level), None)
        if not reward_entry:
            raise HTTPException(404, "Livello non trovato")
        claimed_free = bp.get("claimed_free", [])
        claimed_premium = bp.get("claimed_premium", [])
        rewards_given = {}
        if level not in claimed_free:
            inc = {}
            for k, v in reward_entry["free"].items():
                inc[k] = v
                rewards_given[f"free_{k}"] = v
            if inc: await db.users.update_one({"id": uid}, {"$inc": inc})
            claimed_free.append(level)
        if bp.get("is_premium") and level not in claimed_premium:
            inc = {}
            for k, v in reward_entry["premium"].items():
                inc[k] = v
                rewards_given[f"premium_{k}"] = v
            if inc: await db.users.update_one({"id": uid}, {"$inc": inc})
            claimed_premium.append(level)
        await db.battle_pass.update_one({"user_id": uid}, {"$set": {"claimed_free": claimed_free, "claimed_premium": claimed_premium}})
        return {"success": True, "rewards": rewards_given}

    @router.post("/battlepass/buy-premium")
    async def buy_premium_pass(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        user = await db.users.find_one({"id": uid})
        cost = 500
        if user.get("gems", 0) < cost:
            raise HTTPException(400, f"Servono {cost} gemme!")
        await db.users.update_one({"id": uid}, {"$inc": {"gems": -cost}})
        await db.battle_pass.update_one({"user_id": uid}, {"$set": {"is_premium": True}}, upsert=True)
        return {"success": True}

    @router.post("/battlepass/add-exp")
    async def add_bp_exp(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        bp = await db.battle_pass.find_one({"user_id": uid})
        if not bp:
            bp = {"user_id": uid, "exp": 0, "level": 1, "is_premium": False, "claimed_free": [], "claimed_premium": [], "season": 1}
            await db.battle_pass.insert_one(bp)
        exp_gain = random.randint(50, 150)
        new_exp = bp.get("exp", 0) + exp_gain
        new_level = bp.get("level", 1)
        while new_exp >= new_level * 500 and new_level < 15:
            new_exp -= new_level * 500
            new_level += 1
        await db.battle_pass.update_one({"user_id": uid}, {"$set": {"exp": new_exp, "level": new_level}})
        return {"exp_gained": exp_gain, "new_exp": new_exp, "new_level": new_level, "leveled_up": new_level > bp.get("level", 1)}

    # ==================== MULTI-SERVER SYSTEM ====================
    @router.get("/servers")
    async def get_servers():
        result = []
        for srv in SERVERS:
            count = await db.users.count_documents({"server": srv["id"]})
            bot_count = await db.users.count_documents({"server": srv["id"], "is_bot": True})
            result.append({
                **srv,
                "players_online": count,
                "real_players": count - bot_count,
                "bots": bot_count,
                "load_percent": int((count / srv["max_players"]) * 100),
            })
        return result

    class SelectServerRequest(BaseModel):
        server_id: str

    @router.post("/server/select")
    async def select_server(req: SelectServerRequest, current_user: dict = Depends(get_current_user)):
        srv = next((s for s in SERVERS if s["id"] == req.server_id), None)
        if not srv:
            raise HTTPException(404, "Server non trovato")
        if srv["status"] == "maintenance":
            raise HTTPException(400, "Server in manutenzione!")
        count = await db.users.count_documents({"server": req.server_id})
        if count >= srv["max_players"]:
            raise HTTPException(400, "Server pieno!")
        await db.users.update_one({"id": current_user["id"]}, {"$set": {"server": req.server_id}})
        return {"success": True, "server": srv}

    # ==================== VIP SYSTEM ====================
    @router.get("/vip")
    async def get_vip_status(current_user: dict = Depends(get_current_user)):
        vip_data = await db.vip_data.find_one({"user_id": current_user["id"]})
        if not vip_data:
            vip_data = {"user_id": current_user["id"], "total_spend": 0, "vip_level": 0, "last_daily_claim": None}
            await db.vip_data.insert_one(vip_data)
        current_lvl = 0
        for vl in VIP_LEVELS:
            if vip_data.get("total_spend", 0) >= vl["min_spend"]:
                current_lvl = vl["level"]
        current_vip = VIP_LEVELS[current_lvl]
        next_vip = VIP_LEVELS[current_lvl + 1] if current_lvl < 5 else None
        return {
            "vip_level": current_lvl,
            "vip_name": current_vip["name"],
            "vip_color": current_vip["color"],
            "perks": current_vip["perks"],
            "total_spend": vip_data.get("total_spend", 0),
            "next_level": next_vip,
            "spend_to_next": next_vip["min_spend"] - vip_data.get("total_spend", 0) if next_vip else 0,
            "all_levels": VIP_LEVELS,
            "can_claim_daily": _can_claim_vip_daily(vip_data),
        }

    def _can_claim_vip_daily(vip_data: dict) -> bool:
        last = vip_data.get("last_daily_claim")
        if not last:
            return True
        if isinstance(last, str):
            return True
        return (datetime.utcnow() - last).days >= 1

    @router.post("/vip/claim-daily")
    async def claim_vip_daily(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        vip_data = await db.vip_data.find_one({"user_id": uid})
        if not vip_data or vip_data.get("vip_level", 0) == 0:
            vip_level = 0
            for vl in VIP_LEVELS:
                if (vip_data or {}).get("total_spend", 0) >= vl["min_spend"]:
                    vip_level = vl["level"]
            if vip_level == 0:
                raise HTTPException(400, "Devi essere almeno VIP 1!")
        if not _can_claim_vip_daily(vip_data or {}):
            raise HTTPException(400, "Gia riscosso oggi!")
        vip_level = 0
        for vl in VIP_LEVELS:
            if (vip_data or {}).get("total_spend", 0) >= vl["min_spend"]:
                vip_level = vl["level"]
        perks = VIP_LEVELS[vip_level]["perks"]
        daily_gems = perks.get("daily_gems", 0)
        if daily_gems > 0:
            await db.users.update_one({"id": uid}, {"$inc": {"gems": daily_gems}})
        await db.vip_data.update_one({"user_id": uid}, {"$set": {"last_daily_claim": datetime.utcnow()}}, upsert=True)
        return {"success": True, "gems_received": daily_gems}

    @router.post("/vip/add-spend")
    async def add_vip_spend(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        amount = 100
        await db.vip_data.update_one({"user_id": uid}, {"$inc": {"total_spend": amount}}, upsert=True)
        vip_data = await db.vip_data.find_one({"user_id": uid})
        new_level = 0
        for vl in VIP_LEVELS:
            if vip_data.get("total_spend", 0) >= vl["min_spend"]:
                new_level = vl["level"]
        return {"total_spend": vip_data.get("total_spend", 0), "vip_level": new_level}
