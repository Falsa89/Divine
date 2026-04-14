"""
Divine Waifus - Social Routes (Plaza Chat + Friends)
"""
import random
import uuid
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel


def register_social_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    # ==================== PLAZA (Community Square) ====================
    @router.get("/plaza")
    async def get_plaza(current_user: dict = Depends(get_current_user)):
        real_players = await db.users.find({}).sort("created_at", -1).limit(10).to_list(10)
        players = []
        for p in real_players:
            cosmetics = await db.user_cosmetics.find_one({"user_id": p["id"]})
            players.append({
                "id": p["id"],
                "username": p.get("username", "???"),
                "level": p.get("level", 1),
                "title": p.get("active_title", "Novizio"),
                "aura": cosmetics.get("active_aura") if cosmetics else None,
                "frame": cosmetics.get("active_frame", "bronze") if cosmetics else "bronze",
                "faction": p.get("faction"),
                "x": random.randint(50, 750),
                "y": random.randint(50, 350),
                "is_you": p["id"] == current_user["id"],
            })
        npc_names = ["Mercante Misterioso", "Saggio dell'Olimpo", "Guardiano del Tempio", "Artigiano Divino", "Oracolo"]
        for i, name in enumerate(npc_names):
            players.append({
                "id": f"npc_{i}", "username": name, "level": 99,
                "title": "NPC", "aura": "divine", "frame": "legendary",
                "faction": None, "x": 100 + i * 150, "y": 200, "is_you": False, "is_npc": True,
            })
        return {"players": players}

    class PlazaChatRequest(BaseModel):
        message: str

    @router.post("/plaza/chat")
    async def plaza_chat(req: PlazaChatRequest, current_user: dict = Depends(get_current_user)):
        if len(req.message) > 200:
            raise HTTPException(400, "Messaggio troppo lungo!")
        msg = {
            "id": str(uuid.uuid4()), "user_id": current_user["id"],
            "username": current_user.get("username", "???"), "message": req.message,
            "timestamp": datetime.utcnow(),
        }
        await db.plaza_chat.insert_one(msg)
        return {"success": True, "message": serialize_doc(msg)}

    @router.get("/plaza/chat")
    async def get_plaza_chat(current_user: dict = Depends(get_current_user)):
        messages = await db.plaza_chat.find({}).sort("timestamp", -1).limit(30).to_list(30)
        return [serialize_doc(m) for m in reversed(messages)]

    # ==================== FRIENDS SYSTEM ====================
    @router.get("/friends")
    async def get_friends(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        friend_data = await db.friends.find_one({"user_id": uid})
        if not friend_data:
            friend_data = {"user_id": uid, "friends": [], "requests_in": [], "requests_out": []}
            await db.friends.insert_one(friend_data)
        friends = []
        for fid in friend_data.get("friends", []):
            u = await db.users.find_one({"id": fid})
            if u:
                team = await db.teams.find_one({"user_id": fid, "is_active": True})
                friends.append({
                    "id": fid, "username": u.get("username", "?"), "level": u.get("level", 1),
                    "title": u.get("active_title", ""), "faction": u.get("faction"),
                    "power": team.get("total_power", 0) if team else 0,
                    "is_online": (datetime.utcnow() - (u.get("bot_last_action") or u.get("created_at") or datetime.utcnow())).seconds < 600,
                })
        requests_in = []
        for rid in friend_data.get("requests_in", []):
            u = await db.users.find_one({"id": rid})
            if u:
                requests_in.append({"id": rid, "username": u.get("username", "?"), "level": u.get("level", 1)})
        return {"friends": friends, "requests_in": requests_in, "requests_out": friend_data.get("requests_out", []), "max_friends": 30}

    class FriendRequest(BaseModel):
        target_username: str

    @router.post("/friends/request")
    async def send_friend_request(req: FriendRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        target = await db.users.find_one({"username": req.target_username})
        if not target:
            raise HTTPException(404, "Giocatore non trovato")
        if target["id"] == uid:
            raise HTTPException(400, "Non puoi aggiungerti!")
        my_data = await db.friends.find_one({"user_id": uid})
        if my_data and target["id"] in my_data.get("friends", []):
            raise HTTPException(400, "Gia amici!")
        if my_data and target["id"] in my_data.get("requests_out", []):
            raise HTTPException(400, "Richiesta gia inviata!")
        await db.friends.update_one({"user_id": uid}, {"$push": {"requests_out": target["id"]}}, upsert=True)
        await db.friends.update_one({"user_id": target["id"]}, {"$push": {"requests_in": uid}}, upsert=True)
        return {"success": True, "target": req.target_username}

    class AcceptFriendRequest(BaseModel):
        requester_id: str

    @router.post("/friends/accept")
    async def accept_friend(req: AcceptFriendRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        await db.friends.update_one({"user_id": uid}, {"$pull": {"requests_in": req.requester_id}, "$push": {"friends": req.requester_id}})
        await db.friends.update_one({"user_id": req.requester_id}, {"$pull": {"requests_out": uid}, "$push": {"friends": uid}})
        return {"success": True}

    @router.post("/friends/remove/{friend_id}")
    async def remove_friend(friend_id: str, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        await db.friends.update_one({"user_id": uid}, {"$pull": {"friends": friend_id}})
        await db.friends.update_one({"user_id": friend_id}, {"$pull": {"friends": uid}})
        return {"success": True}

    @router.post("/friends/gift/{friend_id}")
    async def gift_friend(friend_id: str, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        user = await db.users.find_one({"id": uid})
        if user.get("gold", 0) < 1000:
            raise HTTPException(400, "Servono almeno 1000 oro!")
        today = datetime.utcnow().strftime("%Y-%m-%d")
        already = await db.friend_gifts.find_one({"from_id": uid, "to_id": friend_id, "date": today})
        if already:
            raise HTTPException(400, "Gia regalato oggi!")
        await db.users.update_one({"id": uid}, {"$inc": {"gold": -1000}})
        await db.users.update_one({"id": friend_id}, {"$inc": {"gold": 1000, "gems": 5}})
        await db.friend_gifts.insert_one({"from_id": uid, "to_id": friend_id, "date": today})
        target = await db.users.find_one({"id": friend_id})
        await db.user_mail.insert_one({
            "id": str(uuid.uuid4()), "user_id": friend_id,
            "subject": f"Regalo da {user.get('username', '?')}",
            "body": f"{user.get('username')} ti ha inviato un regalo!",
            "rewards": {"gold": 1000, "gems": 5}, "claimed": True,
            "timestamp": datetime.utcnow(),
        })
        return {"success": True, "recipient": target.get("username", "?")}
