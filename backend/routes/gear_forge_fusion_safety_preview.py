"""PROJECT_GEAR_FORGE_FUSION_COMMIT_SAFETY_HARDENING_PACK (v38 Track A).

Preview-only/gated safety layer for the FUTURE Gear Forge/Fusion commit.
Strictly preview-gated. No live commit. No DB write. No gear mutation.
No material/currency consumption. No premium users.gems usage. No BP Delta.
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

FEATURE_FLAG = "GEAR_FORGE_FUSION_SAFETY_PREVIEW_ENABLED"
CONTRACT_VERSION = "gear_forge_fusion_safety_preview_v1"
RUNTIME_MODE_TAG = "gear_forge_fusion_safety_preview_gated_no_live_commit"

router = APIRouter(
    prefix="/api/gear-forge-fusion-safety-preview",
    tags=["gear_forge_fusion_safety_preview"],
)


class RequestPayload(BaseModel):
    payload: Optional[Dict[str, Any]] = None


def _flag_enabled() -> bool:
    return os.environ.get(FEATURE_FLAG, "").strip().lower() == "true"


def _safety_flags() -> Dict[str, Any]:
    return {
        "preview_only": True,
        "commit_enabled": False,
        "live_mutation_enabled": False,
        "gear_mutation_enabled": False,
        "materials_consumed": False,
        "currency_consumed": False,
        "premium_gems_currency_used": False,
        "bp_delta_triggered": False,
        "db_writes": 0,
        "reward_grant_enabled": False,
        "exp_grant_enabled": False,
        "stamina_consumed": False,
        "tickets_consumed": False,
        "calls_battle_engine": False,
        "calls_api_battle_simulate": False,
        "calls_api_story_battle": False,
        "calls_forge_legacy": False,
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
        "live_mutation_enabled": False,
        "gear_mutation_enabled": False,
        "materials_consumed": False,
        "currency_consumed": False,
        "premium_gems_currency_used": False,
        "bp_delta_triggered": False,
        "db_writes": 0,
    }


def _idem(seed: str) -> str:
    return "idem_" + hashlib.sha256(f"gear_forge_fusion_safety|{seed}".encode()).hexdigest()[:24]


ALLOWED_OPERATION_TYPES = ("gear_upgrade", "gear_fusion", "gear_reforge_preview")


def _sample_request() -> Dict[str, Any]:
    return {
        "request_id": "req_gear_forge_fusion_preview_static_v1",
        "idempotency_key": "client_idem_static_v1",
        "operation_type": "gear_fusion",
        "operation_family": "gear_forge_fusion_commit",
        "user_id": "user_preview_static",
        "server_id": "server_s1_preview_static",
        "base_gear_instance_id": "gear_base_preview_static_v1",
        "fodder_gear_instance_ids": ["gear_fodder_a_static_v1", "gear_fodder_b_static_v1"],
        "target_level": 30,
        "target_rarity": 5,
        "expected_base_gear_version": 1,
        "expected_inventory_version": 1,
        "expected_materials_version": 1,
        "client_trace_id": "trace_preview_static_v1",
        "created_at": "2026-05-31T19:00:00Z",
    }


GUARD_CHECKS = [
    "auth_required",
    "user_owns_base_gear",
    "user_owns_all_fodder_gear",
    "base_gear_not_locked",
    "base_gear_not_favorite",
    "fodder_gear_not_locked",
    "fodder_gear_not_favorite",
    "base_gear_not_in_active_team_loadout",
    "base_gear_not_in_pvp_defense_loadout",
    "base_gear_not_in_guild_war_defense_loadout",
    "fodder_gear_not_equipped",
    "fodder_gear_not_in_any_defense_loadout",
    "no_duplicate_fodder_ids",
    "base_not_in_fodder",
    "target_level_within_cap",
    "target_rarity_within_cap",
    "fusion_recipe_valid",
    "material_cost_policy_defined_but_not_charged",
    "currency_cost_policy_defined_but_not_charged",
    "same_request_id_not_committed",
    "idempotency_key_required",
    "expected_versions_match",
    "premium_users_gems_not_used",
    "atomic_commit_required_future",
    "rollback_policy_required_future",
    "audit_log_required_future",
    "bp_delta_not_triggered_in_preview",
]


def _guard_plan(req: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "operation": req.get("operation_type", "gear_fusion"),
        "operation_family": "gear_forge_fusion_commit",
        "guard_checks": [
            {"name": c, "status": "would_run", "preview_only": True} for c in GUARD_CHECKS
        ],
        "live_commit_will_run_in_preview": False,
        "gear_mutation_will_apply_in_preview": False,
        "materials_will_be_consumed_in_preview": False,
        "currency_will_be_consumed_in_preview": False,
        "premium_gems_currency_will_be_used_in_preview": False,
        "bp_delta_will_be_triggered_in_preview": False,
    }


REQUIRED_FIELDS = [
    "request_id", "idempotency_key", "operation_type", "user_id", "server_id",
    "base_gear_instance_id", "fodder_gear_instance_ids",
    "target_level", "target_rarity",
    "expected_base_gear_version", "expected_inventory_version",
    "expected_materials_version", "client_trace_id", "created_at",
]


def _validate_request(req: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(req, dict):
        return {"valid": False, "errors": ["payload must be an object"], "missing_fields": REQUIRED_FIELDS}
    missing = [f for f in REQUIRED_FIELDS if f not in req]
    errors = [f"missing required field: {f}" for f in missing]
    op = req.get("operation_type")
    if op is not None and op not in ALLOWED_OPERATION_TYPES:
        errors.append(f"operation_type must be one of {list(ALLOWED_OPERATION_TYPES)}")
    fodder = req.get("fodder_gear_instance_ids")
    if fodder is not None:
        if not isinstance(fodder, list):
            errors.append("fodder_gear_instance_ids must be a list")
        else:
            if len(set(fodder)) != len(fodder):
                errors.append("fodder_gear_instance_ids must not contain duplicates")
            if req.get("base_gear_instance_id") in fodder:
                errors.append("base_gear_instance_id must not be in fodder_gear_instance_ids")
    return {"valid": len(errors) == 0, "errors": errors, "missing_fields": missing}


def _idempotency_preview(req: Dict[str, Any]) -> Dict[str, Any]:
    seed = "|".join(str(req.get(k)) for k in (
        "request_id", "user_id", "server_id",
        "base_gear_instance_id", "operation_type", "idempotency_key",
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
        "live_commit_allowed": False,
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
        "operation_family": "gear_forge_fusion_commit",
        "allowed_operation_types": list(ALLOWED_OPERATION_TYPES),
        "supported_guard_checks": GUARD_CHECKS,
        "endpoints": {
            "config": "GET /api/gear-forge-fusion-safety-preview/config",
            "validate_request": "POST /api/gear-forge-fusion-safety-preview/validate-request",
            "guard_plan_preview": "POST /api/gear-forge-fusion-safety-preview/guard-plan-preview",
            "idempotency_preview": "POST /api/gear-forge-fusion-safety-preview/idempotency-preview",
        },
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_config_block(),
        "observability_dry_run": _v42_obs_config_block(),
        "idempotency_replay_detection_dry_run": _v43_replay_config_block(),
    }


@router.post("/validate-request")
async def validate_request(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "validate-request"))
    req = body.payload if body and body.payload is not None else _sample_request()
    _v42_rh_env = _v42_rh_envelope(req, "gear_forge_fusion_commit")
    _v42_obs_env = _v42_obs_envelope(
        "gear_forge_fusion_commit", "gear_forge_fusion_commit", "validate-request",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    _v43_replay_env = _v43_replay_envelope(
        "gear_forge_fusion_commit",
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        request_hash=_v42_rh_env.get("request_hash"),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="gear_forge_fusion_commit",
    )
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "gear_forge_fusion_commit",
        "validation": _validate_request(req),
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_env,
        "observability_dry_run": _v42_obs_env,
        "idempotency_replay_detection_dry_run": _v43_replay_env,
    }


@router.post("/guard-plan-preview")
async def guard_plan_preview(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "guard-plan-preview"))
    req = body.payload if body and body.payload is not None else _sample_request()
    _v42_rh_env = _v42_rh_envelope(req, "gear_forge_fusion_commit")
    _v42_obs_env = _v42_obs_envelope(
        "gear_forge_fusion_commit", "gear_forge_fusion_commit", "guard-plan-preview",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    _v43_replay_env = _v43_replay_envelope(
        "gear_forge_fusion_commit",
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        request_hash=_v42_rh_env.get("request_hash"),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="gear_forge_fusion_commit",
    )
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "gear_forge_fusion_commit",
        "guard_plan": _guard_plan(req),
        "validation": _validate_request(req),
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_env,
        "observability_dry_run": _v42_obs_env,
        "idempotency_replay_detection_dry_run": _v43_replay_env,
        "notes": [
            "guard_plan_is_display_only",
            "no_live_commit_in_preview",
            "no_gear_mutation_in_preview",
            "no_materials_consumed_in_preview",
            "no_currency_consumed_in_preview",
            "no_premium_gems_currency_used_in_preview",
            "no_bp_delta_triggered_in_preview",
            "no_db_write_in_preview",
        ],
    }


@router.post("/idempotency-preview")
async def idempotency_preview(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "idempotency-preview"))
    req = body.payload if body and body.payload is not None else _sample_request()
    _v42_rh_env = _v42_rh_envelope(req, "gear_forge_fusion_commit")
    _v42_obs_env = _v42_obs_envelope(
        "gear_forge_fusion_commit", "gear_forge_fusion_commit", "idempotency-preview",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    _v43_replay_env = _v43_replay_envelope(
        "gear_forge_fusion_commit",
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        request_hash=_v42_rh_env.get("request_hash"),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="gear_forge_fusion_commit",
    )
    validation = _validate_request(req)
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "gear_forge_fusion_commit",
        "idempotency_preview": _idempotency_preview(req) if validation.get("valid") else None,
        "validation": validation,
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_env,
        "observability_dry_run": _v42_obs_env,
        "idempotency_replay_detection_dry_run": _v43_replay_env,
        "live_commit_allowed": False,
    }
