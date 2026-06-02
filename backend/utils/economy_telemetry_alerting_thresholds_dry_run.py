"""economy_telemetry_alerting_thresholds_dry_run.py

v46 — Track A
Telemetry Alerting Thresholds (DRY-RUN, in-memory only, no external sink).

Strict properties (NEVER violated):
- Dry-run only. No DB / Redis / filesystem. No external alert dispatch.
- No persistent ledger. No live enforcement.
- Preview request never blocked.
- Consumes only PII-safe v45 aggregation snapshots.
- 0 db_writes; alert_sink_live_enabled=false; preview_request_blocked=false.

Public API:
- evaluate_alerts_from_snapshot(snapshot) -> dict
- build_alerting_thresholds_config() -> dict
- _test_reset() -> None  (test/validator hook only)

Thresholds (evaluated on the 60s rolling window of the v45 snapshot):
- replay rate: warn>=0.20, critical>=0.50
- conflict rate: warn>=0.05, critical>=0.15
- missing-key rate: warn>=0.10, critical>=0.25

Critical-immediate triggers (force critical regardless of rates):
- db_writes_observed > 0
- reward_grants_observed > 0
- mutation_observed > 0
- bp_delta_observed > 0
- live_enforcement_observed > 0
"""
from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

CONTRACT_VERSION = "economy_telemetry_alerting_thresholds_dry_run_v1"
DRY_RUN_ONLY = True
PERSISTED = False
DB_WRITES = 0
LIVE_ENFORCEMENT_ENABLED = False
PREVIEW_REQUEST_BLOCKED = False
ALERT_SINK_LIVE_ENABLED = False

THRESHOLDS = {
    "replay_rate": {"warn": 0.20, "critical": 0.50},
    "conflict_rate": {"warn": 0.05, "critical": 0.15},
    "missing_key_rate": {"warn": 0.10, "critical": 0.25},
}

CRITICAL_IMMEDIATE_FIELDS = (
    "db_writes_observed_total",
    "reward_grants_observed_total",
    "mutation_observed_total",
    "bp_delta_observed_total",
    "live_enforcement_observed_total",
)

_lock = threading.RLock()


def _classify(value: float, warn: float, critical: float) -> str:
    if value >= critical:
        return "critical"
    if value >= warn:
        return "warn"
    return "ok"


def _rate(numer: int, denom: int) -> float:
    if not denom:
        return 0.0
    try:
        return float(numer) / float(denom)
    except Exception:
        return 0.0


def _pick_60s_window(snapshot: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(snapshot, dict):
        return None
    windows = snapshot.get("windows") or []
    for w in windows:
        if isinstance(w, dict) and int(w.get("window_seconds") or 0) == 60:
            return w
    return None


def evaluate_alerts_from_snapshot(snapshot: Any) -> Dict[str, Any]:
    """Evaluate alert classification from a v45 aggregation snapshot.

    Returns a PII-safe envelope. NEVER dispatches to an external sink.
    NEVER blocks the preview request.
    """
    with _lock:
        win = _pick_60s_window(snapshot)
        if win is None:
            return {
                "enabled": True,
                "contract_version": CONTRACT_VERSION,
                "dry_run_only": DRY_RUN_ONLY,
                "evaluated": False,
                "reason": "no_60s_window_available",
                "overall_level": "ok",
                "rates": {},
                "rate_levels": {},
                "critical_immediate_observed": False,
                "alerts": [],
                "alert_sink_live_enabled": ALERT_SINK_LIVE_ENABLED,
                "alert_dispatched": False,
                "db_writes": DB_WRITES,
                "persisted": PERSISTED,
                "live_enforcement_enabled": LIVE_ENFORCEMENT_ENABLED,
                "preview_request_blocked": PREVIEW_REQUEST_BLOCKED,
                "pii_safe": True,
            }
        total = int(win.get("total_events") or 0)
        replay = int(win.get("replay_same_hash_count") or 0)
        conflict = int(win.get("conflict_diff_hash_count") or 0)
        missing = int(win.get("missing_key_count") or 0)
        rates = {
            "replay_rate": _rate(replay, total),
            "conflict_rate": _rate(conflict, total),
            "missing_key_rate": _rate(missing, total),
        }
        levels = {
            k: _classify(v, THRESHOLDS[k]["warn"], THRESHOLDS[k]["critical"])
            for k, v in rates.items()
        }
        critical_immediate: List[str] = []
        for f in CRITICAL_IMMEDIATE_FIELDS:
            try:
                if int(win.get(f) or 0) > 0:
                    critical_immediate.append(f)
            except Exception:
                pass
        # Overall level: critical if any critical_immediate or any rate critical;
        # else warn if any rate warn; else ok.
        overall = "ok"
        if critical_immediate or any(v == "critical" for v in levels.values()):
            overall = "critical"
        elif any(v == "warn" for v in levels.values()):
            overall = "warn"
        alerts: List[Dict[str, Any]] = []
        for k, lvl in levels.items():
            if lvl != "ok":
                alerts.append({
                    "metric": k,
                    "level": lvl,
                    "value": rates[k],
                    "threshold_warn": THRESHOLDS[k]["warn"],
                    "threshold_critical": THRESHOLDS[k]["critical"],
                    "window_seconds": 60,
                    "dispatched": False,
                })
        for f in critical_immediate:
            alerts.append({
                "metric": f,
                "level": "critical",
                "value": int(win.get(f) or 0),
                "rule": "critical_immediate_observed",
                "window_seconds": 60,
                "dispatched": False,
            })
        return {
            "enabled": True,
            "contract_version": CONTRACT_VERSION,
            "dry_run_only": DRY_RUN_ONLY,
            "evaluated": True,
            "overall_level": overall,
            "rates": rates,
            "rate_levels": levels,
            "critical_immediate_observed": bool(critical_immediate),
            "critical_immediate_fields": critical_immediate,
            "alerts": alerts,
            "thresholds": THRESHOLDS,
            "alert_sink_live_enabled": ALERT_SINK_LIVE_ENABLED,
            "alert_dispatched": False,
            "db_writes": DB_WRITES,
            "persisted": PERSISTED,
            "live_enforcement_enabled": LIVE_ENFORCEMENT_ENABLED,
            "preview_request_blocked": PREVIEW_REQUEST_BLOCKED,
            "pii_safe": True,
            "raw_payload_captured": False,
        }


def build_alerting_thresholds_config() -> Dict[str, Any]:
    """Configuration block exposed in /config envelopes."""
    return {
        "enabled": True,
        "contract_version": CONTRACT_VERSION,
        "dry_run_only": DRY_RUN_ONLY,
        "thresholds": THRESHOLDS,
        "critical_immediate_fields": list(CRITICAL_IMMEDIATE_FIELDS),
        "alert_sink_live_enabled": ALERT_SINK_LIVE_ENABLED,
        "alert_dispatched": False,
        "db_writes": DB_WRITES,
        "persisted": PERSISTED,
        "live_enforcement_enabled": LIVE_ENFORCEMENT_ENABLED,
        "preview_request_blocked": PREVIEW_REQUEST_BLOCKED,
        "pii_safe": True,
        "raw_payload_captured": False,
        "external_sink_used": False,
    }


def _test_reset() -> None:
    """Validator/test hook: no-op (utility is stateless beyond inputs)."""
    return None
