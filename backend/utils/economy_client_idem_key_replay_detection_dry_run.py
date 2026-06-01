"""economy_client_idem_key_replay_detection_dry_run

v44 Track A dry-run runtime utility for client-key-based replay/conflict
detection. Complements v43 (server-key-based) by detecting replays/conflicts
from the client's perspective: the cache key includes ONLY
(operation_family, user_id, server_id, client_idempotency_key). The hash
being compared is the v42 request_hash, which DOES include the payload.

This lets us spot:
  - same client key + same payload -> replay (idempotent)
  - same client key + diff payload -> conflict (client bug or replay attack)

No DB. No Redis. No filesystem. No persistent ledger. Never blocks the
preview request. Live enforcement disabled. Resets on process restart.
Not shared across workers.
"""
from __future__ import annotations
import threading
import time
from collections import OrderedDict
from typing import Any, Dict, Optional

MAX_ENTRIES_DEFAULT = 256
TTL_SECONDS_DEFAULT = 60
KEY_STRATEGY = "client_key_user_server_family"

DETECTION_STATUSES = (
    "new_client_key_preview",
    "same_client_key_same_hash_replay_preview",
    "same_client_key_diff_hash_conflict_preview",
    "missing_client_key_preview",
)

_LOCK = threading.Lock()
_CACHE: "OrderedDict[tuple, Dict[str, Any]]" = OrderedDict()
_MAX_ENTRIES = MAX_ENTRIES_DEFAULT
_TTL_SECONDS = TTL_SECONDS_DEFAULT


def _now() -> float:
    return time.monotonic()


def _evict_expired_locked(now_ts: float) -> None:
    if not _CACHE:
        return
    expired = [k for k, v in _CACHE.items() if v.get("expires_at", 0.0) <= now_ts]
    for k in expired:
        _CACHE.pop(k, None)


def _evict_oldest_if_full_locked() -> None:
    while len(_CACHE) > _MAX_ENTRIES:
        _CACHE.popitem(last=False)


def _detect_and_record(operation_family: str,
                      user_id: Optional[str],
                      server_id: Optional[str],
                      client_idempotency_key: Optional[str],
                      request_hash: Optional[str]) -> str:
    if not client_idempotency_key:
        return "missing_client_key_preview"
    if not request_hash:
        return "missing_client_key_preview"
    cache_key = (
        str(operation_family or ""),
        str(user_id or ""),
        str(server_id or ""),
        str(client_idempotency_key),
    )
    now_ts = _now()
    with _LOCK:
        _evict_expired_locked(now_ts)
        existing = _CACHE.get(cache_key)
        if existing is None:
            _CACHE[cache_key] = {
                "request_hash": request_hash,
                "expires_at": now_ts + _TTL_SECONDS,
            }
            _evict_oldest_if_full_locked()
            return "new_client_key_preview"
        _CACHE.move_to_end(cache_key, last=True)
        existing["expires_at"] = now_ts + _TTL_SECONDS
        if existing.get("request_hash") == request_hash:
            return "same_client_key_same_hash_replay_preview"
        return "same_client_key_diff_hash_conflict_preview"


def build_client_key_replay_detection_dry_run_envelope(
    operation_family: str,
    client_idempotency_key: Optional[str] = None,
    request_hash: Optional[str] = None,
    user_id: Optional[str] = None,
    server_id: Optional[str] = None,
    operation_type: Optional[str] = None,
) -> Dict[str, Any]:
    op_family = str(operation_family or "")
    status = _detect_and_record(op_family, user_id, server_id, client_idempotency_key, request_hash)
    same_same = status == "same_client_key_same_hash_replay_preview"
    same_diff = status == "same_client_key_diff_hash_conflict_preview"
    new_key = status == "new_client_key_preview"
    missing = status == "missing_client_key_preview"
    return {
        "enabled": True,
        "dry_run_only": True,
        "key_strategy": KEY_STRATEGY,
        "persistent_ledger_enabled": False,
        "redis_enabled": False,
        "db_writes": 0,
        "max_entries": _MAX_ENTRIES,
        "ttl_seconds": _TTL_SECONDS,
        "operation_family": op_family,
        "operation_type": operation_type or op_family,
        "client_idempotency_key_present": bool(client_idempotency_key),
        "request_hash_present": bool(request_hash),
        "detection_status": status,
        "new_client_key_detected": new_key,
        "same_client_key_same_hash_detected": same_same,
        "same_client_key_diff_hash_detected": same_diff,
        "missing_client_key_detected": missing,
        "conflict_detected": same_diff,
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
    return {
        "enabled": True,
        "dry_run_only": True,
        "key_strategy": KEY_STRATEGY,
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
    global _MAX_ENTRIES, _TTL_SECONDS
    with _LOCK:
        _CACHE.clear()
        _MAX_ENTRIES = int(max_entries) if max_entries is not None else MAX_ENTRIES_DEFAULT
        _TTL_SECONDS = float(ttl_seconds) if ttl_seconds is not None else TTL_SECONDS_DEFAULT


def _test_snapshot_size() -> int:
    with _LOCK:
        return len(_CACHE)


__all__ = [
    "DETECTION_STATUSES", "KEY_STRATEGY",
    "MAX_ENTRIES_DEFAULT", "TTL_SECONDS_DEFAULT",
    "build_client_key_replay_detection_dry_run_envelope",
    "build_config_block",
]
