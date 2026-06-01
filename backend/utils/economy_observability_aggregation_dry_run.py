"""economy_observability_aggregation_dry_run.py

v45 — Track A
Observability Ring-Buffer Aggregation (DRY-RUN, in-memory only).

Strict properties (NEVER violated):
- In-memory only. Per-process. Not shared across workers.
- Not durable across restart.
- NO DB writes. NO Redis. NO filesystem. NO external dependency.
- NO persistent ledger.
- Consumes only PII-safe summaries — never raw payload/PII/token/payment data.
- Live enforcement DISABLED. Mutation DISABLED. Reward grant DISABLED.
- Preview request must NEVER be blocked by this utility.

Public API:
- record_telemetry_event(...)            -> str (event_id_preview) | None on noop
- build_aggregation_snapshot(...)        -> dict
- build_config_block()                   -> dict
- _test_reset()                          -> None  (test/validator hook only)

Rolling windows: 60s, 300s, 900s.
Hard cap: 4096 events total (bounded ring), oldest evicted FIFO.

Telemetry statuses tracked (PII-safe summaries only):
- new_key_preview
- same_key_same_hash_replay_preview
- same_key_diff_hash_conflict_preview
- missing_key_preview
- new_client_key_preview
- same_client_key_same_hash_replay_preview
- same_client_key_diff_hash_conflict_preview
- missing_client_key_preview
"""
from __future__ import annotations

import time
import threading
from collections import deque
from typing import Any, Dict, Iterable, List, Optional

CONTRACT_VERSION = "economy_observability_aggregation_dry_run_v1"
DRY_RUN_ONLY = True
PERSISTED = False
DB_WRITES = 0
LIVE_ENFORCEMENT_ENABLED = False
PREVIEW_REQUEST_BLOCKED = False

ROLLING_WINDOWS_SECONDS = (60, 300, 900)
MAX_EVENTS = 4096

_TRACKED_STATUSES = (
    "new_key_preview",
    "same_key_same_hash_replay_preview",
    "same_key_diff_hash_conflict_preview",
    "missing_key_preview",
    "new_client_key_preview",
    "same_client_key_same_hash_replay_preview",
    "same_client_key_diff_hash_conflict_preview",
    "missing_client_key_preview",
)

_SUPPORTED_FAMILIES = (
    "gem_socket_commit",
    "material_raid_claim",
    "gear_forge_fusion_commit",
    "rune_scroll_talisman_commit",
    "artifact_upgrade_commit",
    "divine_weapon_upgrade_commit",
    "battle_pass_reward_claim",
    "mail_reward_claim",
)

_lock = threading.RLock()
# ring buffer of dict events: {ts, family, route, statuses(list[str])}
_events: "deque[Dict[str, Any]]" = deque(maxlen=MAX_EVENTS)
# monotonic counter for event_id_preview
_seq = 0


def _now() -> float:
    return time.time()


def _normalize_statuses(detection_statuses: Any) -> List[str]:
    if detection_statuses is None:
        return []
    if isinstance(detection_statuses, str):
        return [detection_statuses] if detection_statuses in _TRACKED_STATUSES else []
    if isinstance(detection_statuses, (list, tuple, set)):
        return [s for s in detection_statuses if isinstance(s, str) and s in _TRACKED_STATUSES]
    if isinstance(detection_statuses, dict):
        out: List[str] = []
        for v in detection_statuses.values():
            if isinstance(v, str) and v in _TRACKED_STATUSES:
                out.append(v)
        return out
    return []


def record_telemetry_event(
    operation_family: str,
    detection_statuses: Any = None,
    route_name: Optional[str] = None,
    db_writes: int = 0,
    reward_granted: bool = False,
    mutation_detected: bool = False,
    bp_delta_detected: bool = False,
    live_enforcement_detected: bool = False,
) -> Optional[str]:
    """Record a single telemetry event. Returns an event_id_preview string.

    All counters are observation-only. Enforces 0 DB writes / no mutation /
    no reward grant / no live enforcement: any non-zero hint is recorded
    as 'observed' counter but NEVER triggers action.
    """
    global _seq
    if not isinstance(operation_family, str) or not operation_family:
        return None
    statuses = _normalize_statuses(detection_statuses)
    try:
        dbw = int(db_writes) if db_writes is not None else 0
    except Exception:
        dbw = 0
    rg = bool(reward_granted)
    mu = bool(mutation_detected)
    bpd = bool(bp_delta_detected)
    lee = bool(live_enforcement_detected)
    with _lock:
        _seq += 1
        eid = f"agg_evt_preview_{_seq}"
        _events.append({
            "ts": _now(),
            "family": operation_family,
            "route": str(route_name) if route_name else None,
            "statuses": statuses,
            "db_writes_observed": dbw,
            "reward_granted_observed": rg,
            "mutation_observed": mu,
            "bp_delta_observed": bpd,
            "live_enforcement_observed": lee,
            "event_id_preview": eid,
        })
    return eid


