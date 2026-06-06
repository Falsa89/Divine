"""v108_AUTHORITATIVE_PRE - Battle Instance Envelope preview endpoint.

PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_PRE_BATTLE_INSTANCE_STAGING_NO_REWARD_LIVE

POST /api/battle/instance/preview
---------------------------------
Endpoint authoritative-pre, SAFE.

Garanzie:
- nessuna scrittura DB;
- nessun reward / EXP / drop / progress;
- nessuna mutazione di inventario o currency;
- non chiama endpoint legacy mutanti;
- `authoritative_live=false` SEMPRE (anche se i flag `..._ENABLED` fossero true);
- blocca l'avvio se mancano: server_id, player_team_snapshot reale, enemy_source.

Codici di blocco esplicito (HTTP 400 / 423):
- BATTLE_INSTANCE_SERVER_REQUIRED
- BATTLE_INSTANCE_PLAYER_TEAM_REQUIRED
- BATTLE_INSTANCE_ENEMY_SOURCE_REQUIRED
- BATTLE_INSTANCE_REWARD_LIVE_FORBIDDEN
- BATTLE_INSTANCE_PROGRESS_LIVE_FORBIDDEN
"""
from __future__ import annotations

import os
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/battle", tags=["battle_instance_v108_authoritative_pre"])

PUBLIC_SYNC_TAG = (
    "PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_PRE_BATTLE_INSTANCE_STAGING_NO_REWARD_LIVE"
)

ALLOWED_MODES = {
    "story", "tower", "arena", "training", "boss", "raid",
    "event", "guild_war", "guild_raid", "world_boss",
}
ALLOWED_ENEMY_SOURCES = {
    "authored", "player_team", "bot_team", "boss",
    "training_preset", "event_preset",
}
# enemy source che NON sono accettati player-facing in modalita' non-QA
PLAYER_FACING_ENEMY_SOURCES = {"authored", "boss", "training_preset", "event_preset"}
QA_ONLY_ENEMY_SOURCES = {"player_team", "bot_team"}

ALLOWED_REWARD_POLICY = {"none", "preview"}
ALLOWED_PROGRESS_POLICY = {"none", "preview"}
ALLOWED_ENGINE_MODE = {"preview", "authoritative_pre"}

# Marker placeholder team che NON sono validi come player team reale.
FORBIDDEN_TEAM_MARKERS = {
    "PLAYER_SAFE_FALLBACK_TEAM",
    "FAKE_TEAM",
    "DEFAULT_TEAM",
    "DEMO_TEAM",
    "STUB_TEAM",
}

# Marker enemy placeholder/alpha che richiedono QA flag.
FORBIDDEN_ENEMY_MARKERS = {
    "PLACEHOLDER_ENEMY",
    "ALPHA_ENEMY",
    "STUB_ENEMY",
    "DEMO_ENEMY",
    "GENERATED_ENEMY_RANDOM",
}


class BattleInstancePreviewRequest(BaseModel):
    server_id: Optional[str] = None
    account_id: Optional[str] = None
    mode: str
    encounter_id: Optional[str] = Field(default=None)
    player_team_id: Optional[str] = None
    player_team_snapshot: List[Any] = Field(default_factory=list)
    enemy_source_type: Optional[str] = None
    enemy_source_id: Optional[str] = None
    enemy_team_snapshot: List[Any] = Field(default_factory=list)
    battle_engine_mode: str = "preview"
    reward_policy: str = "preview"
    progress_policy: str = "preview"
    idempotency_key: Optional[str] = None
    client_trace_id: Optional[str] = None
    qa_flag: bool = False


def _flag(name: str) -> bool:
    return (os.getenv(name, "") or "").lower() in {"true", "1", "yes", "on"}


def _block(code: str, http_status: int = 423, **extra) -> None:
    raise HTTPException(
        status_code=http_status,
        detail={
            "code": code,
            "sync_tag": PUBLIC_SYNC_TAG,
            **extra,
        },
    )


