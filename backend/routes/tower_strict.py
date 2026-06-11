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
import hashlib
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException, Depends
from pydantic import BaseModel

# Pack 102 — import del catalog statico dei 100 piani Tower (read-only).
from data.tower_floor_catalog_v1 import (
    TOWER_FLOOR_CATALOG_V1,
    CATALOG_VERSION as TOWER_CATALOG_VERSION,
    TOTAL_LAUNCH_FLOORS,
    get_catalog_summary as _tower_catalog_summary,
    get_floor as _tower_catalog_floor,
)

# Pack 103 — reward source + event bridge per tower floor completion
from utils.reward_source_registry import (
    REWARD_SOURCE_REGISTRY,
    lookup_source,
    is_source_live,
    get_grant_fn,
    _PremiumGrantBlocked,
    _RewardTypeNotAllowed,
)
from utils.daily_quest_events import record_daily_quest_event as _record_dq_event

USER_TEST_MARKER = "pack_101_test_artifact"
PACK_103_USER_TEST_MARKER = "pack_103_test_artifact"
LEGACY_KILL_SWITCH_ENV = "TOWER_LEGACY_LIVE_ENABLED"
PREFLIGHT_KILL_SWITCH_ENV = "TOWER_STRICT_PREFLIGHT_ENABLED"
EXECUTE_KILL_SWITCH_ENV = "TOWER_STRICT_EXECUTE_ENABLED"
FLOOR_CLAIM_KILL_SWITCH_ENV = "TOWER_FLOOR_CLAIM_ENABLED"
GLOBAL_LEDGER_KILL_SWITCH_ENV = "REWARD_CLAIM_LEDGER_LIVE_ENABLED"
STRICT_MARKER_FIELD = "_slc_pack_101_strict"
TOWER_FLOOR_CLAIM_SOURCE = "tower_floor_completion_claim"


def _truthy(v: Optional[str]) -> bool:
    return str(v or "false").strip().lower() in ("true", "1", "yes", "on")


def _legacy_on() -> bool:
    return _truthy(os.getenv(LEGACY_KILL_SWITCH_ENV))


def _preflight_on() -> bool:
    return _truthy(os.getenv(PREFLIGHT_KILL_SWITCH_ENV))


def _execute_on() -> bool:
    return _truthy(os.getenv(EXECUTE_KILL_SWITCH_ENV))


def _floor_claim_on() -> bool:
    return _truthy(os.getenv(FLOOR_CLAIM_KILL_SWITCH_ENV))


