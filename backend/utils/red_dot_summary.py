"""Pre-QA Stabilization 116C — Red Dot summary helper (read-only).

No DB writes. No claim. No read-all. No push. No mutation.
Aggregates indicators hierarchically (source -> screen -> menu -> total).
"""
from __future__ import annotations
from typing import Optional, Mapping

RED_DOT_SUMMARY_VERSION = "red_dot_v1_preqa_read_only_foundation"
RED_DOT_SOURCE_MAP_PATH = "data/design/red_dot/red_dot_notification_badge_source_map_v1.json"
RED_DOT_MAX_COUNT_DISPLAY = 99  # client renders ">99" or "9+" per source policy


def _empty_node(route: str, count: int = 0, has_dot: bool = False, severity: str = "none",
                reason: Optional[str] = None, locked_by_pre_qa: bool = False,
                actionable_now: bool = False) -> dict:
    return {
        "has_dot": bool(has_dot),
        "count": int(count),
        "severity": severity,
        "reason": reason,
        "route": route,
        "locked_by_pre_qa": bool(locked_by_pre_qa),
        "actionable_now": bool(actionable_now),
    }


def build_red_dot_metadata() -> dict:
    return {
        "red_dot_summary_version": RED_DOT_SUMMARY_VERSION,
        "source_map_path": RED_DOT_SOURCE_MAP_PATH,
        "no_db_writes": True,
        "no_claim_activation": True,
        "no_read_all": True,
        "no_push_notification": True,
        "no_toast": True,
        "server_scoped": True,
        "max_count_display_cap": RED_DOT_MAX_COUNT_DISPLAY,
    }


def build_summary(server_id: str, psp_present: bool, team_missing: bool) -> dict:
    """Build the red-dot summary envelope. Pure function. No DB.

    Args:
        server_id: required (already validated by route).
        psp_present: whether PSP exists for the (uid, server_id).
        team_missing: whether the active team is missing (from battle_power summary).
    """
    # active_safe sources (Pack 116C: only system warnings derived from
    # already-existing read-only signals; no new endpoints, no mutations).
    sources = []

    # source: server_profile_required
    if not psp_present:
        sources.append({
            "source_id": "server_profile_required",
            **_empty_node(route="/home", has_dot=True, count=0, severity="warning",
                          reason="PLAYER_SERVER_PROFILE_REQUIRED", locked_by_pre_qa=False,
                          actionable_now=False),
        })

    # source: team_missing_warning
    if psp_present and team_missing:
        sources.append({
            "source_id": "team_missing_warning",
            **_empty_node(route="/battle", has_dot=True, count=0, severity="info",
                          reason="TEAM_FORMATION_EMPTY_OR_INVALID", locked_by_pre_qa=False,
                          actionable_now=False),
        })

    # Aggregations (deduplicated by source_id; capped for anti-spam).
    seen_ids = set()
    dedup_sources = []
    for s in sources:
        sid = s.get("source_id")
        if sid in seen_ids:
            continue
        seen_ids.add(sid)
        dedup_sources.append(s)

    # Screen-level aggregation.
    screens = {}
    for s in dedup_sources:
        route = s["route"]
        node = screens.setdefault(route, _empty_node(route=route))
        if s["has_dot"]:
            node["has_dot"] = True
            node["count"] += s["count"]
            if s["severity"] == "warning":
                node["severity"] = "warning"
            elif s["severity"] == "info" and node["severity"] == "none":
                node["severity"] = "info"
            node["reason"] = node["reason"] or s["reason"]
            node["actionable_now"] = node["actionable_now"] or s["actionable_now"]

    # Menu-category aggregation (simple: every dot goes to "home" parent).
    home_total = _empty_node(route="/home")
    for node in screens.values():
        if node["has_dot"]:
            home_total["has_dot"] = True
            home_total["count"] += node["count"]
            if node["severity"] == "warning":
                home_total["severity"] = "warning"
            elif node["severity"] == "info" and home_total["severity"] == "none":
                home_total["severity"] = "info"

    return {
        "status": "ok",
        "server_id": server_id,
        **build_red_dot_metadata(),
        "psp_present_for_server": bool(psp_present),
        "sources": dedup_sources,
        "by_screen": screens,
        "home_total": home_total,
        "active_sources_count": len(dedup_sources),
    }
