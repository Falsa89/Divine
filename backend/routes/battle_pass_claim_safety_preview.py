"""PROJECT_BATTLE_PASS_REWARD_CLAIM_SAFETY_HARDENING_PACK (v40 Track A).

Preview-only/gated safety layer for the FUTURE Battle Pass reward claim.
No live claim. No reward grant. No inventory/currency/material mutation.
No premium users.gems usage. No premium Battle Pass unlock/purchase.
No VIP/shop/IAP mutation. No BP Delta runtime. Zero DB writes.
frontend/app/battlepass.tsx is MD5 locked and NOT touched.
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

FEATURE_FLAG = "BATTLE_PASS_CLAIM_SAFETY_PREVIEW_ENABLED"
CONTRACT_VERSION = "battle_pass_claim_safety_preview_v1"
RUNTIME_MODE_TAG = "battle_pass_claim_safety_preview_gated_no_live_claim"

router = APIRouter(
    prefix="/api/battle-pass-claim-safety-preview",
    tags=["battle_pass_claim_safety_preview"],
)


class RequestPayload(BaseModel):
    payload: Optional[Dict[str, Any]] = None


# v42c helpers (extracted to make public content explicit and stable):
# - _v42_operation_type(req): determines the operation_type used in the
#   observability envelope. Falls back to "battle_pass_free_reward_claim"
#   when the payload does not provide operation_type/operation.
# - _v42_client_idempotency_key_present(req): detects either
#   "client_idempotency_key" or "idempotency_key" as the idempotency key.
def _v42_operation_type(req: Dict[str, Any]) -> str:
    if isinstance(req, dict):
        return str(req.get("operation_type") or req.get("operation") or "battle_pass_free_reward_claim")
    return "battle_pass_free_reward_claim"


def _v42_client_idempotency_key_present(req: Dict[str, Any]) -> bool:
    return bool(
        isinstance(req, dict)
        and (req.get("client_idempotency_key") or req.get("idempotency_key"))
    )


def _flag_enabled() -> bool:
    return os.environ.get(FEATURE_FLAG, "").strip().lower() == "true"


def _safety_flags() -> Dict[str, Any]:
    return {
        "preview_only": True,
        "claim_enabled": False,
        "live_mutation_enabled": False,
        "reward_grant_enabled": False,
        "inventory_mutation_enabled": False,
        "currency_mutation_enabled": False,
        "premium_currency_used": False,
        "battle_pass_purchase_enabled": False,
        "premium_track_unlock_enabled": False,
        "vip_mutation_enabled": False,
        "shop_mutation_enabled": False,
        "bp_delta_triggered": False,
        "db_writes": 0,
        "exp_grant_enabled": False,
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
        "live_mutation_enabled": False,
        "reward_grant_enabled": False,
        "inventory_mutation_enabled": False,
        "currency_mutation_enabled": False,
        "premium_currency_used": False,
        "battle_pass_purchase_enabled": False,
        "premium_track_unlock_enabled": False,
        "vip_mutation_enabled": False,
        "shop_mutation_enabled": False,
        "bp_delta_triggered": False,
        "db_writes": 0,
    }


def _idem(seed: str) -> str:
    return "idem_" + hashlib.sha256(f"battle_pass_claim_safety|{seed}".encode()).hexdigest()[:24]


ALLOWED_OPERATION_TYPES = (
    "battle_pass_free_reward_claim",
    "battle_pass_premium_reward_claim_preview",
    "battle_pass_milestone_reward_claim",
    "battle_pass_season_reward_claim_preview",
)


def _sample_request() -> Dict[str, Any]:
    return {
        "request_id": "req_battle_pass_claim_preview_static_v1",
        "idempotency_key": "client_idem_static_v1",
        "operation_type": "battle_pass_free_reward_claim",
        "operation_family": "battle_pass_reward_claim",
        "user_id": "user_preview_static",
        "server_id": "server_s1_preview_static",
        "season_id": "season_preview_static_v1",
        "battle_pass_track": "free",
        "reward_tier_id": 1,
        "reward_slot_id": "slot_t1_free_static_v1",
        "expected_user_bp_version": 1,
        "expected_battle_pass_state_version": 1,
        "expected_inventory_version": 1,
        "client_trace_id": "trace_preview_static_v1",
        "created_at": "2026-05-31T22:30:00Z",
    }


GUARD_CHECKS = [
    "auth_required",
    "server_id_required",
    "user_server_binding_valid",
    "season_exists",
    "season_active_or_claim_grace_window_valid",
    "reward_tier_exists",
    "reward_slot_exists",
    "battle_pass_track_valid",
    "free_track_claim_allowed_if_unlocked",
    "premium_track_claim_requires_entitlement_but_preview_never_grants",
    "reward_not_already_claimed",
    "reward_claim_window_valid",
    "reward_payload_schema_valid",
    "no_premium_currency_consumption",
    "no_shop_purchase",
    "no_vip_unlock",
    "no_battle_pass_purchase",
    "same_request_id_not_committed",
    "idempotency_key_required",
    "conflicting_same_idempotency_key_rejected_future",
    "expected_versions_match",
    "atomic_commit_required_future",
    "ledger_entry_required_future",
    "rollback_policy_required_future",
    "audit_log_required_future",
    "bp_delta_not_triggered_in_preview",
]


def _guard_plan(req: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "operation": req.get("operation_type", "battle_pass_free_reward_claim"),
        "operation_family": "battle_pass_reward_claim",
        "guard_checks": [
            {"name": c, "status": "would_run", "preview_only": True} for c in GUARD_CHECKS
        ],
        "live_claim_will_run_in_preview": False,
        "reward_grant_will_apply_in_preview": False,
        "inventory_mutation_will_apply_in_preview": False,
        "currency_mutation_will_apply_in_preview": False,
        "premium_currency_will_be_used_in_preview": False,
        "premium_track_will_be_unlocked_in_preview": False,
        "battle_pass_purchase_will_happen_in_preview": False,
        "vip_will_be_mutated_in_preview": False,
        "shop_will_be_mutated_in_preview": False,
        "bp_delta_will_be_triggered_in_preview": False,
    }


REQUIRED_FIELDS = [
    "request_id", "idempotency_key", "operation_type", "user_id", "server_id",
    "season_id", "battle_pass_track", "reward_tier_id", "reward_slot_id",
    "expected_user_bp_version", "expected_battle_pass_state_version",
    "expected_inventory_version", "client_trace_id", "created_at",
]


def _validate_request(req: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(req, dict):
        return {"valid": False, "errors": ["payload must be an object"], "missing_fields": REQUIRED_FIELDS}
    missing = [f for f in REQUIRED_FIELDS if f not in req]
    errors = [f"missing required field: {f}" for f in missing]
    op = req.get("operation_type")
    if op is not None and op not in ALLOWED_OPERATION_TYPES:
        errors.append(f"operation_type must be one of {list(ALLOWED_OPERATION_TYPES)}")
    track = req.get("battle_pass_track")
    if track is not None and track not in ("free", "premium", "premium_plus"):
        errors.append("battle_pass_track must be one of free|premium|premium_plus")
    return {"valid": len(errors) == 0, "errors": errors, "missing_fields": missing}


def _idempotency_preview(req: Dict[str, Any]) -> Dict[str, Any]:
    seed = "|".join(str(req.get(k)) for k in (
        "request_id", "user_id", "server_id", "season_id",
        "battle_pass_track", "reward_tier_id", "reward_slot_id",
        "operation_type", "idempotency_key",
    ))
    return {
        "server_idempotency_key": _idem(seed),
        "request_hash": hashlib.sha256(seed.encode()).hexdigest()[:16],
        "retry_same_key_must_return_same_result": True,
        "conflicting_payload_with_same_key_must_be_rejected": True,
        "atomic_commit_future": True,
        "ledger_entry_future": True,
        "audit_log_future": True,
        "rollback_strategy_future": True,
        "ttl_seconds_recommended": 86400,
        "live_claim_allowed": False,
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
        "operation_family": "battle_pass_reward_claim",
        "allowed_operation_types": list(ALLOWED_OPERATION_TYPES),
        "supported_guard_checks": GUARD_CHECKS,
        "endpoints": {
            "config": "GET /api/battle-pass-claim-safety-preview/config",
            "validate_request": "POST /api/battle-pass-claim-safety-preview/validate-request",
            "guard_plan_preview": "POST /api/battle-pass-claim-safety-preview/guard-plan-preview",
            "idempotency_preview": "POST /api/battle-pass-claim-safety-preview/idempotency-preview",
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
    _v42_rh_env = _v42_rh_envelope(req, "battle_pass_reward_claim")
    _v42_obs_env = _v42_obs_envelope(
        "battle_pass_reward_claim", _v42_operation_type(req), "validate-request",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=_v42_client_idempotency_key_present(req),
    )
    _v43_replay_env = _v43_replay_envelope(
        "battle_pass_reward_claim",
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        request_hash=_v42_rh_env.get("request_hash"),
        client_idempotency_key_present=_v42_client_idempotency_key_present(req),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type=_v42_operation_type(req),
    )
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "battle_pass_reward_claim",
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
    _v42_rh_env = _v42_rh_envelope(req, "battle_pass_reward_claim")
    _v42_obs_env = _v42_obs_envelope(
        "battle_pass_reward_claim", _v42_operation_type(req), "guard-plan-preview",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=_v42_client_idempotency_key_present(req),
    )
    _v43_replay_env = _v43_replay_envelope(
        "battle_pass_reward_claim",
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        request_hash=_v42_rh_env.get("request_hash"),
        client_idempotency_key_present=_v42_client_idempotency_key_present(req),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type=_v42_operation_type(req),
    )
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "battle_pass_reward_claim",
        "guard_plan": _guard_plan(req),
        "validation": _validate_request(req),
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_env,
        "observability_dry_run": _v42_obs_env,
        "idempotency_replay_detection_dry_run": _v43_replay_env,
        "notes": [
            "guard_plan_is_display_only",
            "no_live_claim_in_preview",
            "no_reward_grant_in_preview",
            "no_inventory_mutation_in_preview",
            "no_currency_mutation_in_preview",
            "no_premium_currency_used_in_preview",
            "no_premium_track_unlock_in_preview",
            "no_battle_pass_purchase_in_preview",
            "no_vip_mutation_in_preview",
            "no_shop_mutation_in_preview",
            "no_bp_delta_triggered_in_preview",
            "no_db_write_in_preview",
        ],
    }


@router.post("/idempotency-preview")
async def idempotency_preview(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "idempotency-preview"))
    req = body.payload if body and body.payload is not None else _sample_request()
    _v42_rh_env = _v42_rh_envelope(req, "battle_pass_reward_claim")
    _v42_obs_env = _v42_obs_envelope(
        "battle_pass_reward_claim", _v42_operation_type(req), "idempotency-preview",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=_v42_client_idempotency_key_present(req),
    )
    _v43_replay_env = _v43_replay_envelope(
        "battle_pass_reward_claim",
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        request_hash=_v42_rh_env.get("request_hash"),
        client_idempotency_key_present=_v42_client_idempotency_key_present(req),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type=_v42_operation_type(req),
    )
    validation = _validate_request(req)
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "battle_pass_reward_claim",
        "idempotency_preview": _idempotency_preview(req) if validation.get("valid") else None,
        "validation": validation,
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_env,
        "observability_dry_run": _v42_obs_env,
        "idempotency_replay_detection_dry_run": _v43_replay_env,
        "live_claim_allowed": False,
    }
