"""PROJECT_DIVINE_WEAPON_UPGRADE_COMMIT_SAFETY_HARDENING_PACK (v39 Track B).

Preview-only/gated safety layer for the FUTURE Divine Weapon unlock/upgrade/
awakening commit. Strictly preview-gated. No live commit. No DB write.
No divine weapon mutation. No hero copy consumption. No material/currency
consumption. No premium users.gems usage. No BP Delta.

Divine Weapon canonical distinction:
- Divine Weapon exists only for native 6★ heroes.
- Divine Weapon is character-bound (exact hero binding).
- Divine Weapon does NOT replace classic gear (6★ still has normal gear).
- Divine Weapon is NOT Artifact / NOT Rune / NOT Gemme / NOT generic gear.
- Authentic mythological identity required before any live activation.
- Character Bible required before any live activation.
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

try:
    from utils.economy_alert_history_ring_buffer_dry_run import (
        build_config_block as _v47_hist_config_block,
        peek_alert_history as _v47_hist_peek,
        build_alert_history_record_envelope as _v47_hist_record,
    )
    _V47_DRY_RUN_AVAILABLE = True
except Exception:  # pragma: no cover - safe fallbacks
    _V47_DRY_RUN_AVAILABLE = False

    def _v47_hist_config_block():  # type: ignore
        return {"enabled": False, "dry_run_only": True, "rolling_windows_seconds": [60, 300, 900], "buffer_capacity": 1024, "alert_sink_live_enabled": False, "alert_dispatched": False, "db_writes": 0, "persisted": False, "live_enforcement_enabled": False, "preview_request_blocked": False, "external_sink_used": False}

    def _v47_hist_peek(operation_family=None, limit=25):  # type: ignore
        return {"enabled": False, "dry_run_only": True, "operation_family": operation_family, "windows": [], "recent_entries": [], "buffer_size_current": 0, "buffer_capacity": 1024, "alert_sink_live_enabled": False, "alert_dispatched": False, "db_writes": 0, "persisted": False, "live_enforcement_enabled": False, "preview_request_blocked": False}

    def _v47_hist_record(operation_family, alert_evaluation=None, route_name=None):  # type: ignore
        return {"enabled": False, "dry_run_only": True, "operation_family": operation_family, "route": route_name, "entry_id_preview": None, "recorded_overall_level": "ok", "alert_sink_live_enabled": False, "alert_dispatched": False, "db_writes": 0, "persisted": False, "live_enforcement_enabled": False, "preview_request_blocked": False}

FEATURE_FLAG = "DIVINE_WEAPON_UPGRADE_SAFETY_PREVIEW_ENABLED"
CONTRACT_VERSION = "divine_weapon_upgrade_safety_preview_v1"
RUNTIME_MODE_TAG = "divine_weapon_upgrade_safety_preview_gated_no_live_commit"

CANONICAL_DISTINCTION = {
    "divine_weapon_is": "character-bound personal weapon/relic for native 6_star heroes",
    "divine_weapon_native_6_star_only": True,
    "divine_weapon_is_character_bound": True,
    "divine_weapon_is_not_generic_gear": True,
    "divine_weapon_is_not_artifact": True,
    "divine_weapon_is_not_rune_or_gem": True,
    "divine_weapon_authentic_mythological_identity_required_before_live": True,
    "divine_weapon_character_bible_required_before_live": True,
}

router = APIRouter(
    prefix="/api/divine-weapon-upgrade-safety-preview",
    tags=["divine_weapon_upgrade_safety_preview"],
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
        "divine_weapon_mutation_enabled": False,
        "hero_copy_consumption_enabled": False,
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
        "character_bible_changed": False,
        "hero_final_numbers_changed": False,
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
        "divine_weapon_mutation_enabled": False,
        "hero_copy_consumption_enabled": False,
        "materials_consumed": False,
        "currency_consumed": False,
        "premium_gems_currency_used": False,
        "bp_delta_triggered": False,
        "db_writes": 0,
        "canonical_distinction": CANONICAL_DISTINCTION,
    }


def _idem(seed: str) -> str:
    return "idem_" + hashlib.sha256(f"divine_weapon_upgrade_safety|{seed}".encode()).hexdigest()[:24]


ALLOWED_OPERATION_TYPES = (
    "divine_weapon_unlock_preview",
    "divine_weapon_upgrade",
    "divine_weapon_awaken_preview",
)


def _sample_request() -> Dict[str, Any]:
    return {
        "request_id": "req_divine_weapon_preview_static_v1",
        "idempotency_key": "client_idem_static_v1",
        "operation_type": "divine_weapon_upgrade",
        "operation_family": "divine_weapon_upgrade_commit",
        "user_id": "user_preview_static",
        "server_id": "server_s1_preview_static",
        "hero_instance_id": "hero_native6_preview_static_v1",
        "hero_id": "hero_native6_static",
        "divine_weapon_id": "divine_weapon_native6_static_v1",
        "target_stage": 1,
        "target_level": 5,
        "fodder_hero_copy_instance_ids": [],
        "expected_hero_version": 1,
        "expected_divine_weapon_version": 1,
        "expected_materials_version": 1,
        "client_trace_id": "trace_preview_static_v1",
        "created_at": "2026-05-31T21:30:00Z",
    }


GUARD_CHECKS = [
    "auth_required",
    "user_owns_hero",
    "hero_is_native_6_star",
    "hero_has_divine_weapon_definition",
    "divine_weapon_bound_to_exact_hero",
    "divine_weapon_is_not_generic_gear",
    "divine_weapon_is_not_artifact",
    "divine_weapon_is_not_rune_or_gem",
    "target_stage_valid",
    "target_level_valid",
    "upgrade_recipe_valid",
    "dedicated_material_cost_policy_defined_but_not_charged",
    "hero_copy_cost_policy_defined_but_not_consumed",
    "fodder_hero_copies_owned_if_required_future",
    "fodder_hero_copies_not_locked",
    "fodder_hero_copies_not_in_active_team",
    "fodder_hero_copies_not_in_pvp_defense",
    "fodder_hero_copies_not_in_guild_war_defense",
    "authentic_mythological_identity_required_before_live",
    "character_bible_required_before_live",
    "anti_power_creep_validator_required_before_live",
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
        "operation": req.get("operation_type", "divine_weapon_upgrade"),
        "operation_family": "divine_weapon_upgrade_commit",
        "guard_checks": [
            {"name": c, "status": "would_run", "preview_only": True} for c in GUARD_CHECKS
        ],
        "live_commit_will_run_in_preview": False,
        "divine_weapon_mutation_will_apply_in_preview": False,
        "hero_copy_consumption_will_apply_in_preview": False,
        "materials_will_be_consumed_in_preview": False,
        "currency_will_be_consumed_in_preview": False,
        "premium_gems_currency_will_be_used_in_preview": False,
        "bp_delta_will_be_triggered_in_preview": False,
        "character_bible_will_be_changed_in_preview": False,
        "hero_final_numbers_will_be_changed_in_preview": False,
    }


REQUIRED_FIELDS = [
    "request_id", "idempotency_key", "operation_type", "user_id", "server_id",
    "hero_instance_id", "hero_id", "divine_weapon_id",
    "target_stage", "target_level", "fodder_hero_copy_instance_ids",
    "expected_hero_version", "expected_divine_weapon_version",
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
    fodder = req.get("fodder_hero_copy_instance_ids")
    if fodder is not None:
        if not isinstance(fodder, list):
            errors.append("fodder_hero_copy_instance_ids must be a list")
        else:
            if len(set(fodder)) != len(fodder):
                errors.append("fodder_hero_copy_instance_ids must not contain duplicates")
    return {"valid": len(errors) == 0, "errors": errors, "missing_fields": missing}


def _idempotency_preview(req: Dict[str, Any]) -> Dict[str, Any]:
    seed = "|".join(str(req.get(k)) for k in (
        "request_id", "user_id", "server_id", "hero_instance_id",
        "hero_id", "divine_weapon_id", "operation_type", "idempotency_key",
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
        "operation_family": "divine_weapon_upgrade_commit",
        "allowed_operation_types": list(ALLOWED_OPERATION_TYPES),
        "supported_guard_checks": GUARD_CHECKS,
        "canonical_distinction": CANONICAL_DISTINCTION,
        "endpoints": {
            "config": "GET /api/divine-weapon-upgrade-safety-preview/config",
            "validate_request": "POST /api/divine-weapon-upgrade-safety-preview/validate-request",
            "guard_plan_preview": "POST /api/divine-weapon-upgrade-safety-preview/guard-plan-preview",
            "idempotency_preview": "POST /api/divine-weapon-upgrade-safety-preview/idempotency-preview",
        },
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_config_block(),
        "observability_dry_run": _v42_obs_config_block(),
        "idempotency_replay_detection_dry_run": _v43_replay_config_block(),
        "client_key_replay_detection_dry_run": _v44_client_key_replay_config_block(),
        "observability_buffer_peek_dry_run": _v44_buffer_status_block(),
        "observability_aggregation_dry_run": _v45_agg_config_block(),
        "alerting_thresholds_dry_run": _v46_alert_config_block(),
        "alert_history_dry_run": _v47_hist_config_block(),
    }


@router.post("/validate-request")
async def validate_request(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "validate-request"))
    req = body.payload if body and body.payload is not None else _sample_request()
    _v42_rh_env = _v42_rh_envelope(req, "divine_weapon_upgrade_commit")
    _v42_obs_env = _v42_obs_envelope(
        "divine_weapon_upgrade_commit", "divine_weapon_upgrade_commit", "validate-request",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    _v43_replay_env = _v43_replay_envelope(
        "divine_weapon_upgrade_commit",
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        request_hash=_v42_rh_env.get("request_hash"),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="divine_weapon_upgrade_commit",
    )
    _v44_ck_env = _v44_client_key_replay_envelope(
        "divine_weapon_upgrade_commit",
        client_idempotency_key=(isinstance(req, dict) and (req.get("client_idempotency_key") or req.get("idempotency_key")) or None) if isinstance(req, dict) else None,
        request_hash=_v42_rh_env.get("request_hash"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="divine_weapon_upgrade_commit",
    )
    try:
        _v44_buffer_record(
            "divine_weapon_upgrade_commit",
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
        "operation_family": "divine_weapon_upgrade_commit",
        "validation": _validate_request(req),
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_env,
        "observability_dry_run": _v42_obs_env,
        "idempotency_replay_detection_dry_run": _v43_replay_env,
        "client_key_replay_detection_dry_run": _v44_ck_env,
        "replay_conflict_telemetry_dry_run": _v45_telemetry_envelope(
            "divine_weapon_upgrade_commit",
            detection_statuses=[
                _v43_replay_env.get("detection_status") if isinstance(_v43_replay_env, dict) else None,
                _v44_ck_env.get("detection_status") if isinstance(_v44_ck_env, dict) else None,
            ],
            route_name=(obs_env.get("path_suffix") if isinstance(obs_env, dict) else None),
        ),
        "telemetry_alert_evaluation_dry_run": _v46_evaluate_alerts(_v45_agg_snapshot("divine_weapon_upgrade_commit")),
        "alert_history_record_dry_run": _v47_hist_record(
            "divine_weapon_upgrade_commit",
            alert_evaluation=_v46_evaluate_alerts(_v45_agg_snapshot("divine_weapon_upgrade_commit")),
            route_name=(obs_env.get("path_suffix") if isinstance(obs_env, dict) else None),
        ),
        "canonical_distinction": CANONICAL_DISTINCTION,
    }


@router.post("/guard-plan-preview")
async def guard_plan_preview(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "guard-plan-preview"))
    req = body.payload if body and body.payload is not None else _sample_request()
    _v42_rh_env = _v42_rh_envelope(req, "divine_weapon_upgrade_commit")
    _v42_obs_env = _v42_obs_envelope(
        "divine_weapon_upgrade_commit", "divine_weapon_upgrade_commit", "guard-plan-preview",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    _v43_replay_env = _v43_replay_envelope(
        "divine_weapon_upgrade_commit",
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        request_hash=_v42_rh_env.get("request_hash"),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="divine_weapon_upgrade_commit",
    )
    _v44_ck_env = _v44_client_key_replay_envelope(
        "divine_weapon_upgrade_commit",
        client_idempotency_key=(isinstance(req, dict) and (req.get("client_idempotency_key") or req.get("idempotency_key")) or None) if isinstance(req, dict) else None,
        request_hash=_v42_rh_env.get("request_hash"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="divine_weapon_upgrade_commit",
    )
    try:
        _v44_buffer_record(
            "divine_weapon_upgrade_commit",
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
        "operation_family": "divine_weapon_upgrade_commit",
        "guard_plan": _guard_plan(req),
        "validation": _validate_request(req),
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_env,
        "observability_dry_run": _v42_obs_env,
        "idempotency_replay_detection_dry_run": _v43_replay_env,
        "client_key_replay_detection_dry_run": _v44_ck_env,
        "replay_conflict_telemetry_dry_run": _v45_telemetry_envelope(
            "divine_weapon_upgrade_commit",
            detection_statuses=[
                _v43_replay_env.get("detection_status") if isinstance(_v43_replay_env, dict) else None,
                _v44_ck_env.get("detection_status") if isinstance(_v44_ck_env, dict) else None,
            ],
            route_name=(obs_env.get("path_suffix") if isinstance(obs_env, dict) else None),
        ),
        "telemetry_alert_evaluation_dry_run": _v46_evaluate_alerts(_v45_agg_snapshot("divine_weapon_upgrade_commit")),
        "alert_history_record_dry_run": _v47_hist_record(
            "divine_weapon_upgrade_commit",
            alert_evaluation=_v46_evaluate_alerts(_v45_agg_snapshot("divine_weapon_upgrade_commit")),
            route_name=(obs_env.get("path_suffix") if isinstance(obs_env, dict) else None),
        ),
        "canonical_distinction": CANONICAL_DISTINCTION,
        "notes": [
            "guard_plan_is_display_only",
            "no_live_commit_in_preview",
            "no_divine_weapon_mutation_in_preview",
            "no_hero_copy_consumption_in_preview",
            "no_materials_consumed_in_preview",
            "no_currency_consumed_in_preview",
            "no_premium_gems_currency_used_in_preview",
            "no_bp_delta_triggered_in_preview",
            "no_character_bible_changed_in_preview",
            "no_hero_final_numbers_changed_in_preview",
            "no_db_write_in_preview",
        ],
    }


@router.post("/idempotency-preview")
async def idempotency_preview(body: RequestPayload) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("POST", "idempotency-preview"))
    req = body.payload if body and body.payload is not None else _sample_request()
    _v42_rh_env = _v42_rh_envelope(req, "divine_weapon_upgrade_commit")
    _v42_obs_env = _v42_obs_envelope(
        "divine_weapon_upgrade_commit", "divine_weapon_upgrade_commit", "idempotency-preview",
        outcome="success_preview_503", status="preview_ok",
        request_hash=_v42_rh_env.get("request_hash"),
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
    )
    _v43_replay_env = _v43_replay_envelope(
        "divine_weapon_upgrade_commit",
        server_idempotency_key=_v42_rh_env.get("server_idempotency_key_preview"),
        request_hash=_v42_rh_env.get("request_hash"),
        client_idempotency_key_present=bool(isinstance(req, dict) and req.get("client_idempotency_key")),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="divine_weapon_upgrade_commit",
    )
    _v44_ck_env = _v44_client_key_replay_envelope(
        "divine_weapon_upgrade_commit",
        client_idempotency_key=(isinstance(req, dict) and (req.get("client_idempotency_key") or req.get("idempotency_key")) or None) if isinstance(req, dict) else None,
        request_hash=_v42_rh_env.get("request_hash"),
        user_id=(req.get("user_id") if isinstance(req, dict) else None),
        server_id=(req.get("server_id") if isinstance(req, dict) else None),
        operation_type="divine_weapon_upgrade_commit",
    )
    try:
        _v44_buffer_record(
            "divine_weapon_upgrade_commit",
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
        "operation_family": "divine_weapon_upgrade_commit",
        "idempotency_preview": _idempotency_preview(req) if validation.get("valid") else None,
        "validation": validation,
        "safety_flags": _safety_flags(),
        "request_hash_dry_run": _v42_rh_env,
        "observability_dry_run": _v42_obs_env,
        "idempotency_replay_detection_dry_run": _v43_replay_env,
        "client_key_replay_detection_dry_run": _v44_ck_env,
        "replay_conflict_telemetry_dry_run": _v45_telemetry_envelope(
            "divine_weapon_upgrade_commit",
            detection_statuses=[
                _v43_replay_env.get("detection_status") if isinstance(_v43_replay_env, dict) else None,
                _v44_ck_env.get("detection_status") if isinstance(_v44_ck_env, dict) else None,
            ],
            route_name=(obs_env.get("path_suffix") if isinstance(obs_env, dict) else None),
        ),
        "telemetry_alert_evaluation_dry_run": _v46_evaluate_alerts(_v45_agg_snapshot("divine_weapon_upgrade_commit")),
        "alert_history_record_dry_run": _v47_hist_record(
            "divine_weapon_upgrade_commit",
            alert_evaluation=_v46_evaluate_alerts(_v45_agg_snapshot("divine_weapon_upgrade_commit")),
            route_name=(obs_env.get("path_suffix") if isinstance(obs_env, dict) else None),
        ),
        "canonical_distinction": CANONICAL_DISTINCTION,
        "live_commit_allowed": False,
    }


@router.get("/peek-buffer")
async def peek_buffer_endpoint(limit: int = 25) -> Dict[str, Any]:
    if not _flag_enabled():
        raise HTTPException(status_code=503, detail=_disabled("GET", "peek-buffer"))
    safe_limit = int(max(0, min(int(limit), 100)))
    snapshot = _v44_buffer_peek("divine_weapon_upgrade_commit", limit=safe_limit)
    return {
        "status": "preview_ok",
        "contract_version": CONTRACT_VERSION,
        "operation_family": "divine_weapon_upgrade_commit",
        "buffer": snapshot,
        "db_writes": 0,
        "persisted": False,
        "live_enforcement_enabled": False,
        "preview_request_blocked": False,
        "aggregation_snapshot": _v45_agg_snapshot("divine_weapon_upgrade_commit"),
        "alert_evaluation": _v46_evaluate_alerts(_v45_agg_snapshot("divine_weapon_upgrade_commit")),
        "alert_history_snapshot": _v47_hist_peek("divine_weapon_upgrade_commit", limit=safe_limit),
    }

