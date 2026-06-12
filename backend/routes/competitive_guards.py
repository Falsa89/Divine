"""Pack 107 — Competitive / Social / Live Mode Server-Scope Guards.

Endpoints registrati su prefix `/api/competitive-guards`:

  * GET  /api/competitive-guards/health
  * POST /api/competitive-guards/arena/preflight
  * POST /api/competitive-guards/pvp/preflight
  * POST /api/competitive-guards/guild/preflight
  * POST /api/competitive-guards/event/preflight

Pack 107 è un layer di **audit + guard onesto**. Non implementa reward live.
Ogni preflight ritorna 200 con lo stato canonico:
  * arena: READY_GATED_REWARDS_DEFERRED (nessuna route arena live in produzione)
  * pvp: READY_GATED_REWARDS_DEFERRED (nessuna route pvp live in produzione)
  * guild: AUDIT_LEGACY_NOT_SERVER_SCOPED (route legacy account-wide, quarantena via blocker)
  * event: READY_GATED_REWARDS_DEFERRED (nessuna route event live in produzione)

Tutti i preflight ritornano i blocker canonici PROMPT_MAIN per route unsafe:
  * ARENA_SERVER_SCOPE_REQUIRED / ARENA_REWARD_LIVE_DISABLED
  * PVP_RANKING_SERVER_SCOPE_DEFERRED
  * GUILD_SERVER_SCOPE_REQUIRED / GUILD_REWARD_LIVE_DISABLED
  * EVENT_SERVER_SCOPE_REQUIRED / EVENT_REWARD_LIVE_DISABLED
  * LEADERBOARD_SERVER_SCOPE_REQUIRED
"""
import os
from typing import Any, Dict, Optional
from fastapi import HTTPException, Depends

PACK_107_USER_TEST_MARKER = "pack_107_test_artifact"


def _truthy(v: Optional[str]) -> bool:
    return str(v or "false").strip().lower() in ("true", "1", "yes", "on")


def _arena_reward_on() -> bool: return _truthy(os.getenv("ARENA_REWARD_LIVE_ENABLED"))
def _pvp_reward_on() -> bool: return _truthy(os.getenv("PVP_REWARD_LIVE_ENABLED"))
def _guild_reward_on() -> bool: return _truthy(os.getenv("GUILD_REWARD_LIVE_ENABLED"))
def _event_reward_on() -> bool: return _truthy(os.getenv("EVENT_REWARD_LIVE_ENABLED"))


async def _require_pack_107_test_user(db, uid: str) -> dict:
    user_doc = await db.users.find_one({"id": uid})
    if not user_doc or not user_doc.get(PACK_107_USER_TEST_MARKER):
        raise HTTPException(403, detail={
            "blocker": "COMPETITIVE_GUARDS_ENDPOINT_TEST_ONLY",
            "marker_required": PACK_107_USER_TEST_MARKER,
        })
    return user_doc


def _validate_server_id(sid: Optional[str]) -> str:
    if not sid or not isinstance(sid, str) or not sid.strip():
        raise HTTPException(400, detail={"blocker": "SERVER_ID_REQUIRED"})
    return sid.strip()


