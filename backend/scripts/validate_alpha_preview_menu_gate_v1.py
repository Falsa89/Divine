#!/usr/bin/env python3
# Validator: PROJECT-ALPHA-PREVIEW-MENU-GATE
# Pack: MEGA_RELEASE_ACCELERATION_20_v71
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "contract": "data/design/navigation/alpha_preview_menu_gate_contract_v1.json",
    "map": "data/design/navigation/alpha_preview_safe_hub_route_map_v1.json",
    "forbidden": "data/design/navigation/alpha_preview_menu_gate_forbidden_scope_v1.json",
    "marker": "data/design/navigation/alpha_preview_menu_gate_marker_v1.json",
}
CONTRACT_EXP = {
    "design_only": True,
    "public_menu_routing_enabled": False,
    "home_menu_routing_enabled": False,
    "deeplink_only": True,
    "public_tabs_routing": False,
    "production_navigation_changes": False,
    "manual_approval_required": True,
}
REQUIRED_ROUTES = {
    "training-combat-onboarding-preview",
    "first-session-onboarding-preview",
    "story-alpha-slice-preview",
    "boss-tower-alpha-loop-preview",
    "event-arena-alpha-gate-preview",
    "event-arena-first-alpha-slice-preview",
    "visual-battle-preview-router",
}


def main() -> int:
    errors = []
    for k, rel in FILES.items():
        if not os.path.isfile(os.path.join(ROOT, rel)):
            errors.append(f"MISSING_FILE: {k}={rel}")
    if errors:
        for e in errors:
            print(e)
        return 1

    contract = json.load(open(os.path.join(ROOT, FILES["contract"]), "r", encoding="utf-8"))
    for k, v in CONTRACT_EXP.items():
        if contract.get(k) != v:
            errors.append(f"CONTRACT_BAD: {k}={contract.get(k)!r} expected {v!r}")

    route_map = json.load(open(os.path.join(ROOT, FILES["map"]), "r", encoding="utf-8"))
    if route_map.get("public_menu_routing_enabled") is not False:
        errors.append("MAP_PUBLIC_MENU_ENABLED")
    if route_map.get("db_writes") != 0:
        errors.append("MAP_BAD_DB_WRITES")
    routes_in_map = {r.get("route") for r in (route_map.get("safe_preview_routes") or [])}
    if not REQUIRED_ROUTES.issubset(routes_in_map):
        errors.append("MAP_ROUTES_MISSING")
    for r in (route_map.get("safe_preview_routes") or []):
        for req_key in ("route", "status", "guardrails", "forbidden_live_systems", "qa_priority"):
            if req_key not in r:
                errors.append(f"ROUTE_ENTRY_MISSING_KEY: {r.get('route')}.{req_key}")

    forbidden = json.load(open(os.path.join(ROOT, FILES["forbidden"]), "r", encoding="utf-8"))
    for must in ["public_menu_exposure", "home_menu_routing",
                 "public_tab_routing", "production_navigation_changes",
                 "db_writes", "reward_grant", "battle_engine_runtime"]:
        if must not in (forbidden.get("forbidden") or []):
            errors.append(f"FORBIDDEN_MISSING: {must}")

    marker = json.load(open(os.path.join(ROOT, FILES["marker"]), "r", encoding="utf-8"))
    if marker.get("public_menu_routing_enabled") is not False:
        errors.append("MARKER_PUBLIC_MENU_ENABLED")
    if marker.get("deeplink_only") is not True:
        errors.append("MARKER_NOT_DEEPLINK_ONLY")

    if errors:
        for e in errors:
            print(e)
        return 1
    print("PROJECT-ALPHA-PREVIEW-MENU-GATE: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