def _global_ledger_on() -> bool:
    return _truthy(os.getenv(GLOBAL_LEDGER_KILL_SWITCH_ENV))


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
            "execute_kill_switch_env": EXECUTE_KILL_SWITCH_ENV,
            "execute_kill_switch_live_enabled": _execute_on(),
            "floor_claim_kill_switch_env": FLOOR_CLAIM_KILL_SWITCH_ENV,
            "floor_claim_kill_switch_live_enabled": _floor_claim_on(),
            "global_ledger_kill_switch_env": GLOBAL_LEDGER_KILL_SWITCH_ENV,
            "global_ledger_kill_switch_live_enabled": _global_ledger_on(),
            "pack_103_execute_endpoint": "/api/tower/strict/battle/execute",
            "pack_103_test_marker": PACK_103_USER_TEST_MARKER,
            "pack_103_floor_claim_source": TOWER_FLOOR_CLAIM_SOURCE,
            "pack_103_daily_quest_event": "tower_floor_clear_success",
            "pack_103_daily_quest_target": "daily_quest_2",
            "strict_marker_field": STRICT_MARKER_FIELD,
            "reward_live_general": False,
            "tower_reward_live_grant": False,
            "tower_progress_server_scope_status": "TOWER_PROGRESS_SERVER_SCOPED_STRICT_READY",
            "tower_reward_quarantine_status": "REWARD_QUARANTINED_PENDING_LEDGER",
            "storage_primary": "player_server_profiles.tower_progress",
            "no_users_gold_gems_experience_mutation": True,
            "pack_origin": "pack_101",
            "release_readiness_claimed": False,
            "tower_catalog_version": TOWER_CATALOG_VERSION,
            "tower_catalog_total_floors": TOTAL_LAUNCH_FLOORS,
            "tower_catalog_pack_origin": "pack_102",
            "tower_catalog_content_identical_across_servers": True,
            "tower_catalog_deterministic": True,
            "tower_catalog_uses_only_launch_base_heroes": True,
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
        # Pack 102 — wiring al catalog. Floor fuori range -> 404 esplicito.
        catalog_floor = _tower_catalog_floor(floor_eff)
        if catalog_floor is None:
            raise HTTPException(404, detail={
                "blocker": "FLOOR_OUT_OF_CATALOG_RANGE",
                "floor": floor_eff,
                "catalog_total_launch_floors": TOTAL_LAUNCH_FLOORS,
            })
        # team_power lettura: PSP-scoped active team se presente, altrimenti default 5000
        team = await db.teams.find_one({"user_id": uid, "is_active": True})
        team_power = int((team or {}).get("total_power", 5000))
        preview = _preview_compute(team_power, floor_eff)
        return {
            "server_id": sid,
            "current_floor": current_floor,
            "preview": preview,
            "catalog_floor": catalog_floor,
            "catalog_version": TOWER_CATALOG_VERSION,
            "reward_live_general": False,
            "tower_reward_live_grant": False,
            "no_reward_grant_on_preview": True,
            "next_step": "REWARD_QUARANTINED_PENDING_LEDGER",
            "_slc_pack_101_battle_preview": True,
            "_slc_pack_102_catalog_wired": True,
        }

    @router.post("/tower/strict/battle/execute")
    async def tower_strict_battle_execute(
        server_id: str = None,
        floor: int = None,
        idempotency_token: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        """Pack 103 — Tower strict battle execute (gated, server-scoped).

        Safety:
          * Triple kill switch AND: global ledger + execute + floor claim default OFF.
          * Test-only finche\u0300 non c'e\u0300 runtime battle reale: marker `pack_103_test_artifact`.
          * Floor deve essere current o current+1 del PSP.tower_progress (no skip).
          * Idempotency_token obbligatorio. Server-side claim_key derivato deterministicamente.
          * Reward via ledger source `tower_floor_completion_claim` (PSP soft only, no premium).
          * Advance PSP.tower_progress.floor solo dopo grant idempotente.
          * Emette evento `tower_floor_clear_success` -> daily_quest_2 (server-scoped).
          * NO mutation users.gold/users.gems/users.experience. NO legacy collection writes.
        """
        uid = current_user["id"]

        # 1. Triple kill switch AND
        if not _global_ledger_on():
            raise HTTPException(503, detail={
                "blocker": "REWARD_CLAIM_LEDGER_DISABLED",
                "kill_switch_env": GLOBAL_LEDGER_KILL_SWITCH_ENV,
            })
        if not _execute_on():
            raise HTTPException(503, detail={
                "blocker": "TOWER_STRICT_EXECUTE_DISABLED",
                "kill_switch_env": EXECUTE_KILL_SWITCH_ENV,
            })
        if not _floor_claim_on():
            raise HTTPException(503, detail={
                "blocker": "TOWER_FLOOR_CLAIM_DISABLED",
                "kill_switch_env": FLOOR_CLAIM_KILL_SWITCH_ENV,
            })

        # 2. server_id + idempotency obbligatori
        if not server_id or not isinstance(server_id, str) or not server_id.strip():
            raise HTTPException(400, detail={"blocker": "SERVER_ID_REQUIRED"})
        sid = server_id.strip()
        if not idempotency_token or not isinstance(idempotency_token, str) or len(idempotency_token) < 8:
            raise HTTPException(400, detail={"blocker": "IDEMPOTENCY_TOKEN_REQUIRED"})

        # 3. floor obbligatorio + range catalog
        if floor is None:
            raise HTTPException(400, detail={"blocker": "FLOOR_REQUIRED"})
        try:
            floor_eff = int(floor)
        except Exception:
            raise HTTPException(422, detail={"blocker": "INVALID_FLOOR"})
        if floor_eff < 1 or floor_eff > TOTAL_LAUNCH_FLOORS:
            raise HTTPException(404, detail={
                "blocker": "FLOOR_OUT_OF_CATALOG_RANGE",
                "floor": floor_eff,
                "catalog_total_launch_floors": TOTAL_LAUNCH_FLOORS,
            })
        catalog_floor = _tower_catalog_floor(floor_eff)
        assert catalog_floor is not None

        # 4. PSP server-scoped check obbligatorio
        psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
        if not psp:
            raise HTTPException(409, detail={
                "blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
                "server_id": sid,
            })

        # 5. Test marker obbligatorio (Pack 103 ancora test-only finche\u0300 battle reale non esiste)
        user_doc = await db.users.find_one({"id": uid})
        if not user_doc or not user_doc.get(PACK_103_USER_TEST_MARKER):
            raise HTTPException(403, detail={
                "blocker": "EXECUTE_ENDPOINT_TEST_ONLY",
                "marker_required": PACK_103_USER_TEST_MARKER,
            })

        # 6. Server-side claim_key deterministico (precomputato per check idempotency)
        claim_key = f"tower_floor_{sid}_{floor_eff}"
        server_idem_token = hashlib.sha1(f"{claim_key}|{idempotency_token}".encode()).hexdigest()

        # 6b. Idempotency PRE-CHECK: se questo (uid, sid, claim_key) e\u0300 gia\u0300 a ledger,
        # ritorniamo replay senza ulteriori validazioni floor (PSP gia\u0300 advanced).
        existing_ledger = await db.reward_claim_ledger.find_one({
            "user_id": uid, "server_id": sid,
            "claim_source": TOWER_FLOOR_CLAIM_SOURCE,
            "claim_key": claim_key,
        })
        if existing_ledger:
            existing_ledger.pop("_id", None)
            for k in ("applied_at", "created_at"):
                v = existing_ledger.get(k)
                if hasattr(v, "isoformat"):
                    existing_ledger[k] = v.isoformat()
            return {
                "idempotent_replay": True,
                "server_id": sid,
                "floor": floor_eff,
                "claim_source": TOWER_FLOOR_CLAIM_SOURCE,
                "claim_key": claim_key,
                "rewards": existing_ledger.get("rewards"),
                "applied_at": existing_ledger.get("applied_at"),
                "tower_floor_clear_success_event_replay": True,
                "reward_live_general": False,
                "premium_grant_blocked": True,
                "_slc_pack_103_tower_execute_idempotent": True,
            }

        # 7. floor must equal current or current+1 (no skip) - solo per nuovi claim
        current_floor = int((psp.get("tower_progress") or {}).get("floor", 1))
        if floor_eff != current_floor and floor_eff != current_floor + 1:
            raise HTTPException(409, detail={
                "blocker": "FLOOR_NOT_ALLOWED_FOR_PSP",
                "psp_current_floor": current_floor,
                "attempted_floor": floor_eff,
                "allowed_floors": [current_floor, current_floor + 1],
            })

        # 9. Grant via ledger source registry
        src = lookup_source(TOWER_FLOOR_CLAIM_SOURCE)
        assert src and is_source_live(TOWER_FLOOR_CLAIM_SOURCE), "tower_floor_completion_claim must be live"
        grant_fn = get_grant_fn(TOWER_FLOOR_CLAIM_SOURCE)
        assert grant_fn is not None, "grant_fn missing for tower_floor_completion_claim"
        try:
            inc = grant_fn(db, uid, sid, {"_server_resolved_floor": floor_eff})
        except _PremiumGrantBlocked as e:
            raise HTTPException(422, detail={"blocker": "PREMIUM_GRANT_BLOCKED", "key": str(e)})
        except _RewardTypeNotAllowed as e:
            raise HTTPException(422, detail={"blocker": "REWARD_TYPE_NOT_ALLOWED", "key": str(e)})

        # 10. Apply grant atomically on PSP soft_currencies
        await db.player_server_profiles.update_one(
            {"user_id": uid, "server_id": sid},
            {"$inc": inc},
            upsert=False,
        )

        # 11. Insert ledger row
        now = datetime.utcnow()
        # Extract rewards summary from inc (strip soft_currencies. prefix)
        rewards_summary = {k.replace("soft_currencies.", ""): v for k, v in inc.items()}
        ledger_row = {
            "user_id": uid,
            "server_id": sid,
            "claim_source": TOWER_FLOOR_CLAIM_SOURCE,
            "claim_key": claim_key,
            "idempotency_token": server_idem_token,
            "client_idempotency_token_hash": hashlib.sha1(idempotency_token.encode()).hexdigest(),
            "floor": floor_eff,
            "rewards": {"server_scoped": rewards_summary},
            "applied_at": now,
            "created_at": now,
            "_slc_pack_103_tower_floor_completion_claim": True,
            "_slc_pack_103_server_side_claim_key": True,
            "_slc_pack_103_execution_proof_via_psp_advance": True,
            "_slc_pack_96_controlled_claim": True,
            "_slc_pack_95_reward_claim_ledger": True,
        }
        try:
            await db.reward_claim_ledger.insert_one(ledger_row)
        except Exception as e:
            # Possibile race su unique index: ritorniamo idempotent_replay
            existing = await db.reward_claim_ledger.find_one({
                "user_id": uid, "server_id": sid,
                "claim_source": TOWER_FLOOR_CLAIM_SOURCE,
                "claim_key": claim_key,
            })
            if existing:
                # Rollback grant just applied (revert inc)
                rollback_inc = {k: -v for k, v in inc.items()}
                await db.player_server_profiles.update_one(
                    {"user_id": uid, "server_id": sid},
                    {"$inc": rollback_inc},
                )
                existing.pop("_id", None)
                return {
                    "idempotent_replay": True,
                    "server_id": sid, "floor": floor_eff,
                    "claim_source": TOWER_FLOOR_CLAIM_SOURCE,
                    "claim_key": claim_key,
                    "rewards": existing.get("rewards"),
                    "applied_at": existing.get("applied_at").isoformat() if hasattr(existing.get("applied_at"), "isoformat") else existing.get("applied_at"),
                    "reward_live_general": False,
                    "premium_grant_blocked": True,
                    "_slc_pack_103_tower_execute_idempotent_race_recovered": True,
                }
            raise HTTPException(500, detail={"blocker": "LEDGER_INSERT_FAILED", "error": str(e)})

        # 12. Advance PSP.tower_progress.floor — sempre advance dopo nuovo grant
        # (idempotent_replay false). Floor cleared = floor_eff. Next becomes floor_eff+1.
        tp = psp.get("tower_progress") or {}
        new_highest = max(int(tp.get("highest_floor", 1)), floor_eff)
        next_floor = floor_eff + 1 if floor_eff < TOTAL_LAUNCH_FLOORS else floor_eff
        await db.player_server_profiles.update_one(
            {"user_id": uid, "server_id": sid},
            {"$set": {
                "tower_progress.floor": next_floor,
                "tower_progress.highest_floor": new_highest,
                "tower_progress.last_battle_at": now,
                "tower_progress._slc_pack_101_strict": True,
                "tower_progress._slc_pack_103_advance_at_floor": floor_eff,
            }},
        )

        # 13. Emit daily quest event bridge: tower_floor_clear_success -> daily_quest_2
        dq_event = await _record_dq_event(
            db, uid, sid, "tower_floor_clear_success",
            payload={"floor": floor_eff, "claim_key": claim_key},
            source_route="tower_strict_battle_execute",
        )

        return {
            "idempotent_replay": False,
            "server_id": sid,
            "floor": floor_eff,
            "claim_source": TOWER_FLOOR_CLAIM_SOURCE,
            "claim_key": claim_key,
            "rewards": ledger_row["rewards"],
            "applied_at": now.isoformat(),
            "tower_progress_advanced": True,
            "catalog_floor": catalog_floor,
            "catalog_version": TOWER_CATALOG_VERSION,
            "daily_quest_event_bridge": dq_event,
            "reward_live_general": False,
            "premium_grant_blocked": True,
            "_slc_pack_103_tower_execute": True,
            "_slc_pack_103_tower_floor_completion_claim": True,
        }

    @router.get("/tower/strict/catalog")
    async def tower_strict_catalog():
        """Pack 102 — endpoint pubblico (auth-free) per il summary del catalog.

        Read-only: no DB access, no mutation. Contenuto identico per ogni client.
        """
        return {
            "catalog": _tower_catalog_summary(),
            "reward_live_general": False,
            "tower_reward_live_grant": False,
            "release_readiness_claimed": False,
            "_slc_pack_102_catalog_summary": True,
        }

    @router.get("/tower/strict/catalog/floor/{floor}")
    async def tower_strict_catalog_floor(floor: int):
        """Pack 102 — endpoint pubblico (auth-free) per il dettaglio di un floor.

        Read-only: solo legge dal catalog statico. Validazione range 1..TOTAL_LAUNCH_FLOORS.
        """
        try:
            f_int = int(floor)
        except Exception:
            raise HTTPException(422, detail={"blocker": "INVALID_FLOOR"})
        if f_int < 1 or f_int > TOTAL_LAUNCH_FLOORS:
            raise HTTPException(404, detail={
                "blocker": "FLOOR_OUT_OF_CATALOG_RANGE",
                "floor": f_int,
                "catalog_total_launch_floors": TOTAL_LAUNCH_FLOORS,
            })
        cf = _tower_catalog_floor(f_int)
        if cf is None:
            raise HTTPException(404, detail={
                "blocker": "FLOOR_NOT_FOUND",
                "floor": f_int,
            })
        return {
            "catalog_floor": cf,
            "catalog_version": TOWER_CATALOG_VERSION,
            "content_identical_across_servers": True,
            "reward_live_general": False,
            "tower_reward_live_grant": False,
            "_slc_pack_102_catalog_floor": True,
        }
