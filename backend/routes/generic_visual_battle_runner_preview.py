"""PROJECT_GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ROUTE_PACK (v34 / PHASE_4).

Preview/route-only shell for the FUTURE Generic Visual Battle Runner.
Consumes the v33 contract/payload schema. Strictly preview-gated.

FLAG: GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ENABLED
  - default off / unset => every endpoint returns HTTP 503 disabled envelope
  - on                  => deterministic sample payload + display-only playback

Hard invariants enforced by code:
  - No DB writes (no DB import in this file).
  - No call to battle_engine (no import).
  - No call to /api/battle/simulate or /api/story/battle (no httpx/requests).
  - No reward grant. No EXP grant. No story/daily/quest/achievement progress.
  - No claim/commit buttons exposed.
  - Runner is view-only by design contract.
"""
from __future__ import annotations

import hashlib
import os
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

FEATURE_FLAG = "GENERIC_VISUAL_BATTLE_RUNNER_PREVIEW_ENABLED"
CONTRACT_VERSION = "generic_visual_battle_runner_preview_v1"
RUNTIME_MODE_TAG = "preview_route_gated_no_live_commit"
SCHEMA_VERSION = "visual_battle_runner_payload_schema_v1"
CONTRACT_VERSION_SOURCE = "generic_visual_battle_runner_contract_v1"

router = APIRouter(
    prefix="/api/generic-visual-battle-runner-preview",
    tags=["generic_visual_battle_runner_preview"],
)


# --------------------------------------------------------------------------- #
# Models
# --------------------------------------------------------------------------- #
class ValidatePayloadRequest(BaseModel):
    payload: Optional[Dict[str, Any]] = None


class PlaybackPreviewRequest(BaseModel):
    payload: Optional[Dict[str, Any]] = None


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _flag_enabled() -> bool:
    return os.environ.get(FEATURE_FLAG, "").strip().lower() == "true"


def _safety_flags() -> Dict[str, Any]:
    return {
        "preview_only": True,
        "db_writes": 0,
        "reward_grant_enabled": False,
        "exp_grant_enabled": False,
        "progress_enabled": False,
        "story_progress_enabled": False,
        "daily_progress_enabled": False,
        "quest_progress_enabled": False,
        "achievement_progress_enabled": False,
        "claim_button_enabled": False,
        "commit_button_enabled": False,
        "battle_simulation_enabled": False,
        "calls_battle_engine": False,
        "calls_api_battle_simulate": False,
        "calls_api_story_battle": False,
    }


def _disabled_payload(method: str, path_suffix: str) -> Dict[str, Any]:
    return {
        "status": "disabled",
        "contract_version": CONTRACT_VERSION,
        "schema_source": SCHEMA_VERSION,
        "contract_source": CONTRACT_VERSION_SOURCE,
        "runtime_mode": RUNTIME_MODE_TAG,
        "feature_flag": FEATURE_FLAG,
        "method": method,
        "path_suffix": path_suffix,
        "runtime_enabled": False,
        "preview_only": True,
        "db_writes": 0,
        "reward_grant_enabled": False,
        "exp_grant_enabled": False,
        "progress_enabled": False,
    }


def _make_battle_instance_id(seed_str: str) -> str:
    seed = f"gvbr_preview|{seed_str}".encode()
    return "bi_" + hashlib.sha256(seed).hexdigest()[:24]


def _make_idempotency_key(battle_instance_id: str) -> str:
    seed = f"idem|{battle_instance_id}".encode()
    return "idem_" + hashlib.sha256(seed).hexdigest()[:24]


