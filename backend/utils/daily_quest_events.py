"""Pack 100 — Daily Quest Gameplay Event Bus / Tracker Bridge.

Helper interno (NON un endpoint) consumato dalle route gameplay server-authoritative
che vogliono dichiarare il completamento di una daily quest dopo un'azione safe.

API principale:

  await record_daily_quest_event(
      db, user_id, server_id, event_type, payload, source_route, day_iso=None,
  )

Responsabilita`:

  * Validare PSP per (user_id, server_id). NO fallback `s1`.
  * Validare `event_type` contro `DAILY_QUEST_EVENT_ALLOWLIST` con mapping verso un
    `quest_id` whitelisted in Pack 99.
  * Scrivere ESCLUSIVAMENTE sulla collection `daily_quest_progress` (Pack 99)
    impostando `state=completed` + audit fields.
  * NESSUN reward grant. NESSUN ledger write. NESSUNA mutation di `users.*` o
    `psp.soft_currencies`.
  * Idempotente: replay stesso (user, server, quest, day) → nessun upsert effetto,
    `idempotent_replay=True`.
  * Marcatura full audit con `_slc_pack_100_event_bridge=True` su ogni transizione
    e con campi `event_type`, `source_route`, `event_at`.

La funzione e` `safe-by-default`: se il kill switch tracker e` OFF, l'evento NON
viene applicato (no-op) ma viene loggato come `skipped_tracker_disabled=True`. Non
impedisce il flusso del chiamante (es. daily_login_claim resta a buon fine anche
se il tracker e` OFF).
"""
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from routes.daily_quest_tracker import (
    TRACKER_COLLECTION,
    TRACKER_KILL_SWITCH_ENV,
    TRACKER_MARKER_FIELD,
    QUEST_ID_WHITELIST,
    _today_iso,
)

# Mapping canonico Pack 100 event_type -> quest_id.
# Solo eventi server-authoritative e già server-scoped sono ammessi qui.
# Aggiungere una nuova entry SOLO se la route emittente è stata sottoposta a
# audit server-scope (Pack 100 SOT, doc 120).
DAILY_QUEST_EVENT_ALLOWLIST: Dict[str, str] = {
    # Pack 100 first real mapping: daily login claim success -> daily_quest_1.
    "daily_login_claim_success": "daily_quest_1",
    # Pack 103 second real mapping: tower floor clear success -> daily_quest_2.
    # Solo eventi server-authoritative dal /api/tower/strict/battle/execute.
    "tower_floor_clear_success": "daily_quest_2",
}

# Source routes ammesse per ogni event_type. Una source route diversa rifiuta l'event.
DAILY_QUEST_EVENT_SOURCE_ALLOWLIST: Dict[str, set] = {
    "daily_login_claim_success": {"daily_login_claim"},
    "tower_floor_clear_success": {"tower_strict_battle_execute"},
}

EVENT_BRIDGE_MARKER = "_slc_pack_100_event_bridge"


def _truthy(v: Optional[str]) -> bool:
    return str(v or "false").strip().lower() in ("true", "1", "yes", "on")


def _tracker_on() -> bool:
    return _truthy(os.getenv(TRACKER_KILL_SWITCH_ENV))


async def record_daily_quest_event(
    db,
    user_id: str,
    server_id: str,
    event_type: str,
    payload: Optional[Dict[str, Any]] = None,
    source_route: Optional[str] = None,
    day_iso: Optional[str] = None,
) -> Dict[str, Any]:
    """Registra un evento gameplay e aggiorna il tracker daily quest.

    NON solleva HTTPException. Restituisce un dict descrittivo che il chiamante
    puo` includere nella response di audit (es. daily_login_claim risponde gia`
    al client; aggiungiamo `daily_quest_event_bridge` come campo informativo).

    Pre-condizioni di sicurezza:
      * `user_id` e `server_id` stringhe non vuote.
      * `event_type` in DAILY_QUEST_EVENT_ALLOWLIST.
      * `source_route` in DAILY_QUEST_EVENT_SOURCE_ALLOWLIST[event_type].
      * PSP esistente per (user_id, server_id).
      * Kill switch tracker ON.

    NESSUN reward grant. NESSUNA scrittura su users/inventory/wallets.
    """
    out: Dict[str, Any] = {
        "event_type": event_type,
        "source_route": source_route,
        "server_id": server_id,
        "quest_id": None,
        "applied": False,
        "idempotent_replay": False,
        "skipped_reason": None,
        EVENT_BRIDGE_MARKER: True,
    }

    # 1. Input validation (soft fail: nessuna eccezione)
    if not user_id or not server_id or not isinstance(server_id, str):
        out["skipped_reason"] = "INVALID_SCOPE"
        return out
    sid = server_id.strip()
    if not sid:
        out["skipped_reason"] = "INVALID_SCOPE"
        return out

    # 2. Event type / source allowlist enforcement
    quest_id = DAILY_QUEST_EVENT_ALLOWLIST.get(event_type)
    if not quest_id or quest_id not in QUEST_ID_WHITELIST:
        out["skipped_reason"] = "EVENT_TYPE_NOT_ALLOWLISTED"
        return out
    allowed_sources = DAILY_QUEST_EVENT_SOURCE_ALLOWLIST.get(event_type) or set()
    if source_route not in allowed_sources:
        out["skipped_reason"] = "SOURCE_ROUTE_NOT_ALLOWLISTED"
        return out
    out["quest_id"] = quest_id

    # 3. Kill switch tracker
    if not _tracker_on():
        out["skipped_reason"] = "TRACKER_KILL_SWITCH_OFF"
        return out

    # 4. PSP server-scoped check
    psp = await db.player_server_profiles.find_one({"user_id": user_id, "server_id": sid})
    if not psp:
        out["skipped_reason"] = "PLAYER_SERVER_PROFILE_REQUIRED"
        return out

    # 5. Day canonical (UTC)
    day = _today_iso(day_iso)
    now = datetime.utcnow()

    # 6. Upsert idempotente sul tracker. Se già completed/claimed: replay.
    existing = await db[TRACKER_COLLECTION].find_one({
        "user_id": user_id, "server_id": sid,
        "quest_id": quest_id, "day_iso": day,
        TRACKER_MARKER_FIELD: True,
    })
    if existing and existing.get("state") in ("completed", "claimed"):
        out["applied"] = True
        out["idempotent_replay"] = True
        out["day_iso"] = day
        out["state"] = existing.get("state")
        return out

    # 7. Insert/upsert state=completed via event bridge
    await db[TRACKER_COLLECTION].update_one(
        {
            "user_id": user_id, "server_id": sid,
            "quest_id": quest_id, "day_iso": day,
            TRACKER_MARKER_FIELD: True,
        },
        {
            "$set": {
                "state": "completed",
                "completed_at": now,
                "updated_at": now,
                "event_type": event_type,
                "source_route": source_route,
                EVENT_BRIDGE_MARKER: True,
                "_slc_pack_100_completion_via_event_bridge": True,
            },
            "$setOnInsert": {
                "user_id": user_id,
                "server_id": sid,
                "quest_id": quest_id,
                "day_iso": day,
                "created_at": now,
                TRACKER_MARKER_FIELD: True,
            },
        },
        upsert=True,
    )
    out["applied"] = True
    out["day_iso"] = day
    out["state"] = "completed"
    return out


def list_event_mapping() -> Dict[str, str]:
    """Snapshot pubblico del mapping (per health/debug endpoints)."""
    return dict(DAILY_QUEST_EVENT_ALLOWLIST)
