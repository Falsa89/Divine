"""Pack 101 — Tower Strict server-scoped endpoints (preview-only, reward quarantined).

Endpoints registrati:
  * GET  /api/tower/strict/health
  * GET  /api/tower/strict/status?server_id=<sid>
  * POST /api/tower/strict/preflight?server_id=<sid>            (test-only marker)
  * POST /api/tower/strict/battle/preview?server_id=<sid>&floor=<n>

SAFETY Pack 101:
  * Storage primario: `player_server_profiles.tower_progress` (server-scoped).
  * NESSUN write su `db.tower_progress` legacy collection.
  * NESSUNA mutation su `users.gold/users.gems/users.experience`.
  * Battle preview è deterministica (no random), ritorna solo `victory/team_power/enemy_power`
    + `next_step="REWARD_QUARANTINED_PENDING_LEDGER"`. Nessun reward grant. Nessun ledger write.
  * Kill switch `TOWER_STRICT_PREFLIGHT_ENABLED` (default OFF) blocca preflight.
  * PSP server-scoped check obbligatorio. No fallback s1.
  * Marker audit `_slc_pack_101_strict` su tutte le scritture.
"""
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException, Depends

USER_TEST_MARKER = "pack_101_test_artifact"
LEGACY_KILL_SWITCH_ENV = "TOWER_LEGACY_LIVE_ENABLED"
PREFLIGHT_KILL_SWITCH_ENV = "TOWER_STRICT_PREFLIGHT_ENABLED"
STRICT_MARKER_FIELD = "_slc_pack_101_strict"


def _truthy(v: Optional[str]) -> bool:
    return str(v or "false").strip().lower() in ("true", "1", "yes", "on")


def _legacy_on() -> bool:
    return _truthy(os.getenv(LEGACY_KILL_SWITCH_ENV))


def _preflight_on() -> bool:
    return _truthy(os.getenv(PREFLIGHT_KILL_SWITCH_ENV))


def _default_tower_progress() -> Dict[str, Any]:
    return {
        "floor": 1,
        "highest_floor": 1,
        "rewards_claimed": [],
        "last_battle_at": None,
        STRICT_MARKER_FIELD: True,
    }


async def get_tower_progress_strict(db, user_id: str, server_id: str) -> Dict[str, Any]:
    """Lettura idempotente: ritorna PSP.tower_progress o default se assente.

    NON crea documenti. NON muta users.*. Solo lettura.
    """
    psp = await db.player_server_profiles.find_one({"user_id": user_id, "server_id": server_id})
    if not psp:
        return {"initialized": False, **_default_tower_progress(), "server_id": server_id}
    tp = psp.get("tower_progress") or {}
    if not tp:
        return {"initialized": False, **_default_tower_progress(), "server_id": server_id}
    return {
        "initialized": True,
        "floor": int(tp.get("floor", 1)),
        "highest_floor": int(tp.get("highest_floor", tp.get("floor", 1))),
        "rewards_claimed": list(tp.get("rewards_claimed") or []),
        "last_battle_at": tp.get("last_battle_at"),
        "server_id": server_id,
        STRICT_MARKER_FIELD: bool(tp.get(STRICT_MARKER_FIELD, False)),
    }


def _preview_compute(team_power: int, floor: int) -> Dict[str, Any]:
    """Calcolo deterministico previsionale (no random).

    Soglia: vittoria se team_power >= enemy_power.
    enemy_power = 2000 + floor*800 + floor**1.5 * 200 (formula come legacy, ma deterministica).
    """
    enemy_power = int(2000 + floor * 800 + (floor ** 1.5) * 200)
    victory_predicted = team_power >= enemy_power
    return {
        "floor": floor,
        "team_power": int(team_power),
        "enemy_power": int(enemy_power),
        "victory_predicted": bool(victory_predicted),
        "deterministic": True,
    }


