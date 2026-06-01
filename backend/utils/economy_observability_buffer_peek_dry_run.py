"""economy_observability_buffer_peek_dry_run

v44 Track B dry-run runtime utility: in-memory ring buffer accumulator for
observability previews. Stores PII-safe summaries of audit_event_preview
and metric_sample_preview (NEVER raw payload, NEVER PII).

No DB. No Redis. No filesystem. No persistent ledger. Not shared across
workers. Not durable across restart. Bounded by:
  - MAX_ENTRIES_PER_FAMILY_DEFAULT = 100
  - TTL_SECONDS_DEFAULT = 300

Exposes:
  - record_observability_preview(operation_family, audit_event_preview,
                                  metric_sample_preview)
  - build_buffer_status_block(operation_family=None)
  - peek_buffer(operation_family=None, limit=25)
  - _test_reset(...) (tests only)
"""
from __future__ import annotations
import threading
import time
from collections import OrderedDict, deque
from typing import Any, Deque, Dict, Iterable, List, Optional

MAX_ENTRIES_PER_FAMILY_DEFAULT = 100
TTL_SECONDS_DEFAULT = 300

SUPPORTED_OPERATION_FAMILIES = frozenset({
    "gem_socket_commit", "material_raid_claim",
    "gear_forge_fusion_commit", "rune_scroll_talisman_commit",
    "artifact_upgrade_commit", "divine_weapon_upgrade_commit",
    "battle_pass_reward_claim", "mail_reward_claim",
})

# Fields that we explicitly DO NOT copy from the audit_event_preview.
FORBIDDEN_AUDIT_FIELDS = frozenset({
    "raw_payload", "email", "display_name", "raw_user_id",
    "ip", "client_ip", "device_id", "device_serial", "hwid",
    "push_token", "phone", "phone_number",
})

_LOCK = threading.Lock()
# OrderedDict[family -> deque of entries]
_BUFFERS: "OrderedDict[str, Deque[Dict[str, Any]]]" = OrderedDict()
_MAX_ENTRIES_PER_FAMILY = MAX_ENTRIES_PER_FAMILY_DEFAULT
_TTL_SECONDS = TTL_SECONDS_DEFAULT


def _now() -> float:
    return time.monotonic()


def _purge_expired_locked(family: str, now_ts: float) -> None:
    buf = _BUFFERS.get(family)
    if buf is None:
        return
    while buf and buf[0].get("expires_at", 0.0) <= now_ts:
        buf.popleft()


