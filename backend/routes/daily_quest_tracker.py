"""Pack 99 — Daily Quest Runtime Tracker server-side.

Endpoints registrati:
  * GET  /api/daily-quest/tracker/health
  * GET  /api/daily-quest/progress?server_id=<sid>
  * POST /api/daily-quest/progress/complete?server_id=<sid>&quest_id=<qid>

Pack 99 SAFETY:
  * Kill switch dedicato `DAILY_QUEST_TRACKER_ENABLED` (default OFF).
  * Storage server-scoped su collection `daily_quest_progress` con
    chiave canonica `(user_id, server_id, quest_id, day_iso)` UTC e
    indice unico parziale `ux_user_server_quest_day_pack99`.
  * Completion endpoint test-only finche` non esiste un runtime di
    gameplay authoritative: richiede marker `pack_99_test_artifact=true`
    sull'utente.
  * Nessun reward grant lato tracker. Lo stato `completed` viene letto
    dal `daily_quest_claim` (Pack 98 refactor) per autorizzare il claim.
  * PSP obbligatoria su `server_id`. NO fallback s1.
  * `quest_id` whitelist identico a Pack 98:
    `daily_quest_1` / `daily_quest_2` / `daily_quest_3`.
"""
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Marker server-side per documenti emessi dal Pack 99 (utile per indici parziali
# e per il cleanup script).
TRACKER_KILL_SWITCH_ENV = "DAILY_QUEST_TRACKER_ENABLED"
TRACKER_COLLECTION = "daily_quest_progress"
TRACKER_UNIQUE_INDEX_NAME = "ux_user_server_quest_day_pack99"
TRACKER_MARKER_FIELD = "_slc_pack_99_tracker"
USER_TEST_MARKER = "pack_99_test_artifact"
QUEST_ID_WHITELIST = {"daily_quest_1", "daily_quest_2", "daily_quest_3"}
QUEST_STATES = ("not_started", "in_progress", "completed", "claimed")


def _truthy(v: Optional[str]) -> bool:
    return str(v or "false").strip().lower() in ("true", "1", "yes", "on")


def _tracker_on() -> bool:
    return _truthy(os.getenv(TRACKER_KILL_SWITCH_ENV))


def _today_iso(day_override: Optional[str] = None) -> str:
    """Restituisce la data canonica UTC (YYYY-MM-DD).

    `day_override` (test-only) accetta una stringa formattata YYYY-MM-DD
    per simulare giorni futuri/passati negli smoke E2E. Validata strettamente.
    """
    if day_override:
        try:
            datetime.strptime(day_override, "%Y-%m-%d")
        except Exception:
            raise HTTPException(400, detail={"blocker": "INVALID_DAY_OVERRIDE_FORMAT"})
        return day_override
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


async def ensure_daily_quest_tracker_indices(db) -> Dict[str, Any]:
    """Crea l'indice unico parziale per il tracker. Idempotente."""
    out: Dict[str, Any] = {"created": [], "stopped": False, "error": None}
    try:
        name = await db[TRACKER_COLLECTION].create_index(
            [("user_id", 1), ("server_id", 1),
             ("quest_id", 1), ("day_iso", 1)],
            unique=True,
            partialFilterExpression={TRACKER_MARKER_FIELD: True},
            name=TRACKER_UNIQUE_INDEX_NAME,
            background=True,
        )
        out["created"].append(name)
    except Exception as e:
        out["stopped"] = True
        out["error"] = repr(e)
    return out


async def get_quest_progress_state(db, user_id: str, server_id: str,
                                   quest_id: str,
                                   day_iso: Optional[str] = None
                                   ) -> Optional[Dict[str, Any]]:
    """Restituisce il documento di progress (o None) per la chiave canonica."""
    day = _today_iso(day_iso)
    return await db[TRACKER_COLLECTION].find_one({
        "user_id": user_id,
        "server_id": server_id,
        "quest_id": quest_id,
        "day_iso": day,
        TRACKER_MARKER_FIELD: True,
    })


async def is_quest_completed(db, user_id: str, server_id: str,
                             quest_id: str,
                             day_iso: Optional[str] = None) -> bool:
    """Helper consumato dal `daily_quest_claim` per autorizzare il claim."""
    doc = await get_quest_progress_state(db, user_id, server_id, quest_id, day_iso)
    if not doc:
        return False
    return doc.get("state") in ("completed", "claimed")


async def mark_quest_claimed(db, user_id: str, server_id: str,
                             quest_id: str,
                             day_iso: Optional[str] = None) -> Dict[str, Any]:
    """Transizione da `completed` a `claimed` post-grant.

    Idempotent: se lo stato e' gia` `claimed` non rilancia errore.
    Ritorna il documento aggiornato (post-update).
    """
    day = _today_iso(day_iso)
    now = datetime.utcnow()
    await db[TRACKER_COLLECTION].update_one(
        {
            "user_id": user_id,
            "server_id": server_id,
            "quest_id": quest_id,
            "day_iso": day,
            TRACKER_MARKER_FIELD: True,
        },
        {"$set": {"state": "claimed", "claimed_at": now,
                  "_slc_pack_99_claim_transition": True}},
        upsert=False,
    )
    return await get_quest_progress_state(db, user_id, server_id, quest_id, day) or {}


class CompleteRequest(BaseModel):
    # Pack 99: il payload e` ignorato lato reward, qui esiste solo per simmetria
    # con eventuali metadata di gameplay futuri (es. score finale, replay seed).
    # NESSUN campo qui influenza il reward o la transizione di stato.
    note: Optional[str] = None
    _test_day_override: Optional[str] = None


def register_daily_quest_tracker_routes(router, db, get_current_user,
                                        *_a, **_kw):

    @router.get("/daily-quest/tracker/health")
    async def daily_quest_tracker_health():
        return {
            "endpoint_group": "/api/daily-quest/progress",
            "kill_switch_env": TRACKER_KILL_SWITCH_ENV,
            "kill_switch_live_enabled": _tracker_on(),
            "completion_endpoint_test_only_until_real_gameplay": True,
            "completion_endpoint_marker_required": USER_TEST_MARKER,
            "states": list(QUEST_STATES),
            "quest_id_whitelist": sorted(QUEST_ID_WHITELIST),
            "collection": TRACKER_COLLECTION,
            "unique_index": TRACKER_UNIQUE_INDEX_NAME,
            "pack_origin": "pack_99",
            "release_readiness_claimed": False,
            "reward_live_general": False,
            "no_reward_grant_on_completion": True,
            "claim_gate_blocker_when_not_completed": "DAILY_QUEST_COMPLETION_REQUIRED",
        }

    @router.post("/daily-quest/tracker/preflight")
    async def daily_quest_tracker_preflight(
        current_user: dict = Depends(get_current_user),
    ):
        idx = await ensure_daily_quest_tracker_indices(db)
        return {
            "kill_switch_on": _tracker_on(),
            "indices": idx,
            "quest_id_whitelist": sorted(QUEST_ID_WHITELIST),
            "_slc_pack_99_tracker_preflight": True,
        }

    @router.get("/daily-quest/progress")
    async def daily_quest_progress_get(
        server_id: str = None,
        _test_day_override: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]

        # 1. server_id obbligatorio (no fallback s1)
        if not server_id or not isinstance(server_id, str) or not server_id.strip():
            raise HTTPException(400, detail={"blocker": "SERVER_ID_REQUIRED"})
        sid = server_id.strip()

        # 2. PSP server-scoped obbligatoria
        psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
        if not psp:
            raise HTTPException(409, detail={
                "blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
                "server_id": sid,
            })

        # 3. Day override opzionale, validato (test-only marker richiesto per usarlo)
        user_doc = await db.users.find_one({"id": uid})
        is_marked = bool(user_doc and user_doc.get(USER_TEST_MARKER))
        day_override = None
        if _test_day_override:
            if not is_marked:
                raise HTTPException(403, detail={
                    "blocker": "DAY_OVERRIDE_FORBIDDEN_FOR_NON_TEST_USER",
                })
            day_override = _test_day_override.strip()
        day = _today_iso(day_override)

        # 4. Lookup progress per ogni quest in whitelist (no insert)
        rows: List[Dict[str, Any]] = []
        cursor = db[TRACKER_COLLECTION].find({
            "user_id": uid,
            "server_id": sid,
            "day_iso": day,
            TRACKER_MARKER_FIELD: True,
        })
        async for doc in cursor:
            rows.append(doc)

        by_quest: Dict[str, Dict[str, Any]] = {}
        for d in rows:
            qid = d.get("quest_id")
            if qid in QUEST_ID_WHITELIST:
                by_quest[qid] = d

        progress: List[Dict[str, Any]] = []
        for qid in sorted(QUEST_ID_WHITELIST):
            doc = by_quest.get(qid)
            if doc:
                progress.append({
                    "quest_id": qid,
                    "state": doc.get("state", "not_started"),
                    "completed_at": (doc.get("completed_at").isoformat()
                                     if doc.get("completed_at") else None),
                    "claimed_at": (doc.get("claimed_at").isoformat()
                                   if doc.get("claimed_at") else None),
                })
            else:
                progress.append({
                    "quest_id": qid,
                    "state": "not_started",
                    "completed_at": None,
                    "claimed_at": None,
                })

        return {
            "server_id": sid,
            "day_iso": day,
            "progress": progress,
            "tracker_kill_switch_on": _tracker_on(),
            "completion_endpoint_test_only_until_real_gameplay": True,
            "_slc_pack_99_tracker_progress_get": True,
            "release_readiness_claimed": False,
            "reward_live_general": False,
        }

    @router.post("/daily-quest/progress/complete")
    async def daily_quest_progress_complete(
        req: Optional[CompleteRequest] = None,
        server_id: str = None,
        quest_id: str = None,
        _test_day_override: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]

        # 1. Kill switch dedicato (default OFF)
        if not _tracker_on():
            raise HTTPException(503, detail={
                "blocker": "DAILY_QUEST_TRACKER_DISABLED",
                "kill_switch_env": TRACKER_KILL_SWITCH_ENV,
            })

        # 2. server_id obbligatorio
        if not server_id or not isinstance(server_id, str) or not server_id.strip():
            raise HTTPException(400, detail={"blocker": "SERVER_ID_REQUIRED"})
        sid = server_id.strip()

        # 3. quest_id + whitelist
        if not quest_id or not isinstance(quest_id, str) or not quest_id.strip():
            raise HTTPException(400, detail={"blocker": "QUEST_ID_REQUIRED"})
        qid = quest_id.strip()
        if qid not in QUEST_ID_WHITELIST:
            raise HTTPException(422, detail={
                "blocker": "QUEST_ID_NOT_WHITELISTED",
                "quest_id": qid,
                "allowlist": sorted(QUEST_ID_WHITELIST),
            })

        # 4. PSP obbligatoria
        psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
        if not psp:
            raise HTTPException(409, detail={
                "blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
                "server_id": sid,
            })

        # 5. Test marker obbligatorio finche` non esiste gameplay reale.
        # NO real user puo` invocare l'endpoint di completion ad oggi.
        user_doc = await db.users.find_one({"id": uid})
        is_marked = bool(user_doc and user_doc.get(USER_TEST_MARKER))
        if not is_marked:
            raise HTTPException(403, detail={
                "blocker": "COMPLETION_ENDPOINT_TEST_ONLY",
                "reason": (
                    "Pack 99 non ha ancora un runtime di gameplay reale per le daily "
                    "quest. L'endpoint di completion serve esclusivamente agli smoke "
                    "E2E test-only marcati `pack_99_test_artifact=true`. I real player "
                    "ricevono il bypass solo quando il gameplay diventa authoritative."
                ),
                "marker_required": USER_TEST_MARKER,
            })

        # 6. Day override (test-only, marker gia` verificato sopra)
        day_override = None
        if _test_day_override:
            day_override = _test_day_override.strip()
        day = _today_iso(day_override)

        # 7. Upsert idempotente: se gia` completed/claimed non sovrascrive timestamp
        now = datetime.utcnow()
        existing = await db[TRACKER_COLLECTION].find_one({
            "user_id": uid, "server_id": sid,
            "quest_id": qid, "day_iso": day,
            TRACKER_MARKER_FIELD: True,
        })
        if existing and existing.get("state") in ("completed", "claimed"):
            existing.pop("_id", None)
            # Normalizza datetimes per JSON
            for k in ("completed_at", "claimed_at", "created_at", "updated_at"):
                v = existing.get(k)
                if hasattr(v, "isoformat"):
                    existing[k] = v.isoformat()
            return {
                "idempotent_replay": True,
                "server_id": sid,
                "quest_id": qid,
                "day_iso": day,
                "state": existing.get("state"),
                "progress": existing,
                "no_reward_grant_on_completion": True,
                "reward_live_general": False,
                "_slc_pack_99_tracker_complete_idempotent": True,
            }

        # 8. Insert/upsert nuovo documento `completed`.
        # Usiamo update_one + upsert con $setOnInsert per evitare race su created_at.
        await db[TRACKER_COLLECTION].update_one(
            {
                "user_id": uid, "server_id": sid,
                "quest_id": qid, "day_iso": day,
                TRACKER_MARKER_FIELD: True,
            },
            {
                "$set": {
                    "state": "completed",
                    "completed_at": now,
                    "updated_at": now,
                    "_slc_pack_99_completion_via_test_marker": True,
                },
                "$setOnInsert": {
                    "user_id": uid,
                    "server_id": sid,
                    "quest_id": qid,
                    "day_iso": day,
                    "created_at": now,
                    TRACKER_MARKER_FIELD: True,
                },
            },
            upsert=True,
        )

        doc = await db[TRACKER_COLLECTION].find_one({
            "user_id": uid, "server_id": sid,
            "quest_id": qid, "day_iso": day,
            TRACKER_MARKER_FIELD: True,
        }) or {}
        doc.pop("_id", None)
        for k in ("completed_at", "claimed_at", "created_at", "updated_at"):
            v = doc.get(k)
            if hasattr(v, "isoformat"):
                doc[k] = v.isoformat()

        return {
            "idempotent_replay": False,
            "server_id": sid,
            "quest_id": qid,
            "day_iso": day,
            "state": "completed",
            "progress": doc,
            "no_reward_grant_on_completion": True,
            "reward_live_general": False,
            "_slc_pack_99_tracker_complete": True,
        }
