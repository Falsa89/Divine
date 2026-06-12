"""Pack 108 — Guild Server-Scope Retrofit (read/preview strict).

Questo modulo introduce gli endpoint Guild *server-scoped* read-only che il
client Alpha può invocare in sicurezza. Tutte le scritture mutanti
rimangono *deferred* in quarantena (vedere `routes/guild.py` Pack 108
quarantine guard + blocker `GUILD_LEGACY_QUARANTINED`).

Endpoint registrati su prefix `/api/guild/strict`:

  * GET  /api/guild/strict/health                  (pubblico)
  * POST /api/guild/strict/preflight                (test-only marker)
  * GET  /api/guild/strict/status?server_id=...     (test-only marker)
  * GET  /api/guild/strict/search?server_id=...     (test-only marker)
  * POST /api/guild/strict/membership/preview        (test-only marker, NO write)

Pack 108 è un layer di **retrofit server-scope READ/PREVIEW**.
Non implementa reward live, non muta `users.*`, non crea né modifica
`db.guilds`. Il path canonico per la futura runtime live richiederà
un pack di autorizzazione esplicito (`AUTORIZZO_V110_GUILD_LIVE_PACK_NEXT`).

Blocker canonici:
  * GUILD_SERVER_SCOPE_REQUIRED
  * GUILD_LEGACY_QUARANTINED
  * GUILD_MEMBERSHIP_SERVER_SCOPE_REQUIRED
  * GUILD_CHAT_SERVER_SCOPE_DEFERRED
  * GUILD_WAR_SERVER_SCOPE_DEFERRED
  * GUILD_REWARD_LIVE_DISABLED

Kill switches (tutti default OFF):
  * GUILD_STRICT_PREFLIGHT_ENABLED
  * GUILD_STRICT_MEMBERSHIP_READ_ENABLED
  * GUILD_STRICT_SEARCH_READ_ENABLED
  * GUILD_REWARD_LIVE_ENABLED  (preservato da Pack 107)
  * GUILD_LEGACY_QUARANTINED   (default TRUE: legacy bloccato)
"""
import os
from typing import Any, Dict, Optional, List
from fastapi import HTTPException, Depends

PACK_108_USER_TEST_MARKER = "pack_108_test_artifact"

# Set canonico di blocker Pack 108 (immutabile).
GUILD_STRICT_CANONICAL_BLOCKERS = (
    "GUILD_SERVER_SCOPE_REQUIRED",
    "GUILD_LEGACY_QUARANTINED",
    "GUILD_MEMBERSHIP_SERVER_SCOPE_REQUIRED",
    "GUILD_CHAT_SERVER_SCOPE_DEFERRED",
    "GUILD_WAR_SERVER_SCOPE_DEFERRED",
    "GUILD_REWARD_LIVE_DISABLED",
)


def _truthy(v: Optional[str]) -> bool:
    return str(v or "false").strip().lower() in ("true", "1", "yes", "on")


def _flag_preflight() -> bool: return _truthy(os.getenv("GUILD_STRICT_PREFLIGHT_ENABLED"))
def _flag_membership_read() -> bool: return _truthy(os.getenv("GUILD_STRICT_MEMBERSHIP_READ_ENABLED"))
def _flag_search_read() -> bool: return _truthy(os.getenv("GUILD_STRICT_SEARCH_READ_ENABLED"))
def _flag_guild_reward_live() -> bool: return _truthy(os.getenv("GUILD_REWARD_LIVE_ENABLED"))
def _flag_legacy_quarantined() -> bool:
    # Default TRUE: i path legacy mutanti restano bloccati salvo override esplicito.
    return _truthy(os.getenv("GUILD_LEGACY_QUARANTINED", "true"))


async def _require_pack_108_test_user(db, uid: str) -> dict:
    user_doc = await db.users.find_one({"id": uid})
    if not user_doc or not user_doc.get(PACK_108_USER_TEST_MARKER):
        raise HTTPException(403, detail={
            "blocker": "GUILD_STRICT_ENDPOINT_TEST_ONLY",
            "marker_required": PACK_108_USER_TEST_MARKER,
            "server_scope_required": True,
        })
    return user_doc


