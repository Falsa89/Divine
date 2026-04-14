"""
Divine Waifus - Push Notification System
Register tokens and send push notifications for game events.
"""
from datetime import datetime
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import httpx


def register_push_routes(router, db, get_current_user, serialize_doc, calculate_hero_power):

    class RegisterPushRequest(BaseModel):
        push_token: str
        platform: str = "unknown"

    @router.post("/push/register")
    async def register_push_token(req: RegisterPushRequest, current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        await db.push_tokens.update_one(
            {"user_id": uid},
            {"$set": {
                "user_id": uid,
                "token": req.push_token,
                "platform": req.platform,
                "registered_at": datetime.utcnow(),
                "active": True,
            }},
            upsert=True,
        )
        return {"success": True}

    @router.get("/push/status")
    async def get_push_status(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        token_doc = await db.push_tokens.find_one({"user_id": uid})
        return {
            "registered": token_doc is not None and token_doc.get("active", False),
            "platform": token_doc.get("platform", "unknown") if token_doc else None,
        }

    @router.get("/notifications")
    async def get_notifications(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        notifs = await db.notifications.find({"user_id": uid}).sort("created_at", -1).limit(30).to_list(30)
        unread = await db.notifications.count_documents({"user_id": uid, "read": False})
        return {"notifications": [serialize_doc(n) for n in notifs], "unread": unread}

    @router.post("/notifications/read-all")
    async def read_all_notifications(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        await db.notifications.update_many({"user_id": uid, "read": False}, {"$set": {"read": True}})
        return {"success": True}

    # Internal helper to create and optionally push a notification
    async def _create_notification(user_id: str, title: str, body: str, notif_type: str = "info", data: dict = None):
        """Create an in-game notification and optionally send push."""
        notif = {
            "id": f"notif_{datetime.utcnow().timestamp()}",
            "user_id": user_id,
            "title": title,
            "body": body,
            "type": notif_type,
            "data": data or {},
            "read": False,
            "created_at": datetime.utcnow(),
        }
        await db.notifications.insert_one(notif)

        # Try to send push notification
        token_doc = await db.push_tokens.find_one({"user_id": user_id, "active": True})
        if token_doc and token_doc.get("token"):
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        "https://exp.host/--/api/v2/push/send",
                        json={
                            "to": token_doc["token"],
                            "title": title,
                            "body": body,
                            "sound": "default",
                            "data": data or {},
                        },
                        timeout=5,
                    )
            except Exception:
                pass  # Push delivery is best-effort

    # Expose the helper for other modules
    router.create_notification = _create_notification

    # Test endpoint
    @router.post("/push/test")
    async def test_push(current_user: dict = Depends(get_current_user)):
        uid = current_user["id"]
        await _create_notification(
            uid,
            "Test Notifica",
            "Le notifiche push funzionano correttamente!",
            "test",
        )
        return {"success": True, "message": "Notifica di test inviata"}
