"""v108_AUTHORITATIVE_RUNTIME - Battle Result Envelope resolve-preview endpoint.

PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_BATTLE_RUNTIME_STAGING_NO_REWARD_LIVE

POST /api/battle/instance/resolve-preview
-----------------------------------------
Endpoint authoritative-staging, SAFE.

Garanzie:
- nessuna scrittura DB;
- nessun reward / EXP / drop / progress / affinity;
- nessuna mutazione di inventario o currency;
- NON chiama l'endpoint legacy simulate ne' endpoint legacy mutanti;
- authoritative_live=false SEMPRE, authoritative_staging=true;
- resolver deterministico in-memory: nessun rewrite del battle_engine.
"""
from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/battle", tags=["battle_runtime_v108_authoritative_staging"])

PUBLIC_SYNC_TAG = (
    "PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_BATTLE_RUNTIME_STAGING_NO_REWARD_LIVE"
)

ALLOWED_MODES = {
    "story","tower","arena","training","boss","raid","event",
    "guild_war","guild_raid","world_boss",
}
ALLOWED_ENEMY_SOURCES = {
    "authored","player_team","bot_team","boss","training_preset","event_preset",
}
PLAYER_FACING_ENEMY_SOURCES = {"authored","boss","training_preset","event_preset"}
QA_ONLY_ENEMY_SOURCES = {"player_team","bot_team"}

FORBIDDEN_TEAM_MARKERS = {
    "PLAYER_SAFE_FALLBACK_TEAM","FAKE_TEAM","DEFAULT_TEAM","DEMO_TEAM",
    "STUB_TEAM","MOCK_TEAM","FALLBACK_TEAM",
}
FORBIDDEN_ENEMY_MARKERS = {
    "PLACEHOLDER_ENEMY","ALPHA_ENEMY","STUB_ENEMY","DEMO_ENEMY",
    "GENERATED_ENEMY_RANDOM","MOCK_ENEMY",
}


class BattleInstanceInput(BaseModel):
    schema_version: Optional[str] = None
    battle_instance_id: Optional[str] = None
    server_id: Optional[str] = None
    account_id: Optional[str] = None
    mode: Optional[str] = None
    encounter_id: Optional[str] = None
    player_team_id: Optional[str] = None
    player_team_snapshot: List[Any] = Field(default_factory=list)
    enemy_source_type: Optional[str] = None
    enemy_source_id: Optional[str] = None
    enemy_team_snapshot: List[Any] = Field(default_factory=list)
    battle_engine_mode: Optional[str] = None
    authoritative_live: Optional[bool] = None
    reward_policy: Optional[str] = None
    progress_policy: Optional[str] = None
    idempotency_key: Optional[str] = None
    client_trace_id: Optional[str] = None


class ResolvePreviewRequest(BaseModel):
    battle_instance: Optional[BattleInstanceInput] = None
    # alternative: campi piatti come per /preview
    server_id: Optional[str] = None
    mode: Optional[str] = None
    encounter_id: Optional[str] = None
    player_team_snapshot: Optional[List[Any]] = None
    enemy_source_type: Optional[str] = None
    enemy_source_id: Optional[str] = None
    enemy_team_snapshot: Optional[List[Any]] = None
    reward_policy: Optional[str] = None
    progress_policy: Optional[str] = None
    authoritative_live: Optional[bool] = None
    battle_instance_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    client_trace_id: Optional[str] = None
    qa_flag: bool = False


def _flag(name: str) -> bool:
    return (os.getenv(name, "") or "").lower() in {"true","1","yes","on"}


def _block(code: str, http_status: int = 423, **extra) -> None:
    raise HTTPException(
        status_code=http_status,
        detail={"code": code, "sync_tag": PUBLIC_SYNC_TAG, **extra},
    )


def _flat(req: ResolvePreviewRequest) -> Dict[str, Any]:
    """Merge battle_instance + flat fields. flat fields hanno precedenza solo se non-None."""
    bi = req.battle_instance.model_dump() if req.battle_instance else {}
    out = dict(bi)
    for k in (
        "server_id","mode","encounter_id","player_team_snapshot",
        "enemy_source_type","enemy_source_id","enemy_team_snapshot",
        "reward_policy","progress_policy","authoritative_live",
        "battle_instance_id","idempotency_key","client_trace_id",
    ):
        v = getattr(req, k, None)
        if v is not None:
            out[k] = v
    return out