@router.post("/instance/preview")
def battle_instance_preview(payload: BattleInstancePreviewRequest) -> Dict[str, Any]:
    # 1) Validazione di forma minima
    if payload.mode not in ALLOWED_MODES:
        raise HTTPException(status_code=400, detail=f"invalid_mode: {payload.mode}")
    if payload.battle_engine_mode not in ALLOWED_ENGINE_MODE:
        raise HTTPException(
            status_code=400,
            detail=f"invalid_battle_engine_mode: {payload.battle_engine_mode}",
        )
    if payload.reward_policy not in ALLOWED_REWARD_POLICY:
        # In authoritative-pre NESSUNA reward live e' accettata.
        _block(
            "BATTLE_INSTANCE_REWARD_LIVE_FORBIDDEN",
            http_status=423,
            requested=payload.reward_policy,
            allowed=sorted(ALLOWED_REWARD_POLICY),
        )
    if payload.progress_policy not in ALLOWED_PROGRESS_POLICY:
        _block(
            "BATTLE_INSTANCE_PROGRESS_LIVE_FORBIDDEN",
            http_status=423,
            requested=payload.progress_policy,
            allowed=sorted(ALLOWED_PROGRESS_POLICY),
        )

    # 2) server_id obbligatorio (no PSP claim ma serve per scope futuro).
    if not payload.server_id or not str(payload.server_id).strip():
        _block(
            "BATTLE_INSTANCE_SERVER_REQUIRED",
            http_status=423,
            reason="server_id selezionato obbligatorio per istanziare battle preview.",
        )

    # 3) player_team_snapshot reale obbligatorio.
    snap = payload.player_team_snapshot or []
    if not isinstance(snap, list) or len(snap) == 0:
        _block(
            "BATTLE_INSTANCE_PLAYER_TEAM_REQUIRED",
            http_status=423,
            reason="player_team_snapshot reale (non vuoto) obbligatorio.",
        )
    # rifiuta marker fake/fallback
    snap_repr = " ".join(str(x) for x in snap).upper()
    for marker in FORBIDDEN_TEAM_MARKERS:
        if marker in snap_repr:
            _block(
                "BATTLE_INSTANCE_PLAYER_TEAM_REQUIRED",
                http_status=423,
                reason=f"player_team marker non valido come reale: {marker}",
            )

    # 4) enemy source obbligatorio + non placeholder/random player-facing.
    if not payload.enemy_source_type or not payload.enemy_source_id:
        _block(
            "BATTLE_INSTANCE_ENEMY_SOURCE_REQUIRED",
            http_status=423,
            reason="enemy_source_type ed enemy_source_id obbligatori.",
        )
    if payload.enemy_source_type not in ALLOWED_ENEMY_SOURCES:
        _block(
            "BATTLE_INSTANCE_ENEMY_SOURCE_REQUIRED",
            http_status=423,
            reason=f"enemy_source_type non valido: {payload.enemy_source_type}",
            allowed=sorted(ALLOWED_ENEMY_SOURCES),
        )
    enemy_id_upper = str(payload.enemy_source_id).upper()
    for marker in FORBIDDEN_ENEMY_MARKERS:
        if marker in enemy_id_upper and not payload.qa_flag:
            _block(
                "BATTLE_INSTANCE_ENEMY_SOURCE_REQUIRED",
                http_status=423,
                reason=f"enemy placeholder/random vietato player-facing: {marker} (richiede qa_flag).",
            )
    # In flusso player normale, accettiamo solo i source player-facing.
    if not payload.qa_flag and payload.enemy_source_type in QA_ONLY_ENEMY_SOURCES:
        _block(
            "BATTLE_INSTANCE_ENEMY_SOURCE_REQUIRED",
            http_status=423,
            reason=f"enemy_source_type {payload.enemy_source_type} ammesso solo con qa_flag=True.",
            allowed_player_facing=sorted(PLAYER_FACING_ENEMY_SOURCES),
        )

    # 5) Coerenza flag globali (lettura honest, NON attivata).
    reward_live = _flag("REWARD_LIVE_ENABLED")
    progress_live = _flag("PROGRESS_LIVE_ENABLED")
    authoritative_live_flag = _flag("BATTLE_LAUNCH_AUTHORITATIVE_ENABLED")
    server_scoped_runtime = _flag("SERVER_SCOPED_RUNTIME_ENABLED")

    # Anche se REWARD_LIVE_ENABLED fosse stato attivato per altro endpoint,
    # qui in authoritative-pre rifiutiamo sempre payload con reward live.
    if reward_live and payload.reward_policy not in ALLOWED_REWARD_POLICY:
        _block(
            "BATTLE_INSTANCE_REWARD_LIVE_FORBIDDEN",
            http_status=423,
            reason="REWARD_LIVE non ammesso in authoritative-pre.",
        )
    if progress_live and payload.progress_policy not in ALLOWED_PROGRESS_POLICY:
        _block(
            "BATTLE_INSTANCE_PROGRESS_LIVE_FORBIDDEN",
            http_status=423,
            reason="PROGRESS_LIVE non ammesso in authoritative-pre.",
        )

    # 6) Build envelope. authoritative_live e' SEMPRE false.
    instance_id = f"bi_{uuid.uuid4().hex[:24]}"
    envelope = {
        "schema_version": "battle_instance_envelope_v1",
        "sync_tag": PUBLIC_SYNC_TAG,
        "battle_instance_id": instance_id,
        "server_id": payload.server_id,
        "account_id": payload.account_id,
        "mode": payload.mode,
        "encounter_id": payload.encounter_id,
        "player_team_id": payload.player_team_id,
        "player_team_snapshot": list(payload.player_team_snapshot),
        "enemy_source_type": payload.enemy_source_type,
        "enemy_source_id": payload.enemy_source_id,
        "enemy_team_snapshot": list(payload.enemy_team_snapshot),
        "battle_engine_mode": payload.battle_engine_mode,
        "authoritative_live": False,
        "reward_policy": "preview",
        "progress_policy": "preview",
        "idempotency_key": payload.idempotency_key,
        "client_trace_id": payload.client_trace_id,
        "feature_flags_observed": {
            "BATTLE_LAUNCH_AUTHORITATIVE_ENABLED": authoritative_live_flag,
            "REWARD_LIVE_ENABLED": reward_live,
            "PROGRESS_LIVE_ENABLED": progress_live,
            "SERVER_SCOPED_RUNTIME_ENABLED": server_scoped_runtime,
        },
        "safety": {
            "db_writes_allowed": False,
            "db_writes_performed": 0,
            "reward_live_enabled": False,
            "progress_live_enabled": False,
            "reward_granted": False,
            "progress_written": False,
            "currency_mutated": False,
            "inventory_mutated": False,
            "server_filter_applied": False,
            "calls_legacy_mutating_endpoints": False,
        },
        "warnings": [
            "Battle instance in authoritative-pre staging.",
            "authoritative_live=false: nessun reward, nessun progress, nessuna scrittura DB.",
            "server_id parsed ma server_filter_applied=false (PSP non attivo).",
        ],
    }
    return envelope
