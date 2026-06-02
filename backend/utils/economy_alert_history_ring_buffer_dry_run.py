"""economy_alert_history_ring_buffer_dry_run.py

v47 — Track A
Alert History Ring-Buffer (DRY-RUN, in-memory only, PII-safe).

Strict properties (NEVER violated):
- In-memory only. Per-process. Not shared across workers.
- Not durable across restart.
- NO DB writes. NO Redis. NO filesystem. NO external alert dispatch.
- NO persistent ledger.
- Consumes only PII-safe alert_evaluation envelopes (v46).
- No raw payload / PII / token / payment data captured.
- Live enforcement DISABLED. Preview request must NEVER be blocked.

Public API:
- record_alert_evaluation(...)        -> str (entry_id_preview) | None
- peek_alert_history(...)             -> dict
- build_config_block()                -> dict
- build_alert_history_record_envelope(...) -> dict  (for POST responses)
- _test_reset()                       -> None  (test/validator hook only)

Rolling windows: 60s / 300s / 900s.
Hard cap: MAX_ENTRIES = 1024 (oldest evicted FIFO).
"""
from __future__ import annotations

import time
import threading
from collections import deque
from typing import Any, Dict, List, Optional

CONTRACT_VERSION = "economy_alert_history_ring_buffer_dry_run_v1"
DRY_RUN_ONLY = True
PERSISTED = False
DB_WRITES = 0
LIVE_ENFORCEMENT_ENABLED = False
PREVIEW_REQUEST_BLOCKED = False
ALERT_SINK_LIVE_ENABLED = False
ROLLING_WINDOWS_SECONDS = (60, 300, 900)
MAX_ENTRIES = 1024

_VALID_LEVELS = ("ok", "warn", "critical")

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
_entries: "deque[Dict[str, Any]]" = deque(maxlen=MAX_ENTRIES)
_seq = 0


def _now() -> float:
    return time.time()


def _safe_alerts(alerts: Any) -> List[Dict[str, Any]]:
    """Strip alerts to PII-safe minimal projection."""
    out: List[Dict[str, Any]] = []
    if not isinstance(alerts, list):
        return out
    for a in alerts:
        if not isinstance(a, dict):
            continue
        out.append({
            "metric": str(a.get("metric")) if a.get("metric") is not None else None,
            "level": a.get("level") if a.get("level") in _VALID_LEVELS else None,
            "window_seconds": int(a.get("window_seconds") or 0),
            "dispatched": False,
        })
    return out


def record_alert_evaluation(
    operation_family: str,
    alert_evaluation: Any = None,
    route_name: Optional[str] = None,
) -> Optional[str]:
    """Record a single alert_evaluation snapshot. PII-safe. No payload kept."""
    global _seq
    if not isinstance(operation_family, str) or not operation_family:
        return None
    if not isinstance(alert_evaluation, dict):
        return None
    overall = alert_evaluation.get("overall_level")
    if overall not in _VALID_LEVELS:
        overall = "ok"
    rates = alert_evaluation.get("rates") or {}
    safe_rates: Dict[str, float] = {}
    if isinstance(rates, dict):
        for k in ("replay_rate", "conflict_rate", "missing_key_rate"):
            try:
                safe_rates[k] = float(rates.get(k) or 0.0)
            except Exception:
                safe_rates[k] = 0.0
    crit_imm = bool(alert_evaluation.get("critical_immediate_observed"))
    crit_fields = alert_evaluation.get("critical_immediate_fields") or []
    safe_crit_fields = [str(x) for x in crit_fields if isinstance(x, str)]
    alerts = _safe_alerts(alert_evaluation.get("alerts"))
    with _lock:
        _seq += 1
        eid = f"alert_hist_entry_preview_{_seq}"
        _entries.append({
            "ts": _now(),
            "family": operation_family,
            "route": str(route_name) if route_name else None,
            "overall_level": overall,
            "rates": safe_rates,
            "critical_immediate_observed": crit_imm,
            "critical_immediate_fields": safe_crit_fields,
            "alerts": alerts,
            "entry_id_preview": eid,
            "dispatched": False,
        })
    return eid


def _aggregate_window(window_seconds: int, family_filter: Optional[str]) -> Dict[str, Any]:
    cutoff = _now() - float(window_seconds)
    total = 0
    by_level = {"ok": 0, "warn": 0, "critical": 0}
    crit_immediate = 0
    with _lock:
        for e in _entries:
            if e["ts"] < cutoff:
                continue
            if family_filter and e.get("family") != family_filter:
                continue
            total += 1
            lvl = e.get("overall_level")
            if lvl in by_level:
                by_level[lvl] += 1
            if e.get("critical_immediate_observed"):
                crit_immediate += 1
    return {
        "window_seconds": int(window_seconds),
        "total_entries": int(total),
        "by_level": by_level,
        "critical_immediate_count": int(crit_immediate),
        "persisted": PERSISTED,
        "db_writes": DB_WRITES,
        "dispatched": False,
    }


