"""PROJECT_BATTLE_REPLAY_PREVIEW_ROUTE_PACK (v36 / PHASE_6).

Preview/route-only shell for the FUTURE Guild War battle-replay/view link.
Consumes the v35 Guild War replay payload schema. Strictly preview-gated.

FLAG: BATTLE_REPLAY_PREVIEW_ENABLED
  - default off / unset => every endpoint returns HTTP 503 disabled envelope
  - on                  => deterministic Guild War replay sample + display-only playback

Hard invariants enforced by code:
  - No DB writes (no DB import in this file).
  - No call to battle_engine (no import).
  - No call to /api/battle/simulate or /api/story/battle (no httpx/requests).
  - No reward grant. No EXP grant. No story/daily/quest/achievement progress.
  - No war score mutation. No guild points mutation.
  - No live /battle-replay route created.
  - viewer_kind = guild_war_view everywhere.
"""
from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

FEATURE_FLAG = "BATTLE_REPLAY_PREVIEW_ENABLED"
CONTRACT_VERSION = "battle_replay_preview_route_v1"
RUNTIME_MODE_TAG = "battle_replay_preview_route_gated_view_only"
SCHEMA_SOURCE = "guild_war_replay_payload_schema_v1"
CONTRACT_SOURCE = "guild_war_autoresolve_replay_link_contract_v1"
VIEWER_KIND = "guild_war_view"

router = APIRouter(
    prefix="/api/battle-replay-preview",
    tags=["battle_replay_preview"],
)


class ValidateReplayPayloadRequest(BaseModel):
    payload: Optional[Dict[str, Any]] = None


class PlaybackPreviewRequest(BaseModel):
    payload: Optional[Dict[str, Any]] = None


def _flag_enabled() -> bool:
    return os.environ.get(FEATURE_FLAG, "").strip().lower() == "true"


def _safety_flags() -> Dict[str, Any]:
    return {
        "preview_only": True,
        "viewer_kind": VIEWER_KIND,
        "db_writes": 0,
        "reward_grant_enabled": False,
        "exp_grant_enabled": False,
        "progress_enabled": False,
        "war_score_mutation_enabled": False,
        "guild_points_mutation_enabled": False,
        "claim_button_enabled": False,
        "commit_button_enabled": False,
        "battle_rerun_enabled": False,
        "calls_battle_engine": False,
        "calls_api_battle_simulate": False,
        "calls_api_story_battle": False,
        "live_battle_replay_route_created": False,
    }


def _disabled_payload(method: str, path_suffix: str) -> Dict[str, Any]:
    return {
        "status": "disabled",
        "contract_version": CONTRACT_VERSION,
        "schema_source": SCHEMA_SOURCE,
        "contract_source": CONTRACT_SOURCE,
        "runtime_mode": RUNTIME_MODE_TAG,
        "feature_flag": FEATURE_FLAG,
        "method": method,
        "path_suffix": path_suffix,
        "runtime_enabled": False,
        "preview_only": True,
        "viewer_kind": VIEWER_KIND,
        "db_writes": 0,
        "reward_grant_enabled": False,
        "exp_grant_enabled": False,
        "progress_enabled": False,
        "war_score_mutation_enabled": False,
        "guild_points_mutation_enabled": False,
    }


def _id(seed: str, prefix: str) -> str:
    h = hashlib.sha256(f"battle_replay_preview|{seed}".encode()).hexdigest()[:24]
    return f"{prefix}_{h}"


def _v35_sample_guild_war_replay() -> Dict[str, Any]:
    gw_id = _id("static_guild_war_battle_seed_v1", "gwb")
    bi_id = _id("static_battle_instance_seed_v1", "bi")
    return {
        "guild_war_battle_id": gw_id,
        "battle_instance_id": bi_id,
        "war_id": "war_preview_static_v1",
        "guild_id_attacker": "guild_atk_preview",
        "guild_id_defender": "guild_def_preview",
        "attacker_snapshot": {
            "schema": "attacker_snapshot_v1",
            "guild_id": "guild_atk_preview",
            "guild_name": "Crimson Vanguard (preview)",
            "heroes": [
                {"slot": 1, "hero_id": "atk_hero_a", "name": "Atk Hero A", "level": 1, "hp": 1100, "atk": 110},
                {"slot": 2, "hero_id": "atk_hero_b", "name": "Atk Hero B", "level": 1, "hp": 950, "atk": 95},
            ],
            "immutable_during_replay": True,
        },
        "defender_snapshot": {
            "schema": "defender_snapshot_v1",
            "guild_id": "guild_def_preview",
            "guild_name": "Iron Bulwark (preview)",
            "heroes": [
                {"slot": 1, "hero_id": "def_hero_a", "name": "Def Hero A", "level": 1, "hp": 1200, "atk": 100},
            ],
            "immutable_during_replay": True,
        },
        "battle_seed_or_precomputed_log": {
            "kind": "precomputed_battle_log",
            "precomputed_battle_log": [
                {"turn": 1, "actor": "atk_hero_a", "action": "basic_attack", "target": "def_hero_a", "damage": 120},
                {"turn": 2, "actor": "def_hero_a", "action": "basic_attack", "target": "atk_hero_a", "damage": 90},
                {"turn": 3, "actor": "atk_hero_b", "action": "basic_attack", "target": "def_hero_a", "damage": 95},
                {"turn": 4, "actor": "atk_hero_a", "action": "basic_attack", "target": "def_hero_a", "damage": 110},
            ],
            "client_side_simulation_forbidden": True,
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
            "winner": "attacker",
            "mvp_hero_id": "atk_hero_a",
            "stars": 3,
            "duration_seconds": 5.0,
            "display_only_in_replay": True,
        },
        "war_score_delta_display_only": {
            "attacker_delta": 25,
            "defender_delta": -25,
            "display_only_in_replay": True,
            "applied": False,
        },
        "reward_policy": {
            "grant_enabled": False,
            "replay_grants_rewards": False,
            "committer": "future_server_authoritative_mode_service",
            "no_duplicate_rewards": True,
        },
        "guild_points_policy": {
            "mutate_enabled": False,
            "replay_mutates_guild_points": False,
        },
        "privacy_policy": {
            "no_pii_in_share_payload": True,
            "redact_other_players": True,
        },
        "retention_policy": {
            "default_retention_days": 14,
            "max_retention_days": 30,
            "ttl_hard_required": True,
            "client_local_persistence_allowed": False,
            "async_storage_writes_allowed": False,
        },
        "created_at": "2026-05-31T18:30:00Z",
        "expires_at": "2026-06-14T18:30:00Z",
        "viewer_kind": VIEWER_KIND,
    }


