"""economy_observability_dry_run

v42 dry-run runtime utility for the observability foundation defined in v41:
- audit schema: data/design/economy_safety/economy_safety_observability_audit_schema_v1.json
- metrics:     data/design/economy_safety/economy_safety_observability_metrics_v1.json
- privacy:     data/design/economy_safety/economy_safety_observability_privacy_policy_v1.json

This module:
- builds an audit_event_preview safe to surface in HTTP responses (no PII, no
  persistence, no external sink)
- builds a metric_sample_preview (counter increment of 0 for invariant
  counters; preview only)
- builds a single observability_dry_run envelope combining both

No DB writes. No external sink. No persistent audit collection. No raw PII.
user_id is hashed (sha256 truncated 32) or omitted. Invariant counters remain
zero.
"""
from __future__ import annotations
import hashlib
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

AUDIT_SCHEMA_NAME = "economy_safety_observability_audit_schema_v1"
METRICS_NAME = "economy_safety_observability_metrics_v1"
PRIVACY_POLICY_NAME = "economy_safety_observability_privacy_policy_v1"

INVARIANT_ZERO_METRICS = (
    "economy_safety_db_writes_total",
    "economy_safety_live_commit_executions_total",
    "economy_safety_live_claim_executions_total",
    "economy_safety_reward_grants_total",
)

SUPPORTED_OPERATION_FAMILIES = frozenset({
    "gem_socket_commit",
    "material_raid_claim",
    "gear_forge_fusion_commit",
    "rune_scroll_talisman_commit",
    "artifact_upgrade_commit",
    "divine_weapon_upgrade_commit",
    "battle_pass_reward_claim",
    "mail_reward_claim",
})

SUPPORTED_OUTCOMES = (
    "success_preview_503",
    "rejected",
    "validation_error",
    "replay_hit",
    "conflict",
)

FORBIDDEN_PAYLOAD_KEYS = frozenset({
    "email",
    "display_name",
    "raw_user_id",
    "ip",
    "client_ip",
    "device_id",
    "device_serial",
    "hwid",
    "push_token",
    "phone",
    "phone_number",
    "raw_payload",
    "premium_currency_amount_used",
    "premium_users_gems_balance",
    "bp_delta_runtime_value",
})


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hash_user_id(user_id: Optional[str]) -> Optional[str]:
    if not user_id:
        return None
    salt = os.environ.get("ECONOMY_AUDIT_USER_SALT", "economy_audit_user_salt_dry_run_v42")
    seed = f"{salt}|{user_id}".encode("utf-8")
    return hashlib.sha256(seed).hexdigest()[:32]


def build_audit_event_preview(operation_family: str,
                              operation_type: str,
                              outcome: str = "success_preview_503",
                              request_hash: Optional[str] = None,
                              server_idempotency_key: Optional[str] = None,
                              user_id: Optional[str] = None,
                              client_idempotency_key_present: bool = False) -> Dict[str, Any]:
    """Build a single audit_event preview dict matching the v41 audit schema.

    Never persisted. Never sent to a sink. Never contains PII or raw user_id.
    """
    if outcome not in SUPPORTED_OUTCOMES:
        outcome = "success_preview_503"
    return {
        "audit_event_id": str(uuid.uuid4()),
        "audit_event_kind": "preview_invocation",
        "operation_family": operation_family,
        "operation": operation_type,
        "server_request_hash": (request_hash or "")[:32],
        "server_idempotency_key": (server_idempotency_key or "")[:24],
        "client_idempotency_key_present": bool(client_idempotency_key_present),
        "user_id_hashed": _hash_user_id(user_id),
        "started_at_utc": _now_utc_iso(),
        "completed_at_utc": _now_utc_iso(),
        "outcome": outcome,
        "db_writes": 0,
        "live_commit_executed": False,
        "live_claim_executed": False,
        "reward_granted": False,
        "safety_feature_flag_state": "enabled_preview_only",
        "persisted": False,
        "sink_emitted": False,
    }


def build_metric_sample_preview(operation_family: str,
                                route: str,
                                status: str = "preview_ok") -> Dict[str, Any]:
    """Build a non-persistent metric sample preview.

    All invariant counters remain at 0. This is a sample shape only and is
    never shipped to a Prometheus client or push gateway.
    """
    return {
        "metric_namespace": "economy_safety",
        "operation_family": operation_family,
        "route": route,
        "status": status,
        "counters": {
            "economy_safety_preview_invocations_total": 1,
            "economy_safety_db_writes_total": 0,
            "economy_safety_live_commit_executions_total": 0,
            "economy_safety_live_claim_executions_total": 0,
            "economy_safety_reward_grants_total": 0,
            "economy_safety_premium_currency_mutations_total": 0,
            "economy_safety_bp_delta_triggers_total": 0,
        },
        "invariant_counters_must_remain_zero": list(INVARIANT_ZERO_METRICS),
        "persisted": False,
        "shipped_to_external_sink": False,
    }


def build_observability_dry_run_envelope(operation_family: str,
                                         operation_type: str,
                                         route: str,
                                         outcome: str = "success_preview_503",
                                         status: str = "preview_ok",
                                         request_hash: Optional[str] = None,
                                         server_idempotency_key: Optional[str] = None,
                                         user_id: Optional[str] = None,
                                         client_idempotency_key_present: bool = False) -> Dict[str, Any]:
    """Return the dry-run observability envelope to attach to a response."""
    audit_event = build_audit_event_preview(
        operation_family=operation_family,
        operation_type=operation_type,
        outcome=outcome,
        request_hash=request_hash,
        server_idempotency_key=server_idempotency_key,
        user_id=user_id,
        client_idempotency_key_present=client_idempotency_key_present,
    )
    metric_sample = build_metric_sample_preview(
        operation_family=operation_family,
        route=route,
        status=status,
    )
    return {
        "enabled": True,
        "audit_schema": AUDIT_SCHEMA_NAME,
        "metrics_catalog": METRICS_NAME,
        "privacy_policy": PRIVACY_POLICY_NAME,
        "audit_event_preview_created": True,
        "audit_event_preview": audit_event,
        "metric_sample_preview_created": True,
        "metric_sample_preview": metric_sample,
        "persistent_audit_write_enabled": False,
        "alert_sink_live_enabled": False,
        "dashboard_runtime_deployed": False,
        "external_sink_shipping_enabled": False,
        "raw_pii_in_payload": False,
        "db_writes": 0,
    }


def build_config_block() -> Dict[str, Any]:
    """Return the dry-run observability block to embed in /config responses."""
    return {
        "enabled": True,
        "audit_schema": AUDIT_SCHEMA_NAME,
        "metrics_catalog": METRICS_NAME,
        "privacy_policy": PRIVACY_POLICY_NAME,
        "persistent_audit_write_enabled": False,
        "alert_sink_live_enabled": False,
        "dashboard_runtime_deployed": False,
        "external_sink_shipping_enabled": False,
        "db_writes": 0,
    }


__all__ = [
    "AUDIT_SCHEMA_NAME",
    "METRICS_NAME",
    "PRIVACY_POLICY_NAME",
    "INVARIANT_ZERO_METRICS",
    "SUPPORTED_OPERATION_FAMILIES",
    "SUPPORTED_OUTCOMES",
    "FORBIDDEN_PAYLOAD_KEYS",
    "build_audit_event_preview",
    "build_metric_sample_preview",
    "build_observability_dry_run_envelope",
    "build_config_block",
]