@router.post("/instance/resolve-preview")
def battle_instance_resolve_preview(req: ResolvePreviewRequest) -> Dict[str, Any]:
    data = _flat(req)

    # 1) battle_instance richiesto (id o campi minimi)
    if not data.get("battle_instance_id") and not (data.get("mode") and data.get("server_id")):
        _block("BATTLE_RESULT_INSTANCE_REQUIRED", reason="battle_instance mancante o senza identita' minima.")

    # 2) authoritative_live=true rifiutato
    if data.get("authoritative_live") is True:
        _block("BATTLE_RESULT_AUTHORITATIVE_LIVE_FORBIDDEN",
               reason="authoritative_live=true non ammesso in staging.")

    # 3) reward_policy/progress_policy live rifiutati
    if (data.get("reward_policy") or "preview") not in {"none","preview"}:
        _block("BATTLE_RESULT_REWARD_LIVE_FORBIDDEN",
               requested=data.get("reward_policy"), allowed=["none","preview"])
    if (data.get("progress_policy") or "preview") not in {"none","preview"}:
        _block("BATTLE_RESULT_PROGRESS_LIVE_FORBIDDEN",
               requested=data.get("progress_policy"), allowed=["none","preview"])

    # 4) mode richiesto e valido
    mode = data.get("mode") or ""
    if mode not in ALLOWED_MODES:
        raise HTTPException(status_code=400, detail=f"invalid_mode: {mode}")

    # 5) server_id richiesto
    if not data.get("server_id") or not str(data["server_id"]).strip():
        _block("BATTLE_RESULT_INSTANCE_REQUIRED",
               reason="server_id obbligatorio per staging resolve.")

    # 6) player team
    pt = data.get("player_team_snapshot") or []
    if not isinstance(pt, list) or len(pt) == 0:
        _block("BATTLE_RESULT_PLAYER_TEAM_REQUIRED",
               reason="player_team_snapshot reale (non vuoto) obbligatorio.")
    pt_repr = " ".join(str(x) for x in pt).upper()
    for m in FORBIDDEN_TEAM_MARKERS:
        if m in pt_repr:
            _block("BATTLE_RESULT_PLAYER_TEAM_REQUIRED",
                   reason=f"player team marker non valido: {m}")
    full_6 = (len(pt) == 6)

    # 7) enemy
    es_type = data.get("enemy_source_type")
    es_id = data.get("enemy_source_id")
    if not es_type or not es_id:
        _block("BATTLE_RESULT_ENEMY_TEAM_REQUIRED",
               reason="enemy_source_type ed enemy_source_id obbligatori.")
    if es_type not in ALLOWED_ENEMY_SOURCES:
        _block("BATTLE_RESULT_ENEMY_TEAM_REQUIRED",
               reason=f"enemy_source_type non valido: {es_type}")
    qa_flag = bool(getattr(req, "qa_flag", False))
    es_id_upper = str(es_id).upper()
    for m in FORBIDDEN_ENEMY_MARKERS:
        if m in es_id_upper and not qa_flag:
            _block("BATTLE_RESULT_ENEMY_TEAM_REQUIRED",
                   reason=f"enemy marker non valido (richiede qa_flag): {m}")
    if es_type in QA_ONLY_ENEMY_SOURCES and not qa_flag:
        _block("BATTLE_RESULT_ENEMY_TEAM_REQUIRED",
               reason=f"enemy_source_type {es_type} ammesso solo con qa_flag.")
    # enemy team: per boss singolo accettiamo enemy_team_snapshot vuoto se source=boss
    en = data.get("enemy_team_snapshot") or []
    if es_type != "boss" and (not isinstance(en, list) or len(en) == 0):
        _block("BATTLE_RESULT_ENEMY_TEAM_REQUIRED",
               reason="enemy_team_snapshot vuoto (richiesto per source non-boss).")

    # 8) hard guard: NESSUNA chiamata all'endpoint legacy simulate in questo codepath.
    # (Statico: il codice non importa simulate; runtime non lo invoca.)

    # 9) Resolver deterministico SEMPLIFICATO (NO battle_engine formula rewrite).
    # winner determinato da hash stabile (battle_instance_id + mode), nessun calcolo
    # di stat reali, nessun reward.
    seed_source = (
        str(data.get("battle_instance_id") or "") + "|" +
        str(data.get("encounter_id") or "") + "|" +
        mode + "|" + str(data.get("server_id"))
    )
    h = hashlib.sha256(seed_source.encode("utf-8")).hexdigest()
    seed_int = int(h[:8], 16)
    # Skew leggero verso player se team_full=6 (decisione di design, non formula di battaglia).
    bias = 0.55 if full_6 else 0.50
    winner = "player" if (seed_int % 1000) / 1000.0 < bias else "enemy"
    turns_total = (seed_int % 7) + 3  # 3..9

    turn_log = [
        {
            "turn": t + 1,
            "actor": "player" if t % 2 == 0 else "enemy",
            "action": "deterministic_staging_action",
            "preview_only": True,
        }
        for t in range(turns_total)
    ]

    player_team_result = {
        "size": len(pt),
        "full_6_slot": full_6,
        "alive_count": len(pt) if winner == "player" else max(0, len(pt) - 1),
        "preview_only": True,
        "exp_granted": 0,
        "drops_granted": 0,
        "affinity_granted": 0,
    }
    enemy_team_result = {
        "size": len(en) if en else 1,
        "alive_count": 0 if winner == "player" else (len(en) if en else 1),
        "preview_only": True,
    }

    reward_live = _flag("REWARD_LIVE_ENABLED")
    progress_live = _flag("PROGRESS_LIVE_ENABLED")
    auth_live_flag = _flag("BATTLE_LAUNCH_AUTHORITATIVE_ENABLED")
    server_scoped_flag = _flag("SERVER_SCOPED_RUNTIME_ENABLED")

    envelope = {
        "schema_version": "battle_result_envelope_v1",
        "sync_tag": PUBLIC_SYNC_TAG,
        "battle_instance_id": data.get("battle_instance_id"),
        "server_id": data.get("server_id"),
        "account_id": data.get("account_id"),
        "mode": mode,
        "encounter_id": data.get("encounter_id"),
        "authoritative_live": False,
        "authoritative_staging": True,
        "battle_engine_mode": "authoritative_staging",
        "winner": winner,
        "turn_log": turn_log,
        "player_team_result": player_team_result,
        "enemy_team_result": enemy_team_result,
        "reward_policy": "preview",
        "progress_policy": "preview",
        "rewards": {
            "granted": False,
            "preview_only": True,
            "exp": 0,
            "gold": 0,
            "gems": 0,
            "drops": [],
            "affinity": 0,
        },
        "progress": {
            "written": False,
            "preview_only": True,
            "story_node_advanced": False,
            "tower_floor_advanced": False,
            "event_progress": 0,
        },
        "idempotency_key": data.get("idempotency_key"),
        "client_trace_id": data.get("client_trace_id"),
        "feature_flags_observed": {
            "BATTLE_LAUNCH_AUTHORITATIVE_ENABLED": auth_live_flag,
            "REWARD_LIVE_ENABLED": reward_live,
            "PROGRESS_LIVE_ENABLED": progress_live,
            "SERVER_SCOPED_RUNTIME_ENABLED": server_scoped_flag,
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
            "user_heroes_exp_mutated": False,
            "battle_pass_mutated": False,
            "vip_mutated": False,
            "soul_forge_mutated": False,
            "equipment_mutated": False,
            "server_filter_applied": False,
            "calls_legacy_mutating_endpoints": False,
            "calls_battle_simulate_endpoint": False,
            "battle_engine_formula_rewritten": False,
        },
        "warnings": [
            "Battle result in authoritative-staging.",
            "authoritative_live=false: nessun reward, nessun progress, nessuna scrittura DB.",
            "Resolver semplificato deterministico in-memory: NON rewrite del battle_engine.",
            "server_id parsed ma server_filter_applied=false (PSP non attivo).",
        ],
    }
    return envelope
