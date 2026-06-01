"""economy_idempotency_replay_detection_dry_run

v43 dry-run runtime utility for in-memory replay/conflict detection.

This module provides a *non-persistent*, *non-shared-across-workers*,
*TTL-bounded* idempotency replay/conflict detector for the 8 safety preview
routes. It NEVER blocks the preview request. It NEVER writes DB. It NEVER
uses Redis or filesystem. It is reset at process restart by design.

Detection states produced:
  - new_key_preview                       (first time we see this key)
  - same_key_same_hash_replay_preview     (same idem key + same hash)
  - same_key_diff_hash_conflict_preview   (same idem key + different hash)
  - missing_key_preview                   (no idem key supplied)

The cache is bounded by:
  - MAX_ENTRIES_DEFAULT = 256 (LRU evict-oldest when over)
  - TTL_SECONDS_DEFAULT = 60  (expire on read or insert)

The envelope returned is shaped to be embeddable in safety preview HTTP
responses. It contains no PII and no raw payload.
"""
from __future__ import annotations
import threading
import time
from collections import OrderedDict
from typing import Any, Dict, Optional

MAX_ENTRIES_DEFAULT = 256
TTL_SECONDS_DEFAULT = 60

DETECTION_STATUSES = (
    "new_key_preview",
    "same_key_same_hash_replay_preview",
    "same_key_diff_hash_conflict_preview",
    "missing_key_preview",
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

_LOCK = threading.Lock()
# OrderedDict so we can pop the oldest entry in O(1) once we reach the cap.
# Key: (operation_family, server_idempotency_key)
# Value: {"request_hash": str, "expires_at": float}
_CACHE: "OrderedDict[tuple, Dict[str, Any]]" = OrderedDict()

_MAX_ENTRIES = MAX_ENTRIES_DEFAULT
_TTL_SECONDS = TTL_SECONDS_DEFAULT


def _now() -> float:
    return time.monotonic()


def _evict_expired_locked(now_ts: float) -> None:
    """Pop all expired entries. Caller must hold _LOCK."""
    if not _CACHE:
        return
    expired_keys = [k for k, v in _CACHE.items() if v.get("expires_at", 0.0) <= now_ts]
    for k in expired_keys:
        _CACHE.pop(k, None)


def _evict_oldest_if_full_locked() -> None:
    """Evict the oldest insertion-order entry while over the cap."""
    while len(_CACHE) > _MAX_ENTRIES:
        _CACHE.popitem(last=False)


def _detect_and_record(operation_family: str,
                      server_idempotency_key: Optional[str],
                      request_hash: Optional[str]) -> str:
    """Core detector: classify request and update the in-memory cache.

    Always returns one of DETECTION_STATUSES. NEVER blocks. NEVER raises.
    """
    if not server_idempotency_key:
        return "missing_key_preview"
    if not request_hash:
        # No hash to compare against. Treat as missing key from a detection
        # standpoint to avoid storing partial state.
        return "missing_key_preview"

    key = (operation_family, server_idempotency_key)
    now_ts = _now()
    with _LOCK:
        _evict_expired_locked(now_ts)
        existing = _CACHE.get(key)
        if existing is None:
            _CACHE[key] = {
                "request_hash": request_hash,
                "expires_at": now_ts + _TTL_SECONDS,
            }
            _evict_oldest_if_full_locked()
            return "new_key_preview"
        # Refresh TTL & re-anchor LRU regardless of outcome.
        _CACHE.move_to_end(key, last=True)
        existing["expires_at"] = now_ts + _TTL_SECONDS
        if existing.get("request_hash") == request_hash:
            return "same_key_same_hash_replay_preview"
        return "same_key_diff_hash_conflict_preview"


def build_replay_detection_dry_run_envelope(operation_family: str,
                                            server_idempotency_key: Optional[str] = None,
                                            request_hash: Optional[str] = None,
                                            client_idempotency_key_present: bool = False,
                                            user_id: Optional[str] = None,
                                            server_id: Optional[str] = None,
                                            operation_type: Optional[str] = None) -> Dict[str, Any]:
    """Return the dry-run replay/conflict envelope safe to embed in responses.

    The envelope NEVER blocks the preview request and NEVER writes DB.
    The detector cache is in-memory only, TTL-bounded, and not shared across
    workers or process restarts.
    """
    op_family = str(operation_family or "")
    detection_status = _detect_and_record(op_family, server_idempotency_key, request_hash)
    same_same = detection_status == "same_key_same_hash_replay_preview"
    same_diff = detection_status == "same_key_diff_hash_conflict_preview"
    new_key = detection_status == "new_key_preview"
    missing = detection_status == "missing_key_preview"
    return {
        "enabled": True,
        "dry_run_only": True,
        "persistent_ledger_enabled": False,
        "redis_enabled": False,
        "db_writes": 0,
        "max_entries": _MAX_ENTRIES,
        "ttl_seconds": _TTL_SECONDS,
        "operation_family": op_family,
        "operation_type": operation_type or op_family,
        "server_id": server_id,
        "client_idempotency_key_present": bool(client_idempotency_key_present),
        "server_idempotency_key_present": bool(server_idempotency_key),
        "request_hash_present": bool(request_hash),
        "detection_status": detection_status,
        "new_key_detected": new_key,
        "same_key_same_hash_detected": same_same,
        "same_key_diff_hash_detected": same_diff,
        "conflict_detected": same_diff,
        "missing_key_detected": missing,
        "would_replay_live": same_same,
        "would_block_live": same_diff,
        "would_pass_live": new_key,
        "preview_request_blocked": False,
        "not_shared_across_workers": True,
        "not_durable_across_restart": True,
        "live_enforcement_enabled": False,
        "persisted": False,
    }


def build_config_block() -> Dict[str, Any]:
    """Return the dry-run replay detection block to embed in /config responses."""
    return {
        "enabled": True,
        "dry_run_only": True,
        "persistent_ledger_enabled": False,
        "redis_enabled": False,
        "db_writes": 0,
        "max_entries": _MAX_ENTRIES,
        "ttl_seconds": _TTL_SECONDS,
        "not_shared_across_workers": True,
        "not_durable_across_restart": True,
        "live_enforcement_enabled": False,
        "detection_statuses": list(DETECTION_STATUSES),
    }


def _test_reset(max_entries: Optional[int] = None,
                ttl_seconds: Optional[float] = None) -> None:
    """Reset the in-memory cache. **For tests only**. Never exposed via HTTP.

    Optionally adjust limits to make tests deterministic.
    """
    global _MAX_ENTRIES, _TTL_SECONDS
    with _LOCK:
        _CACHE.clear()
        if max_entries is not None:
            _MAX_ENTRIES = int(max_entries)
        else:
            _MAX_ENTRIES = MAX_ENTRIES_DEFAULT
        if ttl_seconds is not None:
            _TTL_SECONDS = float(ttl_seconds)
        else:
            _TTL_SECONDS = TTL_SECONDS_DEFAULT


def _test_snapshot_size() -> int:
    """Return current cache size. **For tests only**. Never exposed via HTTP."""
    with _LOCK:
        return len(_CACHE)


__all__ = [
    "DETECTION_STATUSES",
    "MAX_ENTRIES_DEFAULT",
    "TTL_SECONDS_DEFAULT",
    "SUPPORTED_OPERATION_FAMILIES",
    "build_replay_detection_dry_run_envelope",
    "build_config_block",
]