def register_competitive_guards_routes(router, db, get_current_user, *_a, **_kw):

    @router.get("/competitive-guards/health")
    async def cg_health():
        return {
            "endpoint_group": "/api/competitive-guards",
            "pack_origin": "pack_107",
            "pack_107_test_marker": PACK_107_USER_TEST_MARKER,
            "kill_switches": {
                "ARENA_REWARD_LIVE_ENABLED": _arena_reward_on(),
                "PVP_REWARD_LIVE_ENABLED": _pvp_reward_on(),
                "GUILD_REWARD_LIVE_ENABLED": _guild_reward_on(),
                "EVENT_REWARD_LIVE_ENABLED": _event_reward_on(),
            },
            "surfaces": {
                "arena": "READY_GATED_REWARDS_DEFERRED",
                "pvp": "READY_GATED_REWARDS_DEFERRED",
                "guild": "AUDIT_LEGACY_NOT_SERVER_SCOPED",
                "event": "READY_GATED_REWARDS_DEFERRED",
            },
            "blockers_canonical": [
                "ARENA_SERVER_SCOPE_REQUIRED",
                "ARENA_REWARD_LIVE_DISABLED",
                "PVP_RANKING_SERVER_SCOPE_DEFERRED",
                "GUILD_SERVER_SCOPE_REQUIRED",
                "GUILD_REWARD_LIVE_DISABLED",
                "EVENT_SERVER_SCOPE_REQUIRED",
                "EVENT_REWARD_LIVE_DISABLED",
                "LEADERBOARD_SERVER_SCOPE_REQUIRED",
            ],
            "reward_live_general": False,
            "premium_grants": False,
            "release_readiness_claimed": False,
            "no_users_gold_gems_experience_mutation": True,
            "no_arena_pvp_guild_event_reward_live": True,
            "no_cross_server_ranking_leak": True,
            "_slc_pack_107_competitive_guards_health": True,
        }

    @router.post("/competitive-guards/arena/preflight")
    async def arena_preflight(
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        await _require_pack_107_test_user(db, uid)
        sid = _validate_server_id(server_id)
        return {
            "surface": "arena", "server_id": sid,
            "status": "READY_GATED_REWARDS_DEFERRED",
            "active_blockers": ["ARENA_SERVER_SCOPE_REQUIRED", "ARENA_REWARD_LIVE_DISABLED"],
            "arena_reward_live_grant": False,
            "mmr_server_scope_enforcement_state": "NO_LIVE_MMR_ROUTE_PRESENT",
            "rewards_state": "DEFERRED_LEDGER_GATED_OFF",
            "leaderboard_server_scope_required": True,
            "_slc_pack_107_arena_preflight": True,
        }

    @router.post("/competitive-guards/pvp/preflight")
    async def pvp_preflight(
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        await _require_pack_107_test_user(db, uid)
        sid = _validate_server_id(server_id)
        return {
            "surface": "pvp", "server_id": sid,
            "status": "READY_GATED_REWARDS_DEFERRED",
            "active_blockers": ["PVP_RANKING_SERVER_SCOPE_DEFERRED"],
            "pvp_reward_live_grant": False,
            "ranking_server_scope_enforcement_state": "NO_LIVE_PVP_RANKING_ROUTE_PRESENT",
            "rewards_state": "DEFERRED_LEDGER_GATED_OFF",
            "_slc_pack_107_pvp_preflight": True,
        }

    @router.post("/competitive-guards/guild/preflight")
    async def guild_preflight(
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        await _require_pack_107_test_user(db, uid)
        sid = _validate_server_id(server_id)
        # Audit: routes/guild.py legacy NON e' server-scoped (0 occorrenze server_id).
        # Pack 107 segnala il blocker onesto. La quarantena di guild.py NON e'
        # in scope di Pack 107 (audit-only). Una futura Pack potra' applicare
        # filtri server_id alle routes esistenti.
        return {
            "surface": "guild", "server_id": sid,
            "status": "AUDIT_LEGACY_NOT_SERVER_SCOPED",
            "active_blockers": ["GUILD_SERVER_SCOPE_REQUIRED", "GUILD_REWARD_LIVE_DISABLED"],
            "guild_reward_live_grant": False,
            "legacy_route_server_scope_enforcement_state": "NOT_SERVER_SCOPED_LEGACY",
            "legacy_route_file": "backend/routes/guild.py",
            "rewards_state": "DEFERRED_LEDGER_GATED_OFF",
            "guild_membership_server_scope_required": True,
            "guild_search_server_scope_required": True,
            "deferred_next_step": "AUTORIZZO_V110_GUILD_SERVER_SCOPE_RETROFIT_PACK_NEXT",
            "_slc_pack_107_guild_preflight": True,
        }

    @router.post("/competitive-guards/event/preflight")
    async def event_preflight(
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        await _require_pack_107_test_user(db, uid)
        sid = _validate_server_id(server_id)
        return {
            "surface": "event", "server_id": sid,
            "status": "READY_GATED_REWARDS_DEFERRED",
            "active_blockers": ["EVENT_SERVER_SCOPE_REQUIRED", "EVENT_REWARD_LIVE_DISABLED"],
            "event_reward_live_grant": False,
            "event_progress_server_scope_enforcement_state": "NO_LIVE_EVENT_ROUTE_PRESENT",
            "rewards_state": "DEFERRED_LEDGER_GATED_OFF",
            "leaderboard_server_scope_required": True,
            "_slc_pack_107_event_preflight": True,
        }