def register_tower_strict_routes(router, db, get_current_user, *_a, **_kw):

    @router.get("/tower/strict/health")
    async def tower_strict_health():
        return {
            "endpoint_group": "/api/tower/strict",
            "legacy_kill_switch_env": LEGACY_KILL_SWITCH_ENV,
            "legacy_kill_switch_live_enabled": _legacy_on(),
            "preflight_kill_switch_env": PREFLIGHT_KILL_SWITCH_ENV,
            "preflight_kill_switch_live_enabled": _preflight_on(),
            "strict_marker_field": STRICT_MARKER_FIELD,
            "reward_live_general": False,
            "tower_reward_live_grant": False,
            "tower_progress_server_scope_status": "TOWER_PROGRESS_SERVER_SCOPED_STRICT_READY",
            "tower_reward_quarantine_status": "REWARD_QUARANTINED_PENDING_LEDGER",
            "storage_primary": "player_server_profiles.tower_progress",
            "no_users_gold_gems_experience_mutation": True,
            "pack_origin": "pack_101",
            "release_readiness_claimed": False,
        }

    @router.get("/tower/strict/status")
    async def tower_strict_status(
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        if not server_id or not isinstance(server_id, str) or not server_id.strip():
            raise HTTPException(400, detail={"blocker": "SERVER_ID_REQUIRED"})
        sid = server_id.strip()
        # PSP server-scoped check OBBLIGATORIO
        psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
        if not psp:
            raise HTTPException(409, detail={
                "blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
                "server_id": sid,
            })
        progress = await get_tower_progress_strict(db, uid, sid)
        return {
            "server_id": sid,
            "progress": progress,
            "reward_live_general": False,
            "tower_reward_live_grant": False,
            "tower_reward_quarantine_status": "REWARD_QUARANTINED_PENDING_LEDGER",
            "_slc_pack_101_tower_strict_status": True,
        }

    @router.post("/tower/strict/preflight")
    async def tower_strict_preflight(
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        # 1. Kill switch dedicato
        if not _preflight_on():
            raise HTTPException(503, detail={
                "blocker": "TOWER_STRICT_PREFLIGHT_DISABLED",
                "kill_switch_env": PREFLIGHT_KILL_SWITCH_ENV,
            })
        # 2. server_id obbligatorio
        if not server_id or not isinstance(server_id, str) or not server_id.strip():
            raise HTTPException(400, detail={"blocker": "SERVER_ID_REQUIRED"})
        sid = server_id.strip()
        # 3. Test marker obbligatorio: solo utenti marcati possono preflight
        user_doc = await db.users.find_one({"id": uid})
        if not user_doc or not user_doc.get(USER_TEST_MARKER):
            raise HTTPException(403, detail={
                "blocker": "PREFLIGHT_ENDPOINT_TEST_ONLY",
                "marker_required": USER_TEST_MARKER,
            })
        # 4. PSP obbligatoria
        psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
        if not psp:
            raise HTTPException(409, detail={
                "blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
                "server_id": sid,
            })
        # 5. Inizializza/conferma `tower_progress` su PSP. NO mutation users.*
        existing_tp = psp.get("tower_progress") or {}
        if existing_tp and existing_tp.get(STRICT_MARKER_FIELD):
            return {
                "idempotent_replay": True,
                "server_id": sid,
                "tower_progress": existing_tp,
                "reward_live_general": False,
                "tower_reward_live_grant": False,
                "_slc_pack_101_preflight_idempotent": True,
            }
        seed = _default_tower_progress()
        seed["initialized_at"] = datetime.utcnow()
        await db.player_server_profiles.update_one(
            {"user_id": uid, "server_id": sid},
            {"$set": {"tower_progress": seed, "_slc_pack_101_strict_preflight": True}},
            upsert=False,
        )
        return {
            "idempotent_replay": False,
            "server_id": sid,
            "tower_progress": seed,
            "reward_live_general": False,
            "tower_reward_live_grant": False,
            "_slc_pack_101_preflight": True,
        }

    @router.post("/tower/strict/battle/preview")
    async def tower_strict_battle_preview(
        server_id: str = None,
        floor: int = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        # server_id obbligatorio
        if not server_id or not isinstance(server_id, str) or not server_id.strip():
            raise HTTPException(400, detail={"blocker": "SERVER_ID_REQUIRED"})
        sid = server_id.strip()
        # floor opzionale: usa quello del progress se assente; minimo 1
        psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
        if not psp:
            raise HTTPException(409, detail={
                "blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
                "server_id": sid,
            })
        current_floor = int((psp.get("tower_progress") or {}).get("floor", 1))
        if floor is None:
            floor_eff = current_floor
        else:
            try:
                floor_eff = max(1, int(floor))
            except Exception:
                raise HTTPException(422, detail={"blocker": "INVALID_FLOOR"})
        # team_power lettura: PSP-scoped active team se presente, altrimenti default 5000
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        team_power = int((team or {}).get("total_power", 5000))
        preview = _preview_compute(team_power, floor_eff)
        return {
            "server_id": sid,
            "current_floor": current_floor,
            "preview": preview,
            "reward_live_general": False,
            "tower_reward_live_grant": False,
            "no_reward_grant_on_preview": True,
            "next_step": "REWARD_QUARANTINED_PENDING_LEDGER",
            "_slc_pack_101_battle_preview": True,
        }
