"""economy_request_hash_dry_run

v42 dry-run runtime utility for the shared request hash + idempotency contract
defined in v41 (data/design/economy_safety/shared_request_hash_idempotency_contract_v1.json).

This module:
- normalizes a payload deterministically (sorted keys, stripped volatile/PII fields)
- computes a sha256 request_hash (lowercase hex, truncated to 32 chars)
- computes a server_idempotency_key (lowercase hex, truncated to 24 chars)
- builds a dry-run response envelope safe to attach to safety preview routes

No DB writes. No persistence. No mutation. No ledger. No live enforcement.
Used only by the 8 safety preview routes for response augmentation.
"""
from __future__ import annotations
import hashlib
import json
from typing import Any, Dict, Iterable, Optional

CONTRACT_NAME = "shared_request_hash_idempotency_contract_v1"
REQUEST_HASH_TRUNCATION_CHARS = 32
SERVER_IDEMPOTENCY_KEY_TRUNCATION_CHARS = 24

# Volatile fields stripped from the canonicalized payload prior to hashing.
VOLATILE_FIELDS = frozenset({
    "created_at",
    "client_received_at",
    "client_sent_at",
    "client_clock_skew_ms",
    "client_local_request_uuid",
    "telemetry_session_id",
    "telemetry_sequence_id",
    "client_device_model_string",
    "client_app_version_string",
    "client_locale",
    "client_user_agent",
})

# PII fields stripped from the canonicalized payload prior to hashing.
PII_FIELDS = frozenset({
    "email",
    "display_name",
    "ip",
    "client_ip",
    "device_id",
    "device_serial",
    "hwid",
    "push_token",
    "phone",
    "phone_number",
})

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


def _is_strippable(key: str) -> bool:
    return key in VOLATILE_FIELDS or key in PII_FIELDS


def _deep_canonicalize(value: Any) -> Any:
    """Recursively canonicalize a value: dict keys sorted, volatile/PII stripped."""
    if isinstance(value, dict):
        return {
            k: _deep_canonicalize(value[k])
            for k in sorted(value.keys())
            if not _is_strippable(k)
        }
    if isinstance(value, list):
        return [_deep_canonicalize(v) for v in value]
    return value


def canonicalize_payload_for_hash(payload: Optional[Dict[str, Any]],
                                  operation_family: str) -> Dict[str, Any]:
    """Return a canonicalized copy of ``payload`` for hashing.

    - sorted keys ascending
    - volatile fields stripped
    - PII fields stripped
    - operation_family pinned (overrides any value present in payload)
    """
    base: Dict[str, Any] = {}
    if isinstance(payload, dict):
        base = _deep_canonicalize(payload)
    # pin operation_family deterministically
    base["operation_family"] = operation_family
    # ensure sorted: re-create dict in sorted order
    return {k: base[k] for k in sorted(base.keys())}


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_request_hash(payload: Optional[Dict[str, Any]],
                         operation_family: str) -> str:
    """Compute the v41-shape request_hash (sha256, hex lowercase, truncated 32)."""
    canon = canonicalize_payload_for_hash(payload, operation_family)
    blob = _canonical_json(canon).encode("utf-8")
    digest = hashlib.sha256(blob).hexdigest().lower()
    return digest[:REQUEST_HASH_TRUNCATION_CHARS]


def compute_server_idempotency_key(payload: Optional[Dict[str, Any]],
                                   operation_family: str) -> str:
    """Compute the v41-shape server_idempotency_key (sha256, hex, truncated 24).

    Derivation: sha256(operation_family|user_id|client_idempotency_key|canonical_payload)
    """
    canon = canonicalize_payload_for_hash(payload, operation_family)
    user_id = ""
    client_idem = ""
    if isinstance(payload, dict):
        user_id = str(payload.get("user_id", "") or "")
        client_idem = str(payload.get("client_idempotency_key", "") or "")
    seed = "|".join((operation_family, user_id, client_idem, _canonical_json(canon)))
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest().lower()
    return digest[:SERVER_IDEMPOTENCY_KEY_TRUNCATION_CHARS]


def build_request_hash_dry_run_envelope(payload: Optional[Dict[str, Any]],
                                        operation_family: str) -> Dict[str, Any]:
    """Return the dry-run envelope to attach to a safety preview response.

    Safe: no DB writes, no persistence, no mutation.
    """
    return {
        "enabled": True,
        "contract": CONTRACT_NAME,
        "operation_family": operation_family,
        "request_hash": compute_request_hash(payload, operation_family),
        "server_idempotency_key_preview": compute_server_idempotency_key(payload, operation_family),
        "pii_stripped": True,
        "volatile_fields_stripped": True,
        "ledger_write_enabled": False,
        "live_enforcement_enabled": False,
        "persisted": False,
        "db_writes": 0,
        "reward_grant_enabled": False,
        "live_commit_enabled": False,
        "live_claim_enabled": False,
    }


def build_config_block() -> Dict[str, Any]:
    """Return the dry-run block to embed in /config responses."""
    return {
        "request_hash_dry_run_enabled": True,
        "request_hash_contract": CONTRACT_NAME,
        "ledger_write_enabled": False,
        "live_enforcement_enabled": False,
        "persisted": False,
        "db_writes": 0,
    }


__all__ = [
    "CONTRACT_NAME",
    "REQUEST_HASH_TRUNCATION_CHARS",
    "SERVER_IDEMPOTENCY_KEY_TRUNCATION_CHARS",
    "VOLATILE_FIELDS",
    "PII_FIELDS",
    "SUPPORTED_OPERATION_FAMILIES",
    "canonicalize_payload_for_hash",
    "compute_request_hash",
    "compute_server_idempotency_key",
    "build_request_hash_dry_run_envelope",
    "build_config_block",
]