def _scrub_audit_summary(audit_event_preview: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(audit_event_preview, dict):
        return {}
    safe: Dict[str, Any] = {}
    for k in (
        "audit_event_id", "audit_event_kind", "operation_family", "operation",
        "server_request_hash", "server_idempotency_key",
        "client_idempotency_key_present", "user_id_hashed",
        "outcome", "db_writes", "live_commit_executed", "live_claim_executed",
        "reward_granted", "safety_feature_flag_state",
        "started_at_utc", "completed_at_utc",
    ):
        if k in audit_event_preview and k not in FORBIDDEN_AUDIT_FIELDS:
            safe[k] = audit_event_preview[k]
    return safe


def _scrub_metric_summary(metric_sample_preview: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(metric_sample_preview, dict):
        return {}
    out: Dict[str, Any] = {}
    for k in (
        "metric_namespace", "operation_family", "route", "status",
        "persisted", "shipped_to_external_sink",
    ):
        if k in metric_sample_preview:
            out[k] = metric_sample_preview[k]
    counters = metric_sample_preview.get("counters") or {}
    if isinstance(counters, dict):
        out["counters_invariant_zero_status"] = {
            k: counters.get(k, 0) for k in (
                "economy_safety_db_writes_total",
                "economy_safety_live_commit_executions_total",
                "economy_safety_live_claim_executions_total",
                "economy_safety_reward_grants_total",
            )
        }
    return out


def record_observability_preview(operation_family: str,
                                 audit_event_preview: Optional[Dict[str, Any]] = None,
                                 metric_sample_preview: Optional[Dict[str, Any]] = None,
                                 route_name: Optional[str] = None,
                                 detection_summaries: Optional[Dict[str, Any]] = None) -> None:
    """Append a PII-safe summary entry to the buffer for the given family.

    No DB write. No external sink. No raw payload. Never raises.
    """
    op_family = str(operation_family or "")
    audit_safe = _scrub_audit_summary(audit_event_preview)
    metric_safe = _scrub_metric_summary(metric_sample_preview)
    entry: Dict[str, Any] = {
        "created_at": _now(),
        "expires_at": _now() + _TTL_SECONDS,
        "operation_family": op_family,
        "operation_type": audit_safe.get("operation") or op_family,
        "route_name": str(route_name or ""),
        "audit_summary": audit_safe,
        "metric_summary": metric_safe,
        "request_hash_present": bool(audit_safe.get("server_request_hash")),
        "server_idempotency_key_present": bool(audit_safe.get("server_idempotency_key")),
        "client_idempotency_key_present": bool(audit_safe.get("client_idempotency_key_present")),
        "decision": (detection_summaries or {}).get("decision", "preview_ok"),
        "blocked_reason_codes": list((detection_summaries or {}).get("blocked_reason_codes", [])),
        "detection_summaries": detection_summaries or {},
        "pii_safe": True,
        "db_writes": 0,
        "persisted": False,
    }
    with _LOCK:
        if op_family not in _BUFFERS:
            _BUFFERS[op_family] = deque(maxlen=_MAX_ENTRIES_PER_FAMILY)
        else:
            buf = _BUFFERS[op_family]
            if buf.maxlen != _MAX_ENTRIES_PER_FAMILY:
                # Rebuild deque with current max
                _BUFFERS[op_family] = deque(buf, maxlen=_MAX_ENTRIES_PER_FAMILY)
        _BUFFERS[op_family].append(entry)


def _gather_for_family_locked(family: str, limit: int) -> List[Dict[str, Any]]:
    buf = _BUFFERS.get(family)
    if not buf:
        return []
    now_ts = _now()
    _purge_expired_locked(family, now_ts)
    items = list(buf)
    return items[-int(max(limit, 0)):]


def peek_buffer(operation_family: Optional[str] = None,
                limit: int = 25) -> Dict[str, Any]:
    """Return a PII-safe snapshot of the buffer. Read-only."""
    limit_i = int(max(0, min(int(limit), _MAX_ENTRIES_PER_FAMILY)))
    with _LOCK:
        out_families: Dict[str, List[Dict[str, Any]]] = {}
        if operation_family is None:
            for fam in list(_BUFFERS.keys()):
                out_families[fam] = _gather_for_family_locked(fam, limit_i)
        else:
            out_families[str(operation_family)] = _gather_for_family_locked(str(operation_family), limit_i)
        sizes = {fam: len(_BUFFERS.get(fam) or []) for fam in out_families}
    return {
        "enabled": True,
        "dry_run_only": True,
        "persistent_ledger_enabled": False,
        "redis_enabled": False,
        "db_writes": 0,
        "max_entries_per_family": _MAX_ENTRIES_PER_FAMILY,
        "ttl_seconds": _TTL_SECONDS,
        "limit_applied": limit_i,
        "sizes_by_family": sizes,
        "entries_by_family": out_families,
        "pii_safe": True,
        "not_shared_across_workers": True,
        "not_durable_across_restart": True,
    }


def build_buffer_status_block(operation_family: Optional[str] = None) -> Dict[str, Any]:
    with _LOCK:
        if operation_family is None:
            sizes = {fam: len(buf) for fam, buf in _BUFFERS.items()}
        else:
            sizes = {str(operation_family): len(_BUFFERS.get(str(operation_family)) or [])}
    return {
        "enabled": True,
        "dry_run_only": True,
        "persistent_ledger_enabled": False,
        "redis_enabled": False,
        "db_writes": 0,
        "max_entries_per_family": _MAX_ENTRIES_PER_FAMILY,
        "ttl_seconds": _TTL_SECONDS,
        "sizes_by_family": sizes,
        "pii_safe": True,
        "not_shared_across_workers": True,
        "not_durable_across_restart": True,
    }


def _test_reset(max_entries_per_family: Optional[int] = None,
                ttl_seconds: Optional[float] = None) -> None:
    global _MAX_ENTRIES_PER_FAMILY, _TTL_SECONDS
    with _LOCK:
        _BUFFERS.clear()
        _MAX_ENTRIES_PER_FAMILY = int(max_entries_per_family) if max_entries_per_family is not None else MAX_ENTRIES_PER_FAMILY_DEFAULT
        _TTL_SECONDS = float(ttl_seconds) if ttl_seconds is not None else TTL_SECONDS_DEFAULT


__all__ = [
    "MAX_ENTRIES_PER_FAMILY_DEFAULT", "TTL_SECONDS_DEFAULT",
    "SUPPORTED_OPERATION_FAMILIES",
    "record_observability_preview", "peek_buffer",
    "build_buffer_status_block",
]
