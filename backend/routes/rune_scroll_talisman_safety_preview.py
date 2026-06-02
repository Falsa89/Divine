"""PROJECT_RUNE_SCROLL_TALISMAN_COMMIT_SAFETY_HARDENING_PACK (v38 Track B).

Preview-only/gated safety layer for the FUTURE Rune/Scroll/Talisman commit.
Rune = scroll/talismani/pergamene/sigilli sull'eroe. NON Gemme. NON Artifact.
NON Divine Weapon.
Strictly preview-gated. No live commit. No DB write. No hero rune slot
mutation. No rune inventory mutation. No material/currency consumption.
No premium users.gems usage. No BP Delta.
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

try:
    from utils.economy_client_idem_key_replay_detection_dry_run import (
        build_client_key_replay_detection_dry_run_envelope as _v44_client_key_replay_envelope,
        build_config_block as _v44_client_key_replay_config_block,
    )
    from utils.economy_observability_buffer_peek_dry_run import (
        record_observability_preview as _v44_buffer_record,
        peek_buffer as _v44_buffer_peek,
        build_buffer_status_block as _v44_buffer_status_block,
    )
    _V44_DRY_RUN_AVAILABLE = True
except Exception:  # pragma: no cover - safe fallbacks
    _V44_DRY_RUN_AVAILABLE = False

    def _v44_client_key_replay_envelope(*_a, **_kw):  # type: ignore
        return {"enabled": False, "dry_run_only": True, "detection_status": "missing_client_key_preview", "db_writes": 0, "live_enforcement_enabled": False, "preview_request_blocked": False}

    def _v44_client_key_replay_config_block():  # type: ignore
        return {"enabled": False, "dry_run_only": True, "db_writes": 0, "live_enforcement_enabled": False}

    def _v44_buffer_record(*_a, **_kw):  # type: ignore
        return None

    def _v44_buffer_peek(*_a, **_kw):  # type: ignore
        return {"enabled": False, "entries_by_family": {}, "sizes_by_family": {}, "db_writes": 0}

    def _v44_buffer_status_block(*_a, **_kw):  # type: ignore
        return {"enabled": False, "sizes_by_family": {}, "db_writes": 0}

try:
    from utils.economy_observability_aggregation_dry_run import (
        build_config_block as _v45_agg_config_block,
        build_aggregation_snapshot as _v45_agg_snapshot,
        build_replay_conflict_telemetry_envelope as _v45_telemetry_envelope,
    )
    _V45_DRY_RUN_AVAILABLE = True
except Exception:  # pragma: no cover - safe fallbacks
    _V45_DRY_RUN_AVAILABLE = False

    def _v45_agg_config_block():  # type: ignore
        return {"enabled": False, "dry_run_only": True, "db_writes": 0, "live_enforcement_enabled": False, "preview_request_blocked": False, "persisted": False}

    def _v45_agg_snapshot(*_a, **_kw):  # type: ignore
        return {"enabled": False, "dry_run_only": True, "windows": [], "db_writes": 0, "persisted": False}

    def _v45_telemetry_envelope(operation_family, detection_statuses=None, route_name=None):  # type: ignore
        return {"enabled": False, "dry_run_only": True, "operation_family": operation_family, "route": route_name, "statuses": [], "event_id_preview": None, "db_writes": 0, "persisted": False, "live_enforcement_enabled": False, "preview_request_blocked": False}

try:
    from utils.economy_telemetry_alerting_thresholds_dry_run import (
        build_alerting_thresholds_config as _v46_alert_config_block,
        evaluate_alerts_from_snapshot as _v46_evaluate_alerts,
    )
    _V46_DRY_RUN_AVAILABLE = True
except Exception:  # pragma: no cover - safe fallbacks
    _V46_DRY_RUN_AVAILABLE = False

    def _v46_alert_config_block():  # type: ignore
        return {"enabled": False, "dry_run_only": True, "thresholds": {}, "alert_sink_live_enabled": False, "alert_dispatched": False, "db_writes": 0, "persisted": False, "live_enforcement_enabled": False, "preview_request_blocked": False, "external_sink_used": False}

    def _v46_evaluate_alerts(_snap):  # type: ignore
        return {"enabled": False, "dry_run_only": True, "evaluated": False, "overall_level": "ok", "alerts": [], "alert_sink_live_enabled": False, "alert_dispatched": False, "db_writes": 0, "persisted": False, "live_enforcement_enabled": False, "preview_request_blocked": False}

FEATURE_FLAG = "RUNE_SCROLL_TALISMAN_SAFETY_PREVIEW_ENABLED"
CONTRACT_VERSION = "rune_scroll_talisman_safety_preview_v1"
RUNTIME_MODE_TAG = "rune_scroll_talisman_safety_preview_gated_no_live_commit"

CANONICAL_DISTINCTION = {
    "rune_is": "scroll/talismani/pergamene/sigilli equipped on the hero",
    "rune_is_not_gemme": True,
    "rune_is_not_artifact": True,
    "rune_is_not_divine_weapon": True,
    "gemme_belong_to_gear_sockets": True,
}

router = APIRouter(
    prefix="/api/rune-scroll-talisman-safety-preview",
    tags=["rune_scroll_talisman_safety_preview"],
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
        "hero_rune_slot_mutation_enabled": False,
        "rune_inventory_mutation_enabled": False,
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
        "hero_rune_slot_mutation_enabled": False,
        "rune_inventory_mutation_enabled": False,
        "materials_consumed": False,
        "currency_consumed": False,
        "premium_gems_currency_used": False,
        "bp_delta_triggered": False,
        "db_writes": 0,
        "canonical_distinction": CANONICAL_DISTINCTION,
    }


def _idem(seed: str) -> str:
    return "idem_" + hashlib.sha256(f"rune_scroll_talisman_safety|{seed}".encode()).hexdigest()[:24]


ALLOWED_OPERATION_TYPES = (
    "rune_equip", "rune_replace", "rune_unsocket", "rune_fuse", "rune_upgrade",
)


def _sample_request() -> Dict[str, Any]:
    return {
        "request_id": "req_rune_scroll_talisman_preview_static_v1",
        "idempotency_key": "client_idem_static_v1",
        "operation_type": "rune_equip",
        "operation_family": "rune_scroll_talisman_commit",
        "user_id": "user_preview_static",
        "server_id": "server_s1_preview_static",
        "hero_instance_id": "hero_preview_static_v1",
        "rune_instance_id": "rune_preview_static_v1",
        "target_slot_index": 0,
        "fodder_rune_instance_ids": [],
        "expected_hero_version": 1,
        "expected_rune_inventory_version": 1,
        "expected_materials_version": 1,
        "client_trace_id": "trace_preview_static_v1",
        "created_at": "2026-05-31T19:00:00Z",
    }


GUARD_CHECKS = [
    "auth_required",
    "user_owns_hero",
    "user_owns_rune",
    "hero_exists",
    "rune_exists",
    "rune_not_locked",
    "rune_not_favorite",
    "rune_not_equipped_elsewhere",
    "target_slot_index_valid",
    "target_slot_unlocked_by_hero_level_or_stars",
    "rune_family_valid_for_slot",
    "rune_type_valid_for_hero",
    "rune_rarity_valid",
    "rune_role_element_faction_restrictions_future",
    "fodder_runes_owned",
    "fodder_runes_not_locked",
    "fodder_runes_not_equipped",
    "no_duplicate_fodder_ids",
    "base_rune_not_in_fodder",
    "hero_not_in_active_battle_commit_window",
    "hero_pvp_defense_policy_defined",
    "hero_guild_war_defense_policy_defined",
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
        "operation": req.get("operation_type", "rune_equip"),
        "operation_family": "rune_scroll_talisman_commit",
        "guard_checks": [
            {"name": c, "status": "would_run", "preview_only": True} for c in GUARD_CHECKS
        ],
        "live_commit_will_run_in_preview": False,
        "hero_rune_slot_mutation_will_apply_in_preview": False,
        "rune_inventory_mutation_will_apply_in_preview": False,
        "materials_will_be_consumed_in_preview": False,
        "currency_will_be_consumed_in_preview": False,
        "premium_gems_currency_will_be_used_in_preview": False,
        "bp_delta_will_be_triggered_in_preview": False,
    }


REQUIRED_FIELDS = [
    "request_id", "idempotency_key", "operation_type", "user_id", "server_id",
    "hero_instance_id", "rune_instance_id", "target_slot_index",
    "fodder_rune_instance_ids",
    "expected_hero_version", "expected_rune_inventory_version",
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
    fodder = req.get("fodder_rune_instance_ids")
    if fodder is not None:
        if not isinstance(fodder, list):
            errors.append("fodder_rune_instance_ids must be a list")
        else:
            if len(set(fodder)) != len(fodder):
                errors.append("fodder_rune_instance_ids must not contain duplicates")
            if req.get("rune_instance_id") in fodder:
                errors.append("rune_instance_id must not be in fodder_rune_instance_ids")
    return {"valid": len(errors) == 0, "errors": errors, "missing_fields": missing}


def _idempotency_preview(req: Dict[str, Any]) -> Dict[str, Any]:
    seed = "|".join(str(req.get(k)) for k in (
        "request_id", "user_id", "server_id",
        "hero_instance_id", "rune_instance_id", "operation_type", "idempotency_key",
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
        "operation_family": "rune_scroll_talisman_commit",
        "allowed_operation_types": list(ALLOWED_OPERATION_TYPES),
        "supported_guard_checks": GUARD_CHECKS,
        "canonical_distinction": CANONICAL_DISTINCTION,
        "endpoints": {
            "config": "GET /api/rune-scroll-talisman-safety-preview/config",
            "validate_request": "POST /api/rune-scroll-talisman-safety-preview/validate-request",
            "guard_plan_preview": "POST /api/rune-scroll-talisman-safety-preview/guard-plan-preview",
            "idempotency_preview": "POST /api/rune-scroll-talisman-safety-preview/idempotency-preview",
        },
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_config_block(),
        "observability_dry_run": _v42_obs_config_block(),
        "idempotency_replay_detection_dry_run": _v43_replay_config_block(),
        "client_key_replay_detection_dry_run": _v44_client_key_replay_config_block(),
        "observability_buffer_peek_dry_run": _v44_buffer_status_block(),
        "observability_aggregation_dry_run": _v45_agg_config_block(),
        "alerting_thresholds_dry_run": _v46_alert_config_block(),
    }


@router.post("/validate-request")
async def validate_request(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "validate-request"))
    req = body.payload if body and body.payload is not None else _sample_request()
    _v42_rh_env = _v42_rh_envelope(req, "rune_scroll_talisman_commit")
    _v42_obs_env = _v42_obs_envelope(
        "rune_scroll_talisman_commit", "rune_scroll_talisman_commit", "validate-request",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    _v43_replay_env = _v43_replay_envelope(
        "rune_scroll_talisman_commit",
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        request_hash=_v42_rh_env.get("request_hash"),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="rune_scroll_talisman_commit",
    )
    _v44_ck_env = _v44_client_key_replay_envelope(
        "rune_scroll_talisman_commit",
        client_idempotency_key=(isinstance(req, dict) and (req.get("client_idempotency_key") or req.get("idempotency_key")) or None) if isinstance(req, dict) else None,
        request_hash=_v42_rh_env.get("request_hash"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="rune_scroll_talisman_commit",
    )
    try:
        _v44_buffer_record(
            "rune_scroll_talisman_commit",
            audit_event_preview=_v42_obs_env.get("audit_event_preview") if isinstance(_v42_obs_env, dict) else None,
            metric_sample_preview=_v42_obs_env.get("metric_sample_preview") if isinstance(_v42_obs_env, dict) else None,
            route_name="validate-request",
            detection_summaries={
                "decision": "preview_ok",
                "v43_status": _v43_replay_env.get("detection_status") if isinstance(_v43_replay_env, dict) else None,
                "v44_status": _v44_ck_env.get("detection_status") if isinstance(_v44_ck_env, dict) else None,
                "blocked_reason_codes": [],
            },
        )
    except Exception:
        pass
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "rune_scroll_talisman_commit",
        "validation": _validate_request(req),
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_env,
        "observability_dry_run": _v42_obs_env,
        "idempotency_replay_detection_dry_run": _v43_replay_env,
        "client_key_replay_detection_dry_run": _v44_ck_env,
        "replay_conflict_telemetry_dry_run": _v45_telemetry_envelope(
            "rune_scroll_talisman_commit",
            detection_statuses=[
                _v43_replay_env.get("detection_status") if isinstance(_v43_replay_env, dict) else None,
                _v44_ck_env.get("detection_status") if isinstance(_v44_ck_env, dict) else None,
            ],
            route_name=(obs_env.get("path_suffix") if isinstance(obs_env, dict) else None),
        ),
        "telemetry_alert_evaluation_dry_run": _v46_evaluate_alerts(_v45_agg_snapshot("rune_scroll_talisman_commit")),
        "canonical_distinction": CANONICAL_DISTINCTION,
    }


@router.post("/guard-plan-preview")
async def guard_plan_preview(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "guard-plan-preview"))
    req = body.payload if body and body.payload is not None else _sample_request()
    _v42_rh_env = _v42_rh_envelope(req, "rune_scroll_talisman_commit")
    _v42_obs_env = _v42_obs_envelope(
        "rune_scroll_talisman_commit", "rune_scroll_talisman_commit", "guard-plan-preview",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    _v43_replay_env = _v43_replay_envelope(
        "rune_scroll_talisman_commit",
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        request_hash=_v42_rh_env.get("request_hash"),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="rune_scroll_talisman_commit",
    )
    _v44_ck_env = _v44_client_key_replay_envelope(
        "rune_scroll_talisman_commit",
        client_idempotency_key=(isinstance(req, dict) and (req.get("client_idempotency_key") or req.get("idempotency_key")) or None) if isinstance(req, dict) else None,
        request_hash=_v42_rh_env.get("request_hash"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="rune_scroll_talisman_commit",
    )
    try:
        _v44_buffer_record(
            "rune_scroll_talisman_commit",
            audit_event_preview=_v42_obs_env.get("audit_event_preview") if isinstance(_v42_obs_env, dict) else None,
            metric_sample_preview=_v42_obs_env.get("metric_sample_preview") if isinstance(_v42_obs_env, dict) else None,
            route_name="guard-plan-preview",
            detection_summaries={
                "decision": "preview_ok",
                "v43_status": _v43_replay_env.get("detection_status") if isinstance(_v43_replay_env, dict) else None,
                "v44_status": _v44_ck_env.get("detection_status") if isinstance(_v44_ck_env, dict) else None,
                "blocked_reason_codes": [],
            },
        )
    except Exception:
        pass
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "rune_scroll_talisman_commit",
        "guard_plan": _guard_plan(req),
        "validation": _validate_request(req),
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_env,
        "observability_dry_run": _v42_obs_env,
        "idempotency_replay_detection_dry_run": _v43_replay_env,
        "client_key_replay_detection_dry_run": _v44_ck_env,
        "replay_conflict_telemetry_dry_run": _v45_telemetry_envelope(
            "rune_scroll_talisman_commit",
            detection_statuses=[
                _v43_replay_env.get("detection_status") if isinstance(_v43_replay_env, dict) else None,
                _v44_ck_env.get("detection_status") if isinstance(_v44_ck_env, dict) else None,
            ],
            route_name=(obs_env.get("path_suffix") if isinstance(obs_env, dict) else None),
        ),
        "telemetry_alert_evaluation_dry_run": _v46_evaluate_alerts(_v45_agg_snapshot("rune_scroll_talisman_commit")),
        "canonical_distinction": CANONICAL_DISTINCTION,
        "notes": [
            "guard_plan_is_display_only",
            "no_live_commit_in_preview",
            "no_hero_rune_slot_mutation_in_preview",
            "no_rune_inventory_mutation_in_preview",
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
    _v42_rh_env = _v42_rh_envelope(req, "rune_scroll_talisman_commit")
    _v42_obs_env = _v42_obs_envelope(
        "rune_scroll_talisman_commit", "rune_scroll_talisman_commit", "idempotency-preview",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    _v43_replay_env = _v43_replay_envelope(
        "rune_scroll_talisman_commit",
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        request_hash=_v42_rh_env.get("request_hash"),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="rune_scroll_talisman_commit",
    )
    _v44_ck_env = _v44_client_key_replay_envelope(
        "rune_scroll_talisman_commit",
        client_idempotency_key=(isinstance(req, dict) and (req.get("client_idempotency_key") or req.get("idempotency_key")) or None) if isinstance(req, dict) else None,
        request_hash=_v42_rh_env.get("request_hash"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="rune_scroll_talisman_commit",
    )
    try:
        _v44_buffer_record(
            "rune_scroll_talisman_commit",
            audit_event_preview=_v42_obs_env.get("audit_event_preview") if isinstance(_v42_obs_env, dict) else None,
            metric_sample_preview=_v42_obs_env.get("metric_sample_preview") if isinstance(_v42_obs_env, dict) else None,
            route_name="idempotency-preview",
            detection_summaries={
                "decision": "preview_ok",
                "v43_status": _v43_replay_env.get("detection_status") if isinstance(_v43_replay_env, dict) else None,
                "v44_status": _v44_ck_env.get("detection_status") if isinstance(_v44_ck_env, dict) else None,
                "blocked_reason_codes": [],
            },
        )
    except Exception:
        pass
    validation = _validate_request(req)
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "rune_scroll_talisman_commit",
        "idempotency_preview": _idempotency_preview(req) if validation.get("valid") else None,
        "validation": validation,
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_env,
        "observability_dry_run": _v42_obs_env,
        "idempotency_replay_detection_dry_run": _v43_replay_env,
        "client_key_replay_detection_dry_run": _v44_ck_env,
        "replay_conflict_telemetry_dry_run": _v45_telemetry_envelope(
            "rune_scroll_talisman_commit",
            detection_statuses=[
                _v43_replay_env.get("detection_status") if isinstance(_v43_replay_env, dict) else None,
                _v44_ck_env.get("detection_status") if isinstance(_v44_ck_env, dict) else None,
            ],
            route_name=(obs_env.get("path_suffix") if isinstance(obs_env, dict) else None),
        ),
        "telemetry_alert_evaluation_dry_run": _v46_evaluate_alerts(_v45_agg_snapshot("rune_scroll_talisman_commit")),
        "canonical_distinction": CANONICAL_DISTINCTION,
        "live_commit_allowed": False,
    }


@router.get("/peek-buffer")
async def peek_buffer_endpoint(limit: int = 25) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("GET", "peek-buffer"))
    safe_limit = int(max(0, min(int(limit), 100)))
    snapshot = _v44_buffer_peek("rune_scroll_talisman_commit", limit=safe_limit)
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "rune_scroll_talisman_commit",
        "buffer": snapshot,
        "db_writes": 0,
        "persisted": False,
        "live_enforcement_enabled": False,
        "preview_request_blocked": False,
        "aggregation_snapshot": _v45_agg_snapshot("rune_scroll_talisman_commit"),
        "alert_evaluation": _v46_evaluate_alerts(_v45_agg_snapshot("rune_scroll_talisman_commit")),
    }