def _v33_sample_payload() -> Dict[str, Any]:
    """Deterministic sample payload compliant with v33 schema (21 fields)."""
    bi_id = _make_battle_instance_id("static_preview_seed_v1")
    idem = _make_idempotency_key(bi_id)
    now_epoch = 1717000000  # deterministic for preview
    return {
        # v33 required fields (21)
        "battle_instance_id": bi_id,
        "runner_mode": "sandbox_preview",
        "mode_id": "generic_preview",
        "source_entrypoint": "generic_visual_battle_runner_preview",
        "viewer_kind": "sandbox_preview",
        "team_snapshot": {
            "schema": "team_snapshot_v1",
            "heroes": [
                {"slot": 1, "hero_id": "sample_hero_a", "name": "Sample Hero A", "level": 1, "hp": 1000, "atk": 100},
                {"slot": 2, "hero_id": "sample_hero_b", "name": "Sample Hero B", "level": 1, "hp": 900, "atk": 90},
            ],
            "immutable_during_playback": True,
        },
        "enemy_snapshot": {
            "schema": "enemy_snapshot_v1",
            "enemies": [
                {"slot": 1, "enemy_id": "sample_enemy_a", "name": "Sample Enemy A", "hp": 1200, "atk": 110},
            ],
            "immutable_during_playback": True,
        },
        "formation_snapshot": {
            "schema": "formation_snapshot_v1",
            "layout": "2v1_preview",
            "immutable_during_playback": True,
        },
        "battle_background_context": {
            "background_id": "bg_preview_neutral",
            "music_id": "bgm_preview_neutral",
            "weather": "clear",
            "lighting": "neutral",
            "faction_theme": "neutral",
        },
        "battle_seed_or_precomputed_battle_log": {
            "kind": "precomputed_battle_log",
            "precomputed_battle_log": [
                {"turn": 1, "actor": "sample_hero_a", "action": "basic_attack", "target": "sample_enemy_a", "damage": 100},
                {"turn": 2, "actor": "sample_enemy_a", "action": "basic_attack", "target": "sample_hero_a", "damage": 80},
                {"turn": 3, "actor": "sample_hero_b", "action": "basic_attack", "target": "sample_enemy_a", "damage": 90},
                {"turn": 4, "actor": "sample_hero_a", "action": "basic_attack", "target": "sample_enemy_a", "damage": 110},
            ],
            "client_side_simulation_forbidden_in_authoritative_modes": True,
        },
        "playback_timeline": [
            {"t": 0.0, "event": "battle_start"},
            {"t": 1.0, "event": "turn_1_animation"},
            {"t": 2.0, "event": "turn_2_animation"},
            {"t": 3.0, "event": "turn_3_animation"},
            {"t": 4.0, "event": "turn_4_animation"},
            {"t": 5.0, "event": "battle_end_winner_team"},
        ],
        "result_summary": {
            "winner": "team",
            "mvp_hero_id": "sample_hero_a",
            "stars": 3,
            "duration_seconds": 5.0,
            "display_only_in_runner": True,
        },
        "reward_policy": {
            "grant_enabled": False,
            "runner_can_grant": False,
            "committer": "future_server_authoritative_mode_service",
        },
        "exp_policy": {
            "grant_enabled": False,
            "runner_can_grant": False,
            "committer": "future_server_authoritative_mode_service",
        },
        "progress_policy": {
            "advance_enabled": False,
            "runner_can_advance": False,
            "story_progress_enabled": False,
            "daily_progress_enabled": False,
            "quest_progress_enabled": False,
            "achievement_progress_enabled": False,
            "committer": "future_server_authoritative_mode_service",
        },
        "result_commit_policy": {
            "commit_enabled": False,
            "runner_commits": False,
            "idempotency_key_required": True,
            "idempotency_key": idem,
            "committer": "future_server_authoritative_mode_service",
        },
        "replay_snapshot_policy": {
            "write_enabled": False,
            "replay_grants_rewards": False,
            "replay_advances_progress": False,
            "replay_reruns_battle": False,
        },
        "ui_policy": {
            "show_claim_buttons": False,
            "show_commit_buttons": False,
            "spectator_only": True,
            "skip_speed_auto_allowed": True,
        },
        "privacy_policy": {
            "share_contains_pii": False,
            "redact_other_players": True,
        },
        "created_at": "2026-05-31T17:20:00Z",
        "expires_at": "2026-05-31T18:20:00Z",
    }