def _v35_required_fields() -> list:
    return [
        "guild_war_battle_id",
        "battle_instance_id",
        "war_id",
        "guild_id_attacker",
        "guild_id_defender",
        "attacker_snapshot",
        "defender_snapshot",
        "battle_seed_or_precomputed_log",
        "playback_timeline",
        "result_summary",
        "war_score_delta_display_only",
        "reward_policy",
        "guild_points_policy",
        "privacy_policy",
        "retention_policy",
        "created_at",
        "expires_at",
    ]


def _validate_replay_shape(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "valid": False,
            "errors": ["payload must be an object"],
            "missing_fields": _v35_required_fields(),
        }
    missing = [f for f in _v35_required_fields() if f not in payload]
    return {
        "valid": len(missing) == 0,
        "errors": [] if not missing else [f"missing required field: {f}" for f in missing],
        "missing_fields": missing,
    }


@router.get("/config")
async def get_config() -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", "config"))
    return {
        "status": "enabled",
        "contract_version": CONTRACT_VERSION,
        "schema_source": SCHEMA_SOURCE,
        "contract_source": CONTRACT_SOURCE,
        "runtime_mode": RUNTIME_MODE_TAG,
        "feature_flag": FEATURE_FLAG,
        "runtime_enabled": True,
        "preview_only": True,
        "viewer_kind": VIEWER_KIND,
        "endpoints": {
            "config": "GET /api/battle-replay-preview/config",
            "sample_guild_war_replay": "GET /api/battle-replay-preview/sample-guild-war-replay",
            "validate_replay_payload": "POST /api/battle-replay-preview/validate-replay-payload",
            "playback_preview": "POST /api/battle-replay-preview/playback-preview",
        },
        "supported_viewer_kinds": ["guild_war_view"],
        "default_viewer_kind": VIEWER_KIND,
        "safety_flags": _safety_flags(),
    }


@router.get("/sample-guild-war-replay")
async def get_sample_guild_war_replay() -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(
            status_code=503, detail=_disabled_payload("GET", "sample-guild-war-replay")
        )
    payload = _v35_sample_guild_war_replay()
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "schema_source": SCHEMA_SOURCE,
        "contract_source": CONTRACT_SOURCE,
        "viewer_kind": VIEWER_KIND,
        "payload": payload,
        "safety_flags": _safety_flags(),
    }


@router.post("/validate-replay-payload")
async def validate_replay_payload(req: ValidateReplayPayloadRequest) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(
            status_code=503, detail=_disabled_payload("POST", "validate-replay-payload")
        )
    payload = req.payload if req and req.payload is not None else _v35_sample_guild_war_replay()
    result = _validate_replay_shape(payload)
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "schema_source": SCHEMA_SOURCE,
        "viewer_kind": VIEWER_KIND,
        "validation": result,
        "safety_flags": _safety_flags(),
    }


@router.post("/playback-preview")
async def playback_preview(req: PlaybackPreviewRequest) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "playback-preview"))
    payload = req.payload if req and req.payload is not None else _v35_sample_guild_war_replay()
    validation = _validate_replay_shape(payload)
    envelope = {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "schema_source": SCHEMA_SOURCE,
        "runner_mode": "replay_view",
        "viewer_kind": VIEWER_KIND,
        "battle_instance_id": payload.get("battle_instance_id") if validation.get("valid") else None,
        "guild_war_battle_id": payload.get("guild_war_battle_id") if validation.get("valid") else None,
        "timeline": payload.get("playback_timeline") if validation.get("valid") else [],
        "result_summary": payload.get("result_summary") if validation.get("valid") else None,
        "war_score_delta_display_only": payload.get("war_score_delta_display_only") if validation.get("valid") else None,
        "guild_war_context": {
            "war_id": payload.get("war_id") if validation.get("valid") else None,
            "guild_id_attacker": payload.get("guild_id_attacker") if validation.get("valid") else None,
            "guild_id_defender": payload.get("guild_id_defender") if validation.get("valid") else None,
            "guild_name_attacker": (payload.get("attacker_snapshot") or {}).get("guild_name") if validation.get("valid") else None,
            "guild_name_defender": (payload.get("defender_snapshot") or {}).get("guild_name") if validation.get("valid") else None,
        },
        "validation": validation,
        "safety_flags": _safety_flags(),
        "notes": [
            "display_only_envelope",
            "viewer_kind_is_guild_war_view",
            "replay_never_grants_rewards",
            "replay_never_grants_exp",
            "replay_never_advances_progress",
            "replay_never_mutates_war_score",
            "replay_never_mutates_guild_points",
            "replay_never_reruns_battle",
            "replay_never_calls_battle_engine",
            "replay_never_calls_api_battle_simulate",
            "replay_never_calls_api_story_battle",
            "replay_never_writes_to_db",
            "live_battle_replay_route_not_created",
        ],
    }
    return envelope
