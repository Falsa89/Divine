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

    # ==================== PLAZA CHAT — MULTI-CHANNEL (v16.18 Phase 1) ====================
    # Channels supported: global | system | faction | guild
    # Storage: same `db.plaza_chat` collection, distinguished by `channel` field.
    # Backward compat: pre-v16.18 messages without `channel` field are treated as 'global'.
    # System channel is READ-ONLY (POST forbidden) — riservato a notifiche di gioco future.
    # Faction/Guild require user to have respective context, otherwise read returns []
    # and POST raises 403.
    VALID_CHANNELS = {"global", "system", "faction", "guild"}

    class PlazaChatRequest(BaseModel):
        message: str
        channel: str = "global"

    @router.post("/plaza/chat")
    async def plaza_chat(req: PlazaChatRequest, current_user: dict = Depends(get_current_user)):
        ch = req.channel if req.channel in VALID_CHANNELS else "global"
        if ch == "system":
            raise HTTPException(403, "Il canale Sistema è di sola lettura.")
        if len(req.message) > 200:
            raise HTTPException(400, "Messaggio troppo lungo!")
        msg = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "username": current_user.get("username", "???"),
            "message": req.message,
            "timestamp": datetime.utcnow(),
            "channel": ch,
        }
        if ch == "faction":
            f = current_user.get("faction")
            if not f:
                raise HTTPException(403, "Non appartieni a nessuna fazione.")
            msg["faction"] = f
        if ch == "guild":
            g = current_user.get("guild_id")
            if not g:
                raise HTTPException(403, "Non appartieni a nessuna gilda.")
            msg["guild_id"] = g
        await db.plaza_chat.insert_one(msg)
        return {"success": True, "message": serialize_doc(msg)}

    @router.get("/plaza/chat")
    async def get_plaza_chat(channel: str = "global", current_user: dict = Depends(get_current_user)):
        ch = channel if channel in VALID_CHANNELS else "global"
        if ch == "global":
            # backward compat: include legacy messages senza il campo channel
            query: dict = {"$or": [{"channel": "global"}, {"channel": {"$exists": False}}]}
        elif ch == "system":
            query = {"channel": "system"}
        elif ch == "faction":
            f = current_user.get("faction")
            if not f:
                return []
            query = {"channel": "faction", "faction": f}
        elif ch == "guild":
            g = current_user.get("guild_id")
            if not g:
                return []
            query = {"channel": "guild", "guild_id": g}
        else:
            query = {"channel": "global"}
        messages = await db.plaza_chat.find(query).sort("timestamp", -1).limit(30).to_list(30)
        return [serialize_doc(m) for m in reversed(messages)]

    @router.get("/plaza/channels")
    async def get_chat_channels(current_user: dict = Depends(get_current_user)):
        """Phase 1: enumera lo stato dei canali disponibili per l'utente.
        Il frontend usa questa info per: mostrare/disabilitare i tab,
        rendere read-only il composer su 'system', e mostrare locked state
        su faction/guild quando il contesto manca."""
        return {
            "global":  {"available": True,  "readonly": False, "label": "Globale", "context": None},
            "system":  {"available": True,  "readonly": True,  "label": "Sistema", "context": None},
            "faction": {
                "available": bool(current_user.get("faction")),
                "readonly": False,
                "label": "Fazione",
                "context": current_user.get("faction"),
            },
            "guild": {
                "available": bool(current_user.get("guild_id")),
                "readonly": False,
                "label": "Gilda",
                "context": current_user.get("guild_id"),
            },
        }

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

    # ==================== DIRECT MESSAGES (DM) — Phase 2 v16.19 ====================
    # Modello:
    #   db.dm_threads     — 1 doc per coppia di utenti (chiave deterministica
    #                       lex-ordered: smaller user id va in user_a)
    #   db.dm_messages    — 1 doc per messaggio (linked via thread_id)
    # Properties:
    #   - 1-to-1 only (Phase 2). Group chats deferred.
    #   - deterministic thread identity → niente duplicati per coppia
    #   - server-side scoping: ogni endpoint verifica che current_user sia
    #     uno dei due partecipanti del thread
    #   - separato totalmente da plaza_chat: nessun leak tra DM e canali pubblici
    def _dm_pair(uid_a: str, uid_b: str) -> tuple[str, str]:
        """Lex-ordered pair → chiave deterministica."""
        return (uid_a, uid_b) if uid_a < uid_b else (uid_b, uid_a)

    async def _dm_get_or_create_thread(uid: str, peer_uid: str) -> dict:
        """Return existing thread between (uid, peer_uid) or create one."""
        if uid == peer_uid:
            raise HTTPException(400, "Non puoi inviare DM a te stesso")
        a, b = _dm_pair(uid, peer_uid)
        existing = await db.dm_threads.find_one({"user_a": a, "user_b": b})
        if existing:
            return existing
        # Lookup usernames for cache
        u_a = await db.users.find_one({"id": a})
        u_b = await db.users.find_one({"id": b})
        if not u_a or not u_b:
            raise HTTPException(404, "Utente non trovato")
        thread = {
            "id": str(uuid.uuid4()),
            "user_a": a, "user_b": b,
            "user_a_username": u_a.get("username", "?"),
            "user_b_username": u_b.get("username", "?"),
            "last_message": None,
            "last_message_at": None,
            "last_sender_id": None,
            "unread_for_a": 0,
            "unread_for_b": 0,
            "created_at": datetime.utcnow(),
        }
        await db.dm_threads.insert_one(thread)
        return thread

    def _dm_thread_view(t: dict, current_uid: str) -> dict:
        """Render a thread for the current user perspective."""
        is_a = t.get("user_a") == current_uid
        peer_id = t.get("user_b") if is_a else t.get("user_a")
        peer_name = t.get("user_b_username") if is_a else t.get("user_a_username")
        unread = t.get("unread_for_a", 0) if is_a else t.get("unread_for_b", 0)
        return {
            "id": t.get("id"),
            "peer_id": peer_id,
            "peer_username": peer_name,
            "last_message": t.get("last_message"),
            "last_message_at": t.get("last_message_at"),
            "last_sender_id": t.get("last_sender_id"),
            "unread": unread,
        }

    @router.get("/dm/threads")
    async def list_dm_threads(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        cursor = db.dm_threads.find({"$or": [{"user_a": uid}, {"user_b": uid}]}).sort("last_message_at", -1).limit(50)
        threads = await cursor.to_list(50)
        return [_dm_thread_view(t, uid) for t in threads]

    class OpenDMRequest(BaseModel):
        peer_user_id: str

    @router.post("/dm/threads")
    async def open_dm_thread(req: OpenDMRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        # Filtra eventuali peer NPC (il prefix `npc_` non corrisponde a utenti reali)
        if (req.peer_user_id or "").startswith("npc_"):
            raise HTTPException(400, "Non puoi inviare DM a un NPC")
        thread = await _dm_get_or_create_thread(uid, req.peer_user_id)
        # Reset unread for current user (ha appena aperto la conversazione)
        is_a = thread.get("user_a") == uid
        await db.dm_threads.update_one(
            {"id": thread["id"]},
            {"$set": {"unread_for_a" if is_a else "unread_for_b": 0}},
        )
        thread = await db.dm_threads.find_one({"id": thread["id"]})
        return _dm_thread_view(thread, uid)

    @router.get("/dm/threads/{thread_id}/messages")
    async def get_dm_messages(thread_id: str, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        thread = await db.dm_threads.find_one({"id": thread_id})
        if not thread:
            raise HTTPException(404, "Thread non trovato")
        if uid not in (thread.get("user_a"), thread.get("user_b")):
            raise HTTPException(403, "Accesso negato")
        cursor = db.dm_messages.find({"thread_id": thread_id}).sort("timestamp", -1).limit(50)
        messages = await cursor.to_list(50)
        # Reset unread for current user (sta leggendo i messaggi)
        is_a = thread.get("user_a") == uid
        await db.dm_threads.update_one(
            {"id": thread_id},
            {"$set": {"unread_for_a" if is_a else "unread_for_b": 0}},
        )
        return [serialize_doc(m) for m in reversed(messages)]

    class DMSendRequest(BaseModel):
        message: str

    @router.post("/dm/threads/{thread_id}/messages")
    async def send_dm_message(thread_id: str, req: DMSendRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        if len(req.message or "") > 500:
            raise HTTPException(400, "Messaggio troppo lungo")
        if not (req.message or "").strip():
            raise HTTPException(400, "Messaggio vuoto")
        thread = await db.dm_threads.find_one({"id": thread_id})
        if not thread:
            raise HTTPException(404, "Thread non trovato")
        if uid not in (thread.get("user_a"), thread.get("user_b")):
            raise HTTPException(403, "Accesso negato")
        msg = {
            "id": str(uuid.uuid4()),
            "thread_id": thread_id,
            "sender_id": uid,
            "sender_username": current_user.get("username", "?"),
            "message": req.message,
            "timestamp": datetime.utcnow(),
        }
        await db.dm_messages.insert_one(msg)
        # Bump thread last_message + incrementa unread per il destinatario
        is_a = thread.get("user_a") == uid
        peer_unread_field = "unread_for_b" if is_a else "unread_for_a"
        await db.dm_threads.update_one(
            {"id": thread_id},
            {
                "$set": {
                    "last_message": req.message[:120],
                    "last_message_at": msg["timestamp"],
                    "last_sender_id": uid,
                },
                "$inc": {peer_unread_field: 1},
            },
        )
        return {"success": True, "message": serialize_doc(msg)}

    @router.post("/dm/threads/{thread_id}/read")
    async def mark_dm_read(thread_id: str, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        thread = await db.dm_threads.find_one({"id": thread_id})
        if not thread:
            raise HTTPException(404, "Thread non trovato")
        if uid not in (thread.get("user_a"), thread.get("user_b")):
            raise HTTPException(403, "Accesso negato")
        is_a = thread.get("user_a") == uid
        await db.dm_threads.update_one(
            {"id": thread_id},
            {"$set": {"unread_for_a" if is_a else "unread_for_b": 0}},
        )
        return {"success": True}
