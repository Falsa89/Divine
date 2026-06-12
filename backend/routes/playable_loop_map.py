"""Pack 108 — Frontend Playable Loop Map (Alpha).

Endpoint READ-ONLY che espone lo stato canonico delle surface giocabili.
Non dichiara `release_readiness`. Tutti i flag UI sensibili sono
rappresentati come `default_off`, lo status di ogni surface usa il
vocabolario canonico:
  * READY
  * READY_GATED
  * DEFERRED
  * LOCKED
  * PREVIEW
  * QUARANTINED

Il client (Expo) usa questa mappa per costruire Home/Lobby senza false-ready
labels. Server switch deve invocare di nuovo questo endpoint con il nuovo
`server_id`.
"""
import os
from typing import Any, Dict, Optional
from fastapi import HTTPException, Depends

PACK_108_USER_TEST_MARKER = "pack_108_test_artifact"


def _truthy(v: Optional[str]) -> bool:
    return str(v or "false").strip().lower() in ("true", "1", "yes", "on")


def _flag(name: str, default: str = "false") -> bool:
    return _truthy(os.getenv(name, default))


def _validate_server_id(sid: Optional[str]) -> str:
    if not sid or not isinstance(sid, str) or not sid.strip():
        raise HTTPException(400, detail={
            "blocker": "SERVER_ID_REQUIRED",
            "playable_loop_server_scope_required": True,
            "no_silent_fallback_to_s1": True,
        })
    return sid.strip()


def _build_alpha_map(sid: str) -> Dict[str, Any]:
    """Costruisce la mappa Alpha della playable loop.

    NESSUNA surface deve avere `status=READY` se la sua reward live non è
    abilitata. Tutte le surface con reward gate restano `READY_GATED`/
    `DEFERRED`/`LOCKED`.
    """
    return {
        "server_id": sid,
        "alpha_map_version": "pack_108_v1",
        "release_readiness_claimed": False,
        "reward_live_general": _flag("REWARD_LIVE_GENERAL"),
        "no_silent_fallback_to_s1": True,
        "surfaces": {
            "home": {
                "status": "READY_GATED",
                "ui_flag": "EXPO_PUBLIC_DAILY_HOME_UNLOCK",
                "ui_flag_default_off": True,
                "reward_live": False,
                "server_scope_enforced": True,
                "notes": "Home shell visibile; daily claim entrypoint locked se UI flag OFF.",
            },
            "lobby": {
                "status": "READY_GATED",
                "ui_flag": "EXPO_PUBLIC_LOBBY_UI_ENABLED",
                "ui_flag_default_off": True,
                "reward_live": False,
                "server_scope_enforced": True,
                "notes": "Lobby pre-battle entrypoint; nessuna mutation auto.",
            },
            "daily": {
                "status": "READY_GATED",
                "ui_flag": "EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED",
                "ui_flag_default_off": True,
                "reward_live": _flag("REWARD_CLAIM_LEDGER_LIVE_ENABLED") and _flag("DAILY_LOGIN_CLAIM_ENABLED"),
                "server_scope_enforced": True,
                "notes": "Daily login/quest claim dietro doppio kill switch backend.",
            },
            "tower": {
                "status": "READY_GATED",
                "ui_flag": "EXPO_PUBLIC_TOWER_STRICT_UI_ENABLED",
                "ui_flag_default_off": True,
                "reward_live": False,
                "server_scope_enforced": True,
                "notes": "Tower strict preflight/preview; reward live deferred.",
            },
            "shop": {
                "status": "READY_GATED",
                "ui_flag": "EXPO_PUBLIC_ECONOMY_STRICT_UI_ENABLED",
                "ui_flag_default_off": True,
                "reward_live": False,
                "server_scope_enforced": True,
                "notes": "Shop strict server-scoped; no premium/IAP/gacha live.",
            },
            "forge": {
                "status": "READY_GATED",
                "ui_flag": "EXPO_PUBLIC_FORGE_STRICT_UI_ENABLED",
                "ui_flag_default_off": True,
                "reward_live": False,
                "server_scope_enforced": True,
                "notes": "Forge/Upgrade/Fusion PSP material ledger; spend strict.",
            },
            "rewards": {
                "status": "READY_GATED",
                "ui_flag": "EXPO_PUBLIC_REWARD_CENTER_UI_ENABLED",
                "ui_flag_default_off": True,
                "reward_live": False,
                "server_scope_enforced": True,
                "notes": "Mail/Achievements/Daily-Weekly controlled rewards; deferred default.",
            },
            "guild": {
                "status": "READY_GATED_DEFERRED",
                "ui_flag": "EXPO_PUBLIC_GUILD_UI_ENABLED",
                "ui_flag_default_off": True,
                "reward_live": False,
                "server_scope_enforced": True,
                "legacy_route_quarantined": True,
                "notes": "Guild strict read/preview only; legacy account-wide quarantineato.",
            },
            "arena": {
                "status": "LOCKED",
                "ui_flag": "EXPO_PUBLIC_ARENA_UI_ENABLED",
                "ui_flag_default_off": True,
                "reward_live": False,
                "server_scope_enforced": True,
                "notes": "Arena reward live disabled; nessuna route arena live in produzione.",
            },
            "pvp": {
                "status": "LOCKED",
                "ui_flag": "EXPO_PUBLIC_PVP_UI_ENABLED",
                "ui_flag_default_off": True,
                "reward_live": False,
                "server_scope_enforced": True,
                "notes": "PvP ranking server-scope deferred.",
            },
            "event": {
                "status": "LOCKED",
                "ui_flag": "EXPO_PUBLIC_EVENT_UI_ENABLED",
                "ui_flag_default_off": True,
                "reward_live": False,
                "server_scope_enforced": True,
                "notes": "Event reward live disabled; nessuna route event live in produzione.",
            },
        },
        "copy_audit": {
            "locked_copy": "Bloccato (Closed Alpha)",
            "deferred_copy": "In preparazione (deferred)",
            "ready_gated_copy": "Disponibile in anteprima (server-scoped)",
            "preview_copy": "Anteprima sola lettura",
            "quarantined_copy": "Route legacy in quarantena (server-scope retrofit in corso)",
            "no_false_ready_labels": True,
        },
        "safety_statements": {
            "no_users_gold_gems_experience_mutation": True,
            "no_premium_grants": True,
            "no_iap_gacha_payment": True,
            "no_arena_pvp_guild_event_reward_live": True,
            "no_account_wide_guild_writes": True,
            "no_hardcoded_server_id_s1": True,
            "no_cross_server_guild_leak": True,
        },
        "_slc_pack_108_playable_loop_map": True,
    }


