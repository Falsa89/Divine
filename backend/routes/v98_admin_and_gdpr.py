"""
v98 — Server Actors Admin Runtime Controls (read-only status).

Pack: MEGA_RELEASE_ACCELERATION_47_v98.

Endpoint:
- GET /api/admin/server-actors/status   (read-only, no mutation, env-gated)

Safety:
- NO mass creation of bots runtime
- NO mutation (read-only status)
- Kill switches read from env vars
- Default: all bot features OFF unless explicit env enable
"""
import os
from fastapi import APIRouter

router = APIRouter(prefix="/api/admin", tags=["v98_server_actors_admin"])

DISABLE_ALL_BOTS = os.getenv("V98_BOTS_DISABLE_ALL", "true").lower() == "true"
DISABLE_BOT_CHAT = os.getenv("V98_BOTS_DISABLE_CHAT", "true").lower() == "true"
DISABLE_BOT_LIVE_FILL = os.getenv("V98_BOTS_DISABLE_LIVE_FILL", "true").lower() == "true"
DISABLE_BOT_RANKING_VIS = os.getenv("V98_BOTS_DISABLE_RANKING_VISIBILITY", "true").lower() == "true"
BOT_POWER_PERCENTILE_CAP = int(os.getenv("V98_BOTS_POWER_PERCENTILE_CAP", "90"))
BOT_LOW_POP_FILL_ENABLED = os.getenv("V98_BOTS_LOW_POP_FILL_ENABLED", "false").lower() == "true"
RUNTIME_PERSISTENCE_GATED = os.getenv("V98_SERVER_ACTORS_RUNTIME_ENABLED", "false").lower() == "true"


@router.get("/server-actors/status")
def server_actors_status():
    """Read-only status: nessuna creazione di bot runtime, nessuna mutazione."""
    return {
        "v98_server_actors": True,
        "runtime_persistence_enabled": RUNTIME_PERSISTENCE_GATED,
        "kill_switches": {
            "DISABLE_ALL_BOTS": DISABLE_ALL_BOTS,
            "DISABLE_BOT_CHAT": DISABLE_BOT_CHAT,
            "DISABLE_BOT_LIVE_EVENT_FILL": DISABLE_BOT_LIVE_FILL,
            "DISABLE_BOT_RANKING_VISIBILITY": DISABLE_BOT_RANKING_VIS,
            "BOT_LOW_POP_FILL_ENABLED": BOT_LOW_POP_FILL_ENABLED,
            "BOT_POWER_PERCENTILE_CAP": BOT_POWER_PERCENTILE_CAP,
        },
        "default_state": "ALL_BOT_FEATURES_OFF_BY_DEFAULT",
        "mass_creation_protection": True,
        "mutation_allowed": False,
        "no_fake_users_presented_as_real": True,
        "safety": {
            "db_writes": 0,
            "reward_live": False,
            "production_broadcast": False,
        },
    }


# Data export endpoint (GDPR Track G)
auth_extra_router = APIRouter(prefix="/api/auth", tags=["v98_gdpr"])


def create_auth_extra_router(db, get_current_user):
    @auth_extra_router.get("/data-export")
    async def data_export(current_user: dict = Depends(get_current_user)):
        """GDPR data portability: ritorna i dati account in formato JSON safe.

        Esclude provider_user_id_hash (hashato), refresh_token_hash, password_hash.
        """
        user = await db.users.find_one({"id": current_user["id"]})
        if not user:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="user_not_found")
        # Alias-safe export
        export = {
            "account_id": user.get("account_id") or user.get("id"),
            "alias": user.get("alias"),
            "username": user.get("username"),
            "provider": user.get("provider"),
            "level": user.get("level"),
            "experience": user.get("experience"),
            "gold": user.get("gold"),
            "gems": user.get("gems"),
            "stamina": user.get("stamina"),
            "team_formation": user.get("team_formation") or [],
            "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
            "last_login": user.get("last_login").isoformat() if user.get("last_login") else None,
            "pending_deletion": bool(user.get("pending_deletion", False)),
        }
        return {
            "v98_gdpr": True,
            "data_export_format": "json",
            "data": export,
            "fields_excluded_for_security": [
                "provider_user_id_hash",
                "password_hash",
                "refresh_token_hash",
                "internal_db_id",
            ],
            "retention_policy_days": 365,
        }

    @auth_extra_router.post("/hard-delete-confirm")
    async def hard_delete_confirm(current_user: dict = Depends(get_current_user)):
        """Hard delete: gated da env V98_HARD_DELETE_RUNTIME_ENABLED.

        Default OFF: ritorna `runtime_disabled` per commercial review.
        Se enabled: rimuove user doc + refresh_tokens (irreversibile).
        """
        enabled = os.getenv("V98_HARD_DELETE_RUNTIME_ENABLED", "false").lower() == "true"
        if not enabled:
            return {
                "v98_gdpr": True,
                "hard_delete_runtime": "DISABLED_PENDING_COMMERCIAL_REVIEW",
                "soft_delete_active": bool(current_user.get("pending_deletion", False)),
                "scheduled_deletion_at": current_user.get("scheduled_deletion_at").isoformat() if current_user.get("scheduled_deletion_at") else None,
                "instructions": "Hard delete runtime gated. Enable via V98_HARD_DELETE_RUNTIME_ENABLED=true with audit trail.",
            }
        # Runtime gated path (per future enable)
        await db.refresh_tokens.delete_many({"user_id": current_user["id"]})
        await db.users.delete_one({"id": current_user["id"]})
        return {"v98_gdpr": True, "hard_delete_runtime": "EXECUTED", "irreversible": True}

    return auth_extra_router


# Need to import Depends at top
from fastapi import Depends  # noqa: E402
