"""v107A — Battle Launch Contract router.

Mounts:
  POST /api/battle/launch

Default behavior (BATTLE_LAUNCH_AUTHORITATIVE_ENABLED unset/false):
  - Validate Battle Launch Contract v1 payload (shape only).
  - Return preview/non-authoritative echo with explicit warning.
  - NO DB writes.
  - NO reward grant.
  - NO progress write.
  - NO currency mutation.
  - NO server_id-bound filtering (PSP not applied).

When flag set to true AND PSP isolation live:
  - This endpoint is still gated; the actual authoritative engine path is
    deferred to v108. Today, even with flag on, we ONLY echo, never mutate.

Safety:
  - reward_policy and progress_policy enforced as 'none' or 'preview' unless
    REWARD_LIVE_ENABLED / PROGRESS_LIVE_ENABLED are explicitly true.
  - server_id is parsed but used only for echo and audit trail.
  - idempotency_key is required for live_gated/live; absent => preview only.
"""
import os
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/battle", tags=["battle_launch_v107a"])

ALLOWED_MODES = {
    "story", "tower", "arena", "training", "boss", "raid",
    "event", "guild_war", "guild_raid", "world_boss",
}
ALLOWED_ENEMY_SOURCES = {
    "authored", "player_team", "bot_team", "boss",
    "training_preset", "event_preset",
}
ALLOWED_REWARD_POLICY = {"none", "preview", "live_gated", "live"}
ALLOWED_PROGRESS_POLICY = {"none", "preview", "live_gated", "live"}
ALLOWED_ENGINE_MODE = {"preview", "authoritative"}


class BattleLaunchContractV1(BaseModel):
    server_id: str = Field(..., min_length=1)
    mode: str
    encounter_id: str = Field(..., min_length=1)
    player_team_id: Optional[str] = None
    player_team_snapshot: List[Any] = Field(default_factory=list)
    enemy_source_type: str
    enemy_source_id: str = Field(..., min_length=1)
    reward_policy: str = "none"
    progress_policy: str = "none"
    battle_engine_mode: str = "preview"
    idempotency_key: Optional[str] = None
    client_trace_id: Optional[str] = None


def _flag(name: str) -> bool:
    return (os.getenv(name, "") or "").lower() == "true"


@router.post("/launch")
def battle_launch(payload: BattleLaunchContractV1) -> Dict[str, Any]:
    # Shape validation
    if payload.mode not in ALLOWED_MODES:
        raise HTTPException(status_code=400, detail=f"invalid_mode: {payload.mode}")
    if payload.enemy_source_type not in ALLOWED_ENEMY_SOURCES:
        raise HTTPException(status_code=400, detail=f"invalid_enemy_source_type: {payload.enemy_source_type}")
    if payload.reward_policy not in ALLOWED_REWARD_POLICY:
        raise HTTPException(status_code=400, detail=f"invalid_reward_policy: {payload.reward_policy}")
    if payload.progress_policy not in ALLOWED_PROGRESS_POLICY:
        raise HTTPException(status_code=400, detail=f"invalid_progress_policy: {payload.progress_policy}")
    if payload.battle_engine_mode not in ALLOWED_ENGINE_MODE:
        raise HTTPException(status_code=400, detail=f"invalid_battle_engine_mode: {payload.battle_engine_mode}")

    # Feature flag state
    authoritative_enabled = _flag("BATTLE_LAUNCH_AUTHORITATIVE_ENABLED")
    reward_live_enabled = _flag("REWARD_LIVE_ENABLED")
    progress_live_enabled = _flag("PROGRESS_LIVE_ENABLED")
    server_scoped_enabled = _flag("SERVER_SCOPED_RUNTIME_ENABLED")

    # Coerce live policies down to preview when flags are not enabled (HONEST)
    coerced_reward_policy = payload.reward_policy
    coerced_progress_policy = payload.progress_policy
    coerced_engine_mode = payload.battle_engine_mode
    coercions: List[str] = []
    if coerced_reward_policy in ("live_gated", "live") and not reward_live_enabled:
        coerced_reward_policy = "preview"
        coercions.append("reward_policy_coerced_to_preview_flag_off")
    if coerced_progress_policy in ("live_gated", "live") and not progress_live_enabled:
        coerced_progress_policy = "preview"
        coercions.append("progress_policy_coerced_to_preview_flag_off")
    if coerced_engine_mode == "authoritative" and not authoritative_enabled:
        coerced_engine_mode = "preview"
        coercions.append("battle_engine_mode_coerced_to_preview_flag_off")

    # Idempotency requirement for live_gated/live
    requires_idempotency = (
        coerced_reward_policy in ("live_gated", "live")
        or coerced_progress_policy in ("live_gated", "live")
    )
    if requires_idempotency and not payload.idempotency_key:
        raise HTTPException(status_code=400, detail="idempotency_key_required_for_live_gated_or_live")

    # Build echo (no DB writes)
    return {
        "contract_version": "battle_launch_contract_v1",
        "status": "PREVIEW_ECHO_NON_AUTHORITATIVE",
        "echoed_payload": payload.model_dump(),
        "coerced_policy": {
            "reward_policy": coerced_reward_policy,
            "progress_policy": coerced_progress_policy,
            "battle_engine_mode": coerced_engine_mode,
        },
        "coercions_applied": coercions,
        "feature_flags": {
            "BATTLE_LAUNCH_AUTHORITATIVE_ENABLED": authoritative_enabled,
            "REWARD_LIVE_ENABLED": reward_live_enabled,
            "PROGRESS_LIVE_ENABLED": progress_live_enabled,
            "SERVER_SCOPED_RUNTIME_ENABLED": server_scoped_enabled,
        },
        "warnings": [
            "Battle launch is non-authoritative in v107A.",
            "No reward granted. No progress written. No DB mutation.",
            "server_id parsed but not used as backend filter (PSP not applied).",
        ],
        "safety": {
            "db_writes_performed": 0,
            "reward_granted": False,
            "progress_written": False,
            "currency_mutated": False,
        },
    }