def register_playable_loop_map_routes(router, db, get_current_user, *_a, **_kw):

    @router.get("/playable-loop/health")
    async def pl_health():
        return {
            "endpoint_group": "/api/playable-loop",
            "pack_origin": "pack_108",
            "pack_108_test_marker": PACK_108_USER_TEST_MARKER,
            "alpha_map_version": "pack_108_v1",
            "release_readiness_claimed": False,
            "no_silent_fallback_to_s1": True,
            "reward_live_general": _flag("REWARD_LIVE_GENERAL"),
            "_slc_pack_108_playable_loop_health": True,
        }

    @router.get("/playable-loop/map")
    async def pl_map(server_id: str = None):
        """Mappa Alpha della playable loop server-scoped.

        Aperto (non richiede auth) per consentire al client Home/Lobby di
        costruire l'UI prima del login. Comunque server_scoped: server_id
        è REQUIRED, no silent fallback a s1.
        """
        sid = _validate_server_id(server_id)
        return _build_alpha_map(sid)

    @router.get("/playable-loop/state")
    async def pl_state(
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        """Stato playable loop per l'utente corrente (test-only marker).

        Read-only: combina la mappa Alpha + un riassunto kill-switch lato
        backend. Non muta nulla.
        """
        uid = current_user["id"]
        user_doc = await db.users.find_one({"id": uid})
        if not user_doc or not user_doc.get(PACK_108_USER_TEST_MARKER):
            raise HTTPException(403, detail={
                "blocker": "PLAYABLE_LOOP_STATE_TEST_ONLY",
                "marker_required": PACK_108_USER_TEST_MARKER,
            })
        sid = _validate_server_id(server_id)
        amap = _build_alpha_map(sid)
        amap["user_id"] = uid
        amap["server_switch_refresh_required"] = True
        return amap
