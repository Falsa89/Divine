"""PROJECT_MATERIAL_RAID_LIVE_CLAIM_SAFETY_HARDENING_PACK (v37 Track B).

Preview-only/gated safety layer for the FUTURE Material Raid live claim.
Strictly preview-gated. No live claim. No material grant. No DB write.
No stamina/tickets/paid attempts.

v42 dry-run runtime instrumentation: request_hash + observability envelopes
are attached when the feature flag is ON. Default 503 behavior unchanged.
No DB writes. No persistence. No live enforcement.
"""
from __future__ import annotations
import hashlib
import os
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from utils.economy_request_hash_dry_run import (
        build_request_hash_dry_run_envelope as _v42_rh_envelope,
        build_config_block as _v42_rh_config_block,
    )
    from utils.economy_observability_dry_run import (
        build_observability_dry_run_envelope as _v42_obs_envelope,
        build_config_block as _v42_obs_config_block,
    )
    _V42_DRY_RUN_AVAILABLE = True
except Exception:  # pragma: no cover - keep route safe even if utils missing
    _V42_DRY_RUN_AVAILABLE = False

    def _v42_rh_envelope(*_a, **_kw):  # type: ignore
        return {"enabled": False, "db_writes": 0}

    def _v42_rh_config_block():  # type: ignore
        return {"request_hash_dry_run_enabled": False, "db_writes": 0}

    def _v42_obs_envelope(*_a, **_kw):  # type: ignore
        return {"enabled": False, "db_writes": 0}

    def _v42_obs_config_block():  # type: ignore
        return {"enabled": False, "db_writes": 0}

try:
    from utils.economy_idempotency_replay_detection_dry_run import (
        build_replay_detection_dry_run_envelope as _v43_replay_envelope,
        build_config_block as _v43_replay_config_block,
    )
    _V43_REPLAY_DRY_RUN_AVAILABLE = True
except Exception:  # pragma: no cover - keep route safe even if util missing
    _V43_REPLAY_DRY_RUN_AVAILABLE = False

    def _v43_replay_envelope(*_a, **_kw):  # type: ignore
        return {
            "enabled": False,
            "dry_run_only": True,
            "detection_status": "missing_key_preview",
            "db_writes": 0,
            "live_enforcement_enabled": False,
            "preview_request_blocked": False,
        }

    def _v43_replay_config_block():  # type: ignore
        return {
            "enabled": False,
            "dry_run_only": True,
            "db_writes": 0,
            "live_enforcement_enabled": False,
        }

FEATURE_FLAG = "MATERIAL_RAID_CLAIM_SAFETY_PREVIEW_ENABLED"
CONTRACT_VERSION = "material_raid_claim_safety_preview_v1"
RUNTIME_MODE_TAG = "material_raid_claim_safety_preview_gated_no_live_claim"

router = APIRouter(
    prefix="/api/material-raid-claim-safety-preview",
    tags=["material_raid_claim_safety_preview"],
)


class RequestPayload(BaseModel):
    payload: Optional[Dict[str, Any]] = None


def _flag_enabled() -> bool:
    return os.environ.get(FEATURE_FLAG, "").strip().lower() == "true"


def _safety_flags() -> Dict[str, Any]:
    return {
        "preview_only": True,
        "claim_enabled": False,
        "materials_granted": False,
        "user_materials_mutation_enabled": False,
        "db_writes": 0,
        "reward_grant_enabled": False,
        "exp_grant_enabled": False,
        "stamina_consumed": False,
        "tickets_consumed": False,
        "paid_attempt_consumed": False,
        "calls_battle_engine": False,
        "calls_api_battle_simulate": False,
        "calls_api_story_battle": False,
    }


