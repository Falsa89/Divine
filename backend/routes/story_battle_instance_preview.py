"""PROJECT_STORY_BATTLE_INSTANCE_PREVIEW_ENDPOINT (PHASE_2).

Preview-only/gated endpoint for Story battle instance payload creation.
Returns contract-compliant payload envelopes that the future visual battle
runner can consume; never commits rewards, EXP, or story progress.

FLAG: STORY_BATTLE_INSTANCE_PREVIEW_ENABLED
- default off => 503 inert envelope, no DB reads, no DB writes
- on         => deterministic preview payload, no DB writes, no rewards/EXP/progress

MEGA_BATCH_ACCELERATION_1 TRACK A.
No modification of /api/story/battle or /api/battle/simulate. story.tsx UNCHANGED.
combat.tsx UNCHANGED. battle_engine.py UNCHANGED.
"""
import hashlib
import os
import time
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

FEATURE_FLAG = "STORY_BATTLE_INSTANCE_PREVIEW_ENABLED"
CONTRACT_VERSION = "project_story_battle_instance_preview_v1"
RUNTIME_MODE_TAG = "preview_only_gated"

router = APIRouter(prefix="/api/story/battle-instance-preview", tags=["story_battle_instance_preview"])


class CreatePreviewRequest(BaseModel):
    chapter_id: Optional[str] = None
    stage: Optional[str] = None
    stage_id: Optional[str] = None


class ValidatePayloadRequest(BaseModel):
    payload: Optional[dict] = None


def _flag_enabled() -> bool:
    return os.environ.get(FEATURE_FLAG, "").strip().lower() == "true"


def _disabled_payload(method: str, path_suffix: str) -> dict:
    return {
        "status": "disabled",
        "contract_version": CONTRACT_VERSION,
        "runtime_mode": RUNTIME_MODE_TAG,
        "feature_flag": FEATURE_FLAG,
        "method": method,
        "path_suffix": path_suffix,
        "runtime_enabled": False,
        "db_writes": 0,
        "reward_grant_enabled": False,
        "exp_grant_enabled": False,
        "story_progress_enabled": False,
        "visual_runtime_enabled": False,
        "preview_only": True,
    }


def _make_battle_instance_id(chapter_id: str, stage_id: str) -> str:
    seed = f"story|{chapter_id}|{stage_id}|{int(time.time())}".encode()
    return "bi_" + hashlib.sha256(seed).hexdigest()[:24]


def _make_idempotency_key(battle_instance_id: str) -> str:
    seed = f"idem|{battle_instance_id}".encode()
    return "idem_" + hashlib.sha256(seed).hexdigest()[:24]


def _safety_flags() -> dict:
    return {
        "preview_only": True,
        "db_writes": 0,
        "reward_grant_enabled": False,
        "exp_grant_enabled": False,
        "story_progress_enabled": False,
        "visual_runtime_enabled": False,
    }


def _sample_payload(chapter_id: str = "chapter_1", stage_id: str = "1-1") -> dict:
    bi_id = _make_battle_instance_id(chapter_id, stage_id)
    idem = _make_idempotency_key(bi_id)
    created_at = int(time.time())
    expires_at = created_at + 3600
    return {
        "battle_instance_id": bi_id,
        "idempotency_key": idem,
        "mode_id": "story",
        "chapter_id": chapter_id,
        "stage_id": stage_id,
        "source_entrypoint": "story_stage_play",
        "team_snapshot": {"placeholder": True, "note": "contract placeholder; runtime payload will include real team snapshot"},
        "enemy_snapshot": {"placeholder": True, "note": "contract placeholder; runtime payload will include real enemy snapshot"},
        "formation_snapshot": {"placeholder": True, "layout": "3x3"},
        "battle_seed": hashlib.sha256(bi_id.encode()).hexdigest()[:16],
        "precomputed_battle_log": None,
        "reward_policy": {
            "idempotency_key": idem,
            "granted_state": "PENDING",
            "claim_window_seconds": 3600,
            "server_authoritative": True,
            "once_only": True,
        },
        "exp_policy": {
            "hero_exp_idempotency_key": idem + "_hexp",
            "account_exp_idempotency_key": idem + "_aexp",
            "once_only": True,
        },
        "story_progress_policy": {
            "advance_once_only_per_battle_instance_id": True,
            "first_clear_flag_once_only": True,
            "replay_does_not_advance": True,
        },
        "result_commit_policy": {
            "commit_once": True,
            "idempotency_key": idem,
            "server_authoritative": True,
            "retry_returns_same_result": True,
        },
        "replay_snapshot_policy": {
            "ttl_seconds": 86400,
            "scope": "private",
            "pii_safe": True,
            "never_grants_reward": True,
            "never_advances_progress": True,
            "never_reruns_battle_logic_for_reward": True,
        },
        "created_at": created_at,
        "expires_at": expires_at,
        **_safety_flags(),
    }


@router.get("/config")
async def story_battle_instance_preview_config() -> dict:
    """Return preview config/safety. 503 inert if flag-off."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", "config"))
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_mode": RUNTIME_MODE_TAG,
        "feature_flag": FEATURE_FLAG,
        "runtime_enabled": True,
        "endpoints": [
            "/api/story/battle-instance-preview/config",
            "/api/story/battle-instance-preview/create-preview",
            "/api/story/battle-instance-preview/validate-payload",
            "/api/story/battle-instance-preview/sample",
        ],
        "safety": _safety_flags(),
        "separated_from": [
            "/api/story/battle (legacy auto-resolve)",
            "/api/battle/simulate (direct visual route)",
            "battle_engine",
            "reward_grant",
            "exp_grant",
            "story_progress_mutation",
        ],
    }


@router.post("/create-preview")
async def story_battle_instance_create_preview(payload: CreatePreviewRequest) -> dict:
    """Create a preview-only battle instance envelope. NO DB writes."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "create-preview"))
    chapter_id = (payload.chapter_id or "chapter_1").strip() or "chapter_1"
    stage_id = (payload.stage_id or payload.stage or "1-1").strip() or "1-1"
    envelope = _sample_payload(chapter_id, stage_id)
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_mode": RUNTIME_MODE_TAG,
        "runtime_enabled": True,
        "battle_instance": envelope,
        "safety": _safety_flags(),
    }


@router.post("/validate-payload")
async def story_battle_instance_validate_payload(req: ValidatePayloadRequest) -> dict:
    """Validate the shape of a supplied preview payload. NO DB writes."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("POST", "validate-payload"))
    p = req.payload or {}
    required = [
        "battle_instance_id", "idempotency_key", "mode_id", "chapter_id", "stage_id",
        "source_entrypoint", "team_snapshot", "enemy_snapshot", "formation_snapshot",
        "reward_policy", "exp_policy", "story_progress_policy",
        "result_commit_policy", "replay_snapshot_policy",
        "created_at", "expires_at",
    ]
    missing = [k for k in required if k not in p]
    has_seed_or_log = bool(p.get("battle_seed")) or bool(p.get("precomputed_battle_log"))
    valid = (not missing) and has_seed_or_log and (p.get("mode_id") == "story")
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "valid": valid,
        "missing_fields": missing,
        "has_seed_or_log": has_seed_or_log,
        "safety": _safety_flags(),
    }


@router.get("/sample")
async def story_battle_instance_sample() -> dict:
    """Return a deterministic sample payload for frontend/future runner."""
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled_payload("GET", "sample"))
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "runtime_enabled": True,
        "battle_instance": _sample_payload("chapter_1", "1-1"),
        "safety": _safety_flags(),
    }
