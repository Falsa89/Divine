#!/usr/bin/env python3
# Validator: PROJECT-ALPHA-PREVIEW-NAVIGATION-ASSET-BOUNDARY
# Pack: MEGA_RELEASE_ACCELERATION_19_v70
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "nav_boundary": "data/design/release_acceleration/first_session_event_arena_alpha_navigation_boundary_v1.json",
    "nav_map": "data/design/release_acceleration/alpha_preview_navigation_map_v1.json",
    "deferred_gate": "data/design/release_acceleration/v70_deferred_asset_import_gate_v1.json",
}

SAFE_LINKS = {
    "training-combat-onboarding-preview",
    "story-alpha-slice-preview",
    "boss-tower-alpha-loop-preview",
    "event-arena-alpha-gate-preview",
    "event-arena-first-alpha-slice-preview",
    "first-session-onboarding-preview",
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

    nb = json.load(open(os.path.join(ROOT, FILES["nav_boundary"]), "r", encoding="utf-8"))
    for k, v in {
        "preview_navigation_only": True,
        "public_menu_routing_enabled": False,
        "deep_link_only": True,
        "account_mutation": False,
        "db_writes": 0,
        "reward_grant": False,
        "real_asset_import": False,
        "asset_staging_import_deferred": True,
        "requires_real_asset_pack_before_import": True,
    }.items():
        if nb.get(k) != v:
            errors.append(f"NAV_BAD: {k}={nb.get(k)!r} expected {v!r}")

    nm = json.load(open(os.path.join(ROOT, FILES["nav_map"]), "r", encoding="utf-8"))
    if not SAFE_LINKS.issubset(set(nm.get("safe_links") or [])):
        errors.append("NAV_MAP_SAFE_LINKS_MISSING")
    if nm.get("public_menu_routing_enabled") is not False:
        errors.append("NAV_MAP_PUBLIC_MENU")
    if nm.get("db_writes") != 0:
        errors.append("NAV_MAP_BAD_DB_WRITES")

    dg = json.load(open(os.path.join(ROOT, FILES["deferred_gate"]), "r", encoding="utf-8"))
    for k, v in {
        "asset_staging_import_deferred": True,
        "requires_real_asset_pack_before_import": True,
        "real_asset_import": False,
        "file_copy_enabled": False,
        "runtime_asset_resolver_changed": False,
        "character_bible_changed": False,
        "hero_roster_changed": False,
        "manual_approval_required": True,
        "db_writes": 0,
    }.items():
        if dg.get(k) != v:
            errors.append(f"GATE_BAD: {k}={dg.get(k)!r} expected {v!r}")

    if errors:
        for e in errors:
            print(e)
        return 1
    print("PROJECT-ALPHA-PREVIEW-NAVIGATION-ASSET-BOUNDARY: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