def _disabled(method: str, path_suffix: str) -> Dict[str, Any]:
    return {
        "status": "disabled",
        "contract_version": CONTRACT_VERSION,
        "runtime_mode": RUNTIME_MODE_TAG,
        "feature_flag": FEATURE_FLAG,
        "method": method,
        "path_suffix": path_suffix,
        "runtime_enabled": False,
        "preview_only": True,
        "claim_enabled": False,
        "materials_granted": False,
        "user_materials_mutation_enabled": False,
        "db_writes": 0,
        "reward_grant_enabled": False,
        "exp_grant_enabled": False,
        "stamina_consumed": False,
    }


def _idem(seed: str) -> str:
    return "idem_" + hashlib.sha256(f"material_raid_claim_safety|{seed}".encode()).hexdigest()[:24]


def _sample_request() -> Dict[str, Any]:
    return {
        "request_id": "req_material_raid_claim_preview_static_v1",
        "user_id": "user_preview_static",
        "track_id": "track_gold",
        "stage_id": "stage_1",
        "raid_clear_instance_id_future": "clr_preview_static_v1",
        "expected_reward_hash": "reward_hash_static_v1",
        "expected_reward_table_version": 1,
        "operation": "material_raid_claim",
        "operation_family": "material_raid_claim",
        "client_idempotency_key": "client_idem_static_v1",
    }


GUARD_CHECKS = [
    "ownership_verified",
    "track_id_valid",
    "stage_id_valid",
    "raid_clear_instance_id_future_match",
    "not_already_claimed_future",
    "expected_reward_hash_match",
    "expected_reward_table_version_match",
    "idempotency_key_required",
    "user_materials_future_target_acquired",
    "atomic_increment_future",
    "rollback_strategy_required_future",
    "audit_log_required_future",
    "no_stamina_consumed",
    "no_tickets_consumed",
    "no_paid_attempt_consumed",
]


def _guard_plan(req: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "operation": req.get("operation", "material_raid_claim"),
        "operation_family": "material_raid_claim",
        "guard_checks": [
            {"name": c, "status": "would_run", "preview_only": True} for c in GUARD_CHECKS
        ],
        "live_claim_will_run_in_preview": False,
        "materials_will_be_granted_in_preview": False,
        "user_materials_will_be_mutated_in_preview": False,
    }


def _validate_request(req: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    required = [
        "request_id", "user_id", "track_id", "stage_id",
        "raid_clear_instance_id_future", "expected_reward_hash",
        "expected_reward_table_version",
        "operation", "operation_family", "client_idempotency_key",
    ]
    if not isinstance(req, dict):
        return {"valid": False, "errors": ["payload must be an object"], "missing_fields": required}
    missing = [f for f in required if f not in req]
    errors = [f"missing required field: {f}" for f in missing]
    if req.get("operation_family") and req.get("operation_family") != "material_raid_claim":
        errors.append("operation_family must be 'material_raid_claim'")
    return {"valid": len(errors) == 0, "errors": errors, "missing_fields": missing}


def _idempotency_preview(req: Dict[str, Any]) -> Dict[str, Any]:
    seed = "|".join(str(req.get(k)) for k in (
        "request_id", "user_id", "track_id", "stage_id",
        "raid_clear_instance_id_future", "expected_reward_hash",
        "operation_family", "client_idempotency_key",
    ))
    return {
        "server_idempotency_key": _idem(seed),
        "request_hash": hashlib.sha256(seed.encode()).hexdigest()[:16],
        "retry_same_key_must_return_same_result": True,
        "conflicting_payload_with_same_key_must_be_rejected": True,
        "atomic_increment_future": True,
        "audit_log_future": True,
        "rollback_strategy_future": True,
        "ttl_seconds_recommended": 86400,
    }


@router.get("/config")
async def get_config() -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("GET", "config"))
    return {
        "status": "enabled",
        "contract_version": CONTRACT_VERSION,
        "runtime_mode": RUNTIME_MODE_TAG,
        "feature_flag": FEATURE_FLAG,
        "runtime_enabled": True,
        "preview_only": True,
        "operation_family": "material_raid_claim",
        "supported_guard_checks": GUARD_CHECKS,
        "endpoints": {
            "config": "GET /api/material-raid-claim-safety-preview/config",
            "validate_claim_request": "POST /api/material-raid-claim-safety-preview/validate-claim-request",
            "grant_plan_preview": "POST /api/material-raid-claim-safety-preview/grant-plan-preview",
            "idempotency_preview": "POST /api/material-raid-claim-safety-preview/idempotency-preview",
        },
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_config_block(),
        "observability_dry_run": _v42_obs_config_block(),
        "idempotency_replay_detection_dry_run": _v43_replay_config_block(),
    }