def _aggregate_window(window_seconds: int, family_filter: Optional[str]) -> Dict[str, Any]:
    cutoff = _now() - float(window_seconds)
    total = 0
    counters = {s: 0 for s in _TRACKED_STATUSES}
    db_writes_obs = 0
    reward_obs = 0
    mutation_obs = 0
    bp_delta_obs = 0
    live_enf_obs = 0
    with _lock:
        for ev in _events:
            if ev["ts"] < cutoff:
                continue
            if family_filter and ev.get("family") != family_filter:
                continue
            total += 1
            for s in ev.get("statuses") or ():
                if s in counters:
                    counters[s] += 1
            db_writes_obs += int(ev.get("db_writes_observed") or 0)
            if ev.get("reward_granted_observed"):
                reward_obs += 1
            if ev.get("mutation_observed"):
                mutation_obs += 1
            if ev.get("bp_delta_observed"):
                bp_delta_obs += 1
            if ev.get("live_enforcement_observed"):
                live_enf_obs += 1
    return {
        "window_seconds": int(window_seconds),
        "total_events": int(total),
        "new_key_count": int(counters["new_key_preview"]),
        "replay_same_hash_count": int(
            counters["same_key_same_hash_replay_preview"] + counters["same_client_key_same_hash_replay_preview"]
        ),
        "conflict_diff_hash_count": int(
            counters["same_key_diff_hash_conflict_preview"] + counters["same_client_key_diff_hash_conflict_preview"]
        ),
        "missing_key_count": int(
            counters["missing_key_preview"] + counters["missing_client_key_preview"]
        ),
        "new_client_key_count": int(counters["new_client_key_preview"]),
        "status_breakdown": dict(counters),
        "db_writes_observed_total": int(db_writes_obs),
        "reward_grants_observed_total": int(reward_obs),
        "mutation_observed_total": int(mutation_obs),
        "bp_delta_observed_total": int(bp_delta_obs),
        "live_enforcement_observed_total": int(live_enf_obs),
        "persisted": PERSISTED,
        "db_writes": DB_WRITES,
    }


def build_aggregation_snapshot(operation_family: Optional[str] = None) -> Dict[str, Any]:
    """Return rolling-window aggregation snapshot. PII-safe."""
    fam = operation_family if (isinstance(operation_family, str) and operation_family) else None
    windows = [_aggregate_window(w, fam) for w in ROLLING_WINDOWS_SECONDS]
    with _lock:
        buffer_size = len(_events)
    return {
        "enabled": True,
        "contract_version": CONTRACT_VERSION,
        "dry_run_only": DRY_RUN_ONLY,
        "operation_family": fam,
        "rolling_windows_seconds": list(ROLLING_WINDOWS_SECONDS),
        "windows": windows,
        "buffer_size_current": int(buffer_size),
        "buffer_capacity": int(MAX_EVENTS),
        "persisted": PERSISTED,
        "db_writes": DB_WRITES,
        "live_enforcement_enabled": LIVE_ENFORCEMENT_ENABLED,
        "preview_request_blocked": PREVIEW_REQUEST_BLOCKED,
        "pii_safe": True,
        "raw_payload_captured": False,
        "supported_families": list(_SUPPORTED_FAMILIES),
        "tracked_statuses": list(_TRACKED_STATUSES),
    }


def build_config_block() -> Dict[str, Any]:
    """Configuration block exposed in /config envelopes."""
    return {
        "enabled": True,
        "contract_version": CONTRACT_VERSION,
        "dry_run_only": DRY_RUN_ONLY,
        "rolling_windows_seconds": list(ROLLING_WINDOWS_SECONDS),
        "buffer_capacity": int(MAX_EVENTS),
        "persisted": PERSISTED,
        "db_writes": DB_WRITES,
        "live_enforcement_enabled": LIVE_ENFORCEMENT_ENABLED,
        "preview_request_blocked": PREVIEW_REQUEST_BLOCKED,
        "pii_safe": True,
        "raw_payload_captured": False,
        "supported_families": list(_SUPPORTED_FAMILIES),
        "tracked_statuses": list(_TRACKED_STATUSES),
    }


def build_replay_conflict_telemetry_envelope(
    operation_family: str,
    detection_statuses: Any = None,
    route_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the per-response envelope to be embedded in POST routes.

    This RECORDS a telemetry event as a side-effect AND returns a PII-safe
    classification envelope suitable for embedding in the JSON response.
    """
    statuses = _normalize_statuses(detection_statuses)
    eid = record_telemetry_event(
        operation_family=operation_family,
        detection_statuses=statuses,
        route_name=route_name,
        db_writes=0,
        reward_granted=False,
        mutation_detected=False,
        bp_delta_detected=False,
        live_enforcement_detected=False,
    )
    return {
        "enabled": True,
        "contract_version": CONTRACT_VERSION,
        "dry_run_only": DRY_RUN_ONLY,
        "operation_family": str(operation_family) if operation_family else None,
        "route": route_name,
        "statuses": statuses,
        "event_id_preview": eid,
        "persisted": PERSISTED,
        "db_writes": DB_WRITES,
        "live_enforcement_enabled": LIVE_ENFORCEMENT_ENABLED,
        "preview_request_blocked": PREVIEW_REQUEST_BLOCKED,
        "pii_safe": True,
        "raw_payload_captured": False,
    }


def _test_reset() -> None:
    """Validator/test hook: clear the in-memory ring buffer. NEVER call at runtime."""
    global _seq
    with _lock:
        _events.clear()
        _seq = 0
