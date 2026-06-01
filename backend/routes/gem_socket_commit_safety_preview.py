"""PROJECT_GEM_SOCKET_COMMIT_SAFETY_HARDENING_PACK (v37 Track A).

Preview-only/gated safety layer for the FUTURE Gem Socket commit.
Strictly preview-gated. No live commit. No DB write. No premium gems use.
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

FEATURE_FLAG = "GEM_SOCKET_COMMIT_SAFETY_PREVIEW_ENABLED"
CONTRACT_VERSION = "gem_socket_commit_safety_preview_v1"
RUNTIME_MODE_TAG = "gem_socket_commit_safety_preview_gated_no_live_commit"

router = APIRouter(
    prefix="/api/gem-socket-commit-safety-preview",
    tags=["gem_socket_commit_safety_preview"],
)


class RequestPayload(BaseModel):
    payload: Optional[Dict[str, Any]] = None


def _flag_enabled() -> bool:
    return os.environ.get(FEATURE_FLAG, "").strip().lower() == "true"


def _safety_flags() -> Dict[str, Any]:
    return {
        "preview_only": True,
        "commit_enabled": False,
        "gear_mutation_enabled": False,
        "gem_inventory_mutation_enabled": False,
        "premium_users_gems_used": False,
        "db_writes": 0,
        "reward_grant_enabled": False,
        "exp_grant_enabled": False,
        "stamina_consumed": False,
        "tickets_consumed": False,
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
        "commit_enabled": False,
        "gear_mutation_enabled": False,
        "gem_inventory_mutation_enabled": False,
        "db_writes": 0,
        "reward_grant_enabled": False,
        "exp_grant_enabled": False,
    }


def _idem(seed: str) -> str:
    return "idem_" + hashlib.sha256(f"gem_socket_commit_safety|{seed}".encode()).hexdigest()[:24]


def _sample_request() -> Dict[str, Any]:
    return {
        "request_id": "req_gem_socket_preview_static_v1",
        "user_id": "user_preview_static",
        "gear_id": "gear_preview_static_v1",
        "socket_index": 0,
        "gem_id": "gem_preview_static_v1",
        "expected_gear_version": 1,
        "expected_gem_version": 1,
        "expected_gear_socket_state_version": 1,
        "expected_gem_inventory_version": 1,
        "operation": "gem_socket_commit",
        "operation_family": "gem_socket_commit",
        "client_idempotency_key": "client_idem_static_v1",
    }


GUARD_CHECKS = [
    "ownership_verified",
    "gear_locked_or_favorite_check",
    "active_team_loadout_check",
    "active_pvp_loadout_check",
    "active_guild_war_loadout_check",
    "socket_index_eligible",
    "gem_valid_and_not_consumed",
    "expected_gear_version_match",
    "expected_gem_version_match",
    "expected_gear_socket_state_version_match",
    "expected_gem_inventory_version_match",
    "idempotency_key_required",
    "atomic_commit_required_future",
    "rollback_strategy_required_future",
    "audit_log_required_future",
]


def _guard_plan(req: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "operation": req.get("operation", "gem_socket_commit"),
        "operation_family": "gem_socket_commit",
        "guard_checks": [
            {"name": c, "status": "would_run", "preview_only": True} for c in GUARD_CHECKS
        ],
        "live_commit_will_run_in_preview": False,
        "gear_mutation_will_apply_in_preview": False,
        "gem_inventory_mutation_will_apply_in_preview": False,
    }


def _validate_request(req: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    required = [
        "request_id", "user_id", "gear_id", "socket_index", "gem_id",
        "expected_gear_version", "expected_gem_version",
        "expected_gear_socket_state_version", "expected_gem_inventory_version",
        "operation", "operation_family", "client_idempotency_key",
    ]
    if not isinstance(req, dict):
        return {"valid": False, "errors": ["payload must be an object"], "missing_fields": required}
    missing = [f for f in required if f not in req]
    errors = [f"missing required field: {f}" for f in missing]
    if req.get("operation_family") and req.get("operation_family") != "gem_socket_commit":
        errors.append("operation_family must be 'gem_socket_commit'")
    return {"valid": len(errors) == 0, "errors": errors, "missing_fields": missing}


def _idempotency_preview(req: Dict[str, Any]) -> Dict[str, Any]:
    seed = "|".join(str(req.get(k)) for k in (
        "request_id", "user_id", "gear_id", "socket_index", "gem_id",
        "operation_family", "client_idempotency_key",
    ))
    return {
        "server_idempotency_key": _idem(seed),
        "request_hash": hashlib.sha256(seed.encode()).hexdigest()[:16],
        "retry_same_key_must_return_same_result": True,
        "conflicting_payload_with_same_key_must_be_rejected": True,
        "atomic_commit_future": True,
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
        "operation_family": "gem_socket_commit",
        "supported_guard_checks": GUARD_CHECKS,
        "endpoints": {
            "config": "GET /api/gem-socket-commit-safety-preview/config",
            "validate_request": "POST /api/gem-socket-commit-safety-preview/validate-request",
            "guard_plan_preview": "POST /api/gem-socket-commit-safety-preview/guard-plan-preview",
            "idempotency_preview": "POST /api/gem-socket-commit-safety-preview/idempotency-preview",
        },
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_config_block(),
        "observability_dry_run": _v42_obs_config_block(),
    }


@router.post("/validate-request")
async def validate_request(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "validate-request"))
    req = body.payload if body and body.payload is not None else _sample_request()
    _v42_rh_env = _v42_rh_envelope(req, "gem_socket_commit")
    _v42_obs_env = _v42_obs_envelope(
        "gem_socket_commit", "gem_socket_commit", "validate-request",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "gem_socket_commit",
        "validation": _validate_request(req),
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_env,
        "observability_dry_run": _v42_obs_env,
    }


@router.post("/guard-plan-preview")
async def guard_plan_preview(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "guard-plan-preview"))
    req = body.payload if body and body.payload is not None else _sample_request()
    _v42_rh_env = _v42_rh_envelope(req, "gem_socket_commit")
    _v42_obs_env = _v42_obs_envelope(
        "gem_socket_commit", "gem_socket_commit", "guard-plan-preview",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "gem_socket_commit",
        "guard_plan": _guard_plan(req),
        "validation": _validate_request(req),
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_env,
        "observability_dry_run": _v42_obs_env,
        "notes": [
            "guard_plan_is_display_only",
            "no_live_commit_in_preview",
            "no_gear_mutation_in_preview",
            "no_gem_inventory_mutation_in_preview",
            "no_db_write_in_preview",
            "no_premium_users_gems_used",
        ],
    }


@router.post("/idempotency-preview")
async def idempotency_preview(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "idempotency-preview"))
    req = body.payload if body and body.payload is not None else _sample_request()
    _v42_rh_env = _v42_rh_envelope(req, "gem_socket_commit")
    _v42_obs_env = _v42_obs_envelope(
        "gem_socket_commit", "gem_socket_commit", "idempotency-preview",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    validation = _validate_request(req)
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "gem_socket_commit",
        "idempotency_preview": _idempotency_preview(req) if validation.get("valid") else None,
        "validation": validation,
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_env,
        "observability_dry_run": _v42_obs_env,
    }