@router.post("/validate-claim-request")
async def validate_claim_request(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "validate-claim-request"))
    req = body.payload if body and body.payload is not None else _sample_request()
    rh_env = _v42_rh_envelope(req, "material_raid_claim")
    obs_env = _v42_obs_envelope(
        "material_raid_claim", "material_raid_claim", "validate-claim-request",
        outcome="success_preview_503", status="preview_ok",
        request_hash=rh_env.get("request_hash"),
        server_idempotency_key=rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    _v43_replay_env = _v43_replay_envelope(
        "material_raid_claim",
        server_idempotency_key=rh_env.get("server_idempotency_key_preview"),
        request_hash=rh_env.get("request_hash"),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="material_raid_claim",
    )
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "material_raid_claim",
        "validation": _validate_request(req),
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": rh_env,
        "observability_dry_run": obs_env,
        "idempotency_replay_detection_dry_run": _v43_replay_env,
    }


@router.post("/grant-plan-preview")
async def grant_plan_preview(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "grant-plan-preview"))
    req = body.payload if body and body.payload is not None else _sample_request()
    rh_env = _v42_rh_envelope(req, "material_raid_claim")
    obs_env = _v42_obs_envelope(
        "material_raid_claim", "material_raid_claim", "grant-plan-preview",
        outcome="success_preview_503", status="preview_ok",
        request_hash=rh_env.get("request_hash"),
        server_idempotency_key=rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    _v43_replay_env = _v43_replay_envelope(
        "material_raid_claim",
        server_idempotency_key=rh_env.get("server_idempotency_key_preview"),
        request_hash=rh_env.get("request_hash"),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="material_raid_claim",
    )
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "material_raid_claim",
        "grant_plan": _guard_plan(req),
        "validation": _validate_request(req),
        "safety_flags": _safety_flags(),
        "notes": [
            "grant_plan_is_display_only",
            "no_live_claim_in_preview",
            "no_materials_granted_in_preview",
            "no_user_materials_mutation_in_preview",
            "no_db_write_in_preview",
            "no_stamina_consumed_in_preview",
            "no_tickets_consumed_in_preview",
            "no_paid_attempt_consumed_in_preview",
        ],
        "request_hash_dry_run": rh_env,
        "observability_dry_run": obs_env,
        "idempotency_replay_detection_dry_run": _v43_replay_env,
    }


@router.post("/idempotency-preview")
async def idempotency_preview(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "idempotency-preview"))
    req = body.payload if body and body.payload is not None else _sample_request()
    validation = _validate_request(req)
    rh_env = _v42_rh_envelope(req, "material_raid_claim")
    obs_env = _v42_obs_envelope(
        "material_raid_claim", "material_raid_claim", "idempotency-preview",
        outcome="success_preview_503", status="preview_ok",
        request_hash=rh_env.get("request_hash"),
        server_idempotency_key=rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    _v43_replay_env = _v43_replay_envelope(
        "material_raid_claim",
        server_idempotency_key=rh_env.get("server_idempotency_key_preview"),
        request_hash=rh_env.get("request_hash"),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="material_raid_claim",
    )
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "material_raid_claim",
        "idempotency_preview": _idempotency_preview(req) if validation.get("valid") else None,
        "validation": validation,
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": rh_env,
        "observability_dry_run": obs_env,
        "idempotency_replay_detection_dry_run": _v43_replay_env,
    }