def _v33_required_fields() -> list:
    return [
        "battle_instance_id",
        "runner_mode",
        "mode_id",
        "source_entrypoint",
        "viewer_kind",
        "team_snapshot",
        "enemy_snapshot",
        "formation_snapshot",
        "battle_background_context",
        "battle_seed_or_precomputed_battle_log",
        "playback_timeline",
        "result_summary",
        "reward_policy",
        "exp_policy",
        "progress_policy",
        "result_commit_policy",
        "replay_snapshot_policy",
        "ui_policy",
        "privacy_policy",
        "created_at",
        "expires_at",
    ]


def _validate_payload_shape(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "valid": False,
            "errors": ["payload must be an object"],
            "missing_fields": _v33_required_fields(),
        }
    missing = [f for f in _v33_required_fields() if f not in payload]
    return {
        "valid": len(missing) == 0,
        "errors": [] if not missing else [f"missing required field: {f}" for f in missing],
        "missing_fields": missing,
    }


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #
@router.get("/config")
async def get_config() -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", "config"))
    return {
        "status": "enabled",
        "contract_version": CONTRACT_VERSION,
        "schema_source": SCHEMA_VERSION,
        "contract_source": CONTRACT_VERSION_SOURCE,
        "runtime_mode": RUNTIME_MODE_TAG,
        "feature_flag": FEATURE_FLAG,
        "runtime_enabled": True,
        "preview_only": True,
        "endpoints": {
            "config": "GET /api/generic-visual-battle-runner-preview/config",
            "sample_payload": "GET /api/generic-visual-battle-runner-preview/sample-payload",
            "validate_payload": "POST /api/generic-visual-battle-runner-preview/validate-payload",
            "playback_preview": "POST /api/generic-visual-battle-runner-preview/playback-preview",
        },
        "supported_viewer_kinds": [
            "live_preview",
            "live_commit_pending_future",
            "replay_view",
            "guild_war_view",
            "sandbox_preview",
            "qa_direct",
        ],
        "default_viewer_kind": "sandbox_preview",
        "safety_flags": _safety_flags(),
    }


@router.get("/sample-payload")
async def get_sample_payload() -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", "sample-payload"))
    payload = _v33_sample_payload()
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "schema_source": SCHEMA_VERSION,
        "contract_source": CONTRACT_VERSION_SOURCE,
        "payload": payload,
        "safety_flags": _safety_flags(),
    }


@router.post("/validate-payload")
async def validate_payload(req: ValidatePayloadRequest) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "validate-payload"))
    payload = req.payload if req and req.payload is not None else _v33_sample_payload()
    result = _validate_payload_shape(payload)
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "schema_source": SCHEMA_VERSION,
        "validation": result,
        "safety_flags": _safety_flags(),
    }


@router.post("/playback-preview")
async def playback_preview(req: PlaybackPreviewRequest) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "playback-preview"))
    payload = req.payload if req and req.payload is not None else _v33_sample_payload()
    validation = _validate_payload_shape(payload)
    # Display-only envelope. No battle simulation. No winner recomputation.
    envelope = {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "schema_source": SCHEMA_VERSION,
        "runner_mode": payload.get("runner_mode") if validation.get("valid") else None,
        "viewer_kind": payload.get("viewer_kind") if validation.get("valid") else None,
        "battle_instance_id": payload.get("battle_instance_id") if validation.get("valid") else None,
        "timeline": payload.get("playback_timeline") if validation.get("valid") else [],
        "result_summary": payload.get("result_summary") if validation.get("valid") else None,
        "validation": validation,
        "safety_flags": _safety_flags(),
        "notes": [
            "display_only_envelope",
            "runner_never_grants_rewards",
            "runner_never_grants_exp",
            "runner_never_advances_progress",
            "runner_never_calls_battle_engine",
            "runner_never_calls_api_battle_simulate",
            "runner_never_calls_api_story_battle",
            "runner_never_writes_to_db",
        ],
    }
    return envelope