def _validate_server_id(sid: Optional[str]) -> str:
    if not sid or not isinstance(sid, str) or not sid.strip():
        raise HTTPException(400, detail={
            "blocker": "SERVER_ID_REQUIRED",
            "guild_server_scope_required": True,
            "no_silent_fallback_to_s1": True,
        })
    sid = sid.strip()
    # No silent fallback a s1; se viene esplicitamente passato 's1' è ok,
    # ma il sistema NON deve mai inferirlo da solo.
    return sid


def register_guild_strict_routes(router, db, get_current_user, *_a, **_kw):

    @router.get("/guild/strict/health")
    async def gs_health():
        return {
            "endpoint_group": "/api/guild/strict",
            "pack_origin": "pack_108",
            "pack_108_test_marker": PACK_108_USER_TEST_MARKER,
            "kill_switches": {
                "GUILD_STRICT_PREFLIGHT_ENABLED": _flag_preflight(),
                "GUILD_STRICT_MEMBERSHIP_READ_ENABLED": _flag_membership_read(),
                "GUILD_STRICT_SEARCH_READ_ENABLED": _flag_search_read(),
                "GUILD_REWARD_LIVE_ENABLED": _flag_guild_reward_live(),
                "GUILD_LEGACY_QUARANTINED": _flag_legacy_quarantined(),
            },
            "surface": "guild_strict_read_preview",
            "status_default": "READY_GATED_DEFERRED",
            "blockers_canonical": list(GUILD_STRICT_CANONICAL_BLOCKERS),
            "reward_live_general": False,
            "guild_reward_live_grant": False,
            "premium_grants": False,
            "release_readiness_claimed": False,
            "no_users_gold_gems_experience_mutation": True,
            "no_cross_server_guild_leak": True,
            "legacy_route_quarantined_default": True,
            "deferred_next_step": "AUTORIZZO_V110_GUILD_LIVE_PACK_NEXT",
            "_slc_pack_108_guild_strict_health": True,
        }

    @router.post("/guild/strict/preflight")
    async def gs_preflight(
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        await _require_pack_108_test_user(db, uid)
        sid = _validate_server_id(server_id)
        if not _flag_preflight():
            return {
                "surface": "guild_strict",
                "server_id": sid,
                "status": "READY_GATED_PREFLIGHT_DISABLED",
                "active_blockers": list(GUILD_STRICT_CANONICAL_BLOCKERS),
                "kill_switch_state": False,
                "deferred_next_step": "AUTORIZZO_V110_GUILD_LIVE_PACK_NEXT",
                "_slc_pack_108_guild_strict_preflight": True,
            }
        return {
            "surface": "guild_strict",
            "server_id": sid,
            "status": "READY_GATED_REWARDS_DEFERRED",
            "active_blockers": [
                "GUILD_CHAT_SERVER_SCOPE_DEFERRED",
                "GUILD_WAR_SERVER_SCOPE_DEFERRED",
                "GUILD_REWARD_LIVE_DISABLED",
            ],
            "guild_reward_live_grant": False,
            "membership_server_scope_enforced": True,
            "search_server_scope_enforced": True,
            "chat_state": "DEFERRED",
            "war_state": "DEFERRED",
            "rewards_state": "DEFERRED_LEDGER_GATED_OFF",
            "legacy_route_quarantined": _flag_legacy_quarantined(),
            "_slc_pack_108_guild_strict_preflight": True,
        }

    @router.get("/guild/strict/status")
    async def gs_status(
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        await _require_pack_108_test_user(db, uid)
        sid = _validate_server_id(server_id)
        if not _flag_membership_read():
            return {
                "surface": "guild_strict_status",
                "server_id": sid,
                "status": "READY_GATED_READ_DISABLED",
                "membership": None,
                "active_blockers": [
                    "GUILD_MEMBERSHIP_SERVER_SCOPE_REQUIRED",
                    "GUILD_REWARD_LIVE_DISABLED",
                ],
                "_slc_pack_108_guild_strict_status": True,
            }
        # Read-only server-scoped: cerca membership in `guild_memberships_v2`
        # collection (NON modifica nulla; restituisce None se assente).
        membership_doc = await db.guild_memberships_v2.find_one({
            "user_id": uid, "server_id": sid,
        })
        membership_payload = None
        if membership_doc:
            membership_payload = {
                "user_id": uid,
                "server_id": sid,
                "guild_id": membership_doc.get("guild_id"),
                "role": membership_doc.get("role", "member"),
                "joined_at": str(membership_doc.get("joined_at", "")),
            }
        return {
            "surface": "guild_strict_status",
            "server_id": sid,
            "status": "READ_OK_SERVER_SCOPED",
            "membership": membership_payload,
            "active_blockers": [
                "GUILD_CHAT_SERVER_SCOPE_DEFERRED",
                "GUILD_WAR_SERVER_SCOPE_DEFERRED",
                "GUILD_REWARD_LIVE_DISABLED",
            ],
            "reward_live_general": False,
            "_slc_pack_108_guild_strict_status": True,
        }

    @router.get("/guild/strict/search")
    async def gs_search(
        server_id: str = None,
        q: str = "",
        limit: int = 20,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        await _require_pack_108_test_user(db, uid)
        sid = _validate_server_id(server_id)
        if not _flag_search_read():
            return {
                "surface": "guild_strict_search",
                "server_id": sid,
                "status": "READY_GATED_SEARCH_DISABLED",
                "results": [],
                "active_blockers": [
                    "GUILD_SERVER_SCOPE_REQUIRED",
                    "GUILD_REWARD_LIVE_DISABLED",
                ],
                "_slc_pack_108_guild_strict_search": True,
            }
        # Cap di sicurezza sul limit.
        try:
            limit = max(1, min(int(limit or 20), 50))
        except Exception:
            limit = 20
        q_clean = (q or "").strip()[:64]
        query: Dict[str, Any] = {"server_id": sid}
        if q_clean:
            query["name"] = {"$regex": f"^{q_clean}", "$options": "i"}
        cursor = db.guilds_v2.find(query).limit(limit)
        guilds: List[Dict[str, Any]] = []
        async for g in cursor:
            guilds.append({
                "guild_id": g.get("guild_id") or g.get("id"),
                "name": g.get("name", ""),
                "server_id": g.get("server_id"),
                "member_count": int(g.get("member_count", 0) or 0),
                "level": int(g.get("level", 1) or 1),
            })
        return {
            "surface": "guild_strict_search",
            "server_id": sid,
            "q": q_clean,
            "status": "READ_OK_SERVER_SCOPED",
            "results": guilds,
            "count": len(guilds),
            "active_blockers": [
                "GUILD_CHAT_SERVER_SCOPE_DEFERRED",
                "GUILD_WAR_SERVER_SCOPE_DEFERRED",
                "GUILD_REWARD_LIVE_DISABLED",
            ],
            "reward_live_general": False,
            "_slc_pack_108_guild_strict_search": True,
        }

    @router.post("/guild/strict/membership/preview")
    async def gs_membership_preview(
        server_id: str = None,
        guild_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        """Pure-preview: NON crea né muta membership. Restituisce solo se la
        richiesta sarebbe valida server-scope-wise.
        """
        uid = current_user["id"]
        await _require_pack_108_test_user(db, uid)
        sid = _validate_server_id(server_id)
        if not guild_id or not isinstance(guild_id, str) or not guild_id.strip():
            raise HTTPException(400, detail={
                "blocker": "GUILD_ID_REQUIRED",
                "server_scope_required": True,
            })
        gid = guild_id.strip()
        # Lookup read-only su guilds_v2 per coerenza server-scope.
        guild_doc = await db.guilds_v2.find_one({
            "guild_id": gid, "server_id": sid,
        })
        guild_exists_in_server = guild_doc is not None
        # Lookup membership corrente (read-only).
        existing_membership = await db.guild_memberships_v2.find_one({
            "user_id": uid, "server_id": sid,
        })
        return {
            "surface": "guild_strict_membership_preview",
            "server_id": sid,
            "guild_id": gid,
            "status": "PREVIEW_ONLY_NO_WRITE",
            "guild_exists_in_server": guild_exists_in_server,
            "user_has_membership_in_server": existing_membership is not None,
            "would_be_allowed": (
                guild_exists_in_server and existing_membership is None
            ),
            "write_disabled": True,
            "active_blockers": [
                "GUILD_MEMBERSHIP_SERVER_SCOPE_REQUIRED",
                "GUILD_REWARD_LIVE_DISABLED",
            ],
            "reward_live_general": False,
            "deferred_next_step": "AUTORIZZO_V110_GUILD_LIVE_PACK_NEXT",
            "_slc_pack_108_guild_strict_membership_preview": True,
        }