def peek_alert_history(operation_family: Optional[str] = None, limit: int = 25) -> Dict[str, Any]:
    """Return a PII-safe snapshot of the alert history ring buffer.

    `limit` clamped to [0, 100]. Returns rolling-window aggregations
    + the most recent `limit` entries (PII-safe projection).
    """
    try:
        safe_limit = int(limit)
    except Exception:
        safe_limit = 25
    safe_limit = max(0, min(safe_limit, 100))
    fam = operation_family if (isinstance(operation_family, str) and operation_family) else None
    windows = [_aggregate_window(w, fam) for w in ROLLING_WINDOWS_SECONDS]
    with _lock:
        if fam:
            tail = [e for e in list(_entries) if e.get("family") == fam][-safe_limit:]
        else:
            tail = list(_entries)[-safe_limit:]
        # Return PII-safe projection (no raw payload, only summaries already stored)
        recent = [{
            "ts": e["ts"],
            "family": e.get("family"),
            "route": e.get("route"),
            "overall_level": e.get("overall_level"),
            "rates": e.get("rates"),
            "critical_immediate_observed": e.get("critical_immediate_observed"),
            "alerts": e.get("alerts") or [],
            "entry_id_preview": e.get("entry_id_preview"),
            "dispatched": False,
        } for e in tail]
        buffer_size = len(_entries)
    return {
        "enabled": True,
        "contract_version": CONTRACT_VERSION,
        "dry_run_only": DRY_RUN_ONLY,
        "operation_family": fam,
        "rolling_windows_seconds": list(ROLLING_WINDOWS_SECONDS),
        "windows": windows,
        "recent_entries": recent,
        "buffer_size_current": int(buffer_size),
        "buffer_capacity": int(MAX_ENTRIES),
        "persisted": PERSISTED,
        "db_writes": DB_WRITES,
        "alert_sink_live_enabled": ALERT_SINK_LIVE_ENABLED,
        "alert_dispatched": False,
        "live_enforcement_enabled": LIVE_ENFORCEMENT_ENABLED,
        "preview_request_blocked": PREVIEW_REQUEST_BLOCKED,
        "pii_safe": True,
        "raw_payload_captured": False,
        "supported_families": list(_SUPPORTED_FAMILIES),
    }


def build_config_block() -> Dict[str, Any]:
    """Configuration block exposed in /config envelopes."""
    return {
        "enabled": True,
        "contract_version": CONTRACT_VERSION,
        "dry_run_only": DRY_RUN_ONLY,
        "rolling_windows_seconds": list(ROLLING_WINDOWS_SECONDS),
        "buffer_capacity": int(MAX_ENTRIES),
        "persisted": PERSISTED,
        "db_writes": DB_WRITES,
        "alert_sink_live_enabled": ALERT_SINK_LIVE_ENABLED,
        "alert_dispatched": False,
        "live_enforcement_enabled": LIVE_ENFORCEMENT_ENABLED,
        "preview_request_blocked": PREVIEW_REQUEST_BLOCKED,
        "pii_safe": True,
        "raw_payload_captured": False,
        "external_sink_used": False,
        "supported_families": list(_SUPPORTED_FAMILIES),
    }


def build_alert_history_record_envelope(
    operation_family: str,
    alert_evaluation: Any = None,
    route_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Record the evaluation and return a PII-safe envelope for POST responses."""
    eid = record_alert_evaluation(operation_family, alert_evaluation, route_name)
    overall = (alert_evaluation or {}).get("overall_level") if isinstance(alert_evaluation, dict) else None
    if overall not in _VALID_LEVELS:
        overall = "ok"
    return {
        "enabled": True,
        "contract_version": CONTRACT_VERSION,
        "dry_run_only": DRY_RUN_ONLY,
        "operation_family": str(operation_family) if operation_family else None,
        "route": route_name,
        "entry_id_preview": eid,
        "recorded_overall_level": overall,
        "alert_sink_live_enabled": ALERT_SINK_LIVE_ENABLED,
        "alert_dispatched": False,
        "persisted": PERSISTED,
        "db_writes": DB_WRITES,
        "live_enforcement_enabled": LIVE_ENFORCEMENT_ENABLED,
        "preview_request_blocked": PREVIEW_REQUEST_BLOCKED,
        "pii_safe": True,
        "raw_payload_captured": False,
    }


def _test_reset() -> None:
    """Validator/test hook: clear in-memory ring buffer."""
    global _seq
    with _lock:
        _entries.clear()
        _seq = 0
