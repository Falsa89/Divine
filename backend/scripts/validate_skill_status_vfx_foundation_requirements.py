#!/usr/bin/env python3
"""Validate RM1.25-A skill/status/VFX foundation requirements.

This script validates the design requirements JSON shipped with the RM1.25-A
foundation package. It is intentionally read-only and performs no DB writes,
no migrations, and no runtime activation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQ_PATH = ROOT / "data" / "design" / "skill_status_vfx_foundation_requirements.json"

EXPECTED_ELEMENTS = {"water", "fire", "earth", "wind", "lightning", "light", "dark"}
FORBIDDEN_ELEMENTS = {"ice", "nature", "holy", "shadow", "thunder"}
EXPECTED_RARITY_MAP = {
    "1": ["basic"],
    "2": ["basic", "passive_base"],
    "3": ["basic", "passive_base", "skill_1"],
    "4": ["basic", "passive_base", "skill_1", "passive_advanced"],
    "5": ["basic", "passive_base", "skill_1", "passive_advanced", "skill_2"],
    "6": ["basic", "passive_base", "skill_1", "passive_advanced", "skill_2", "ultimate"],
}
EXPECTED_STATUS_COUNT = 40
REQUIRED_VFX_TYPES = {
    "apply_vfx",
    "projectile_vfx",
    "travel_vfx",
    "impact_vfx",
    "persistent_status_vfx",
    "stack_gain_vfx",
    "stack_decay_vfx",
    "expire_vfx",
    "cleanse_vfx",
    "field_domain_vfx",
    "screen_edge_vfx",
    "fullscreen_vfx",
}
REQUIRED_PRESENTATION_BLOCKS = {
    "source_actor_motion",
    "projectile_vfx",
    "target_impact_vfx",
    "return_motion",
    "persistent_status_vfx",
    "screen_or_field_vfx",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    require(REQ_PATH.exists(), f"Missing requirements file: {REQ_PATH}")
    data = json.loads(REQ_PATH.read_text(encoding="utf-8"))

    require(data.get("task_id") == "RM1.25-A", "task_id must be RM1.25-A")
    require(data.get("status") == "approved_requirements_package", "status must be approved_requirements_package")

    scope = data.get("scope", {})
    require(scope.get("implementation_type") == "foundation_only", "scope.implementation_type must be foundation_only")
    require(scope.get("runtime_activation") is False, "runtime_activation must be false")
    require(scope.get("battle_engine_changes_allowed") is False, "battle_engine_changes_allowed must be false")
    require(scope.get("ui_runtime_changes_allowed") is False, "ui_runtime_changes_allowed must be false")
    require(scope.get("asset_generation_allowed") is False, "asset_generation_allowed must be false")

    elements = set(data.get("official_elements", []))
    require(elements == EXPECTED_ELEMENTS, f"official_elements mismatch: {elements}")
    forbidden = set(data.get("forbidden_primary_elements", []))
    require(FORBIDDEN_ELEMENTS.issubset(forbidden), "forbidden_primary_elements missing one or more forbidden element names")
    require(elements.isdisjoint(forbidden), "official elements overlap forbidden elements")

    rarity_map = data.get("rarity_skill_slots", {})
    require(rarity_map == EXPECTED_RARITY_MAP, "rarity_skill_slots does not match approved progression")

    core_statuses = data.get("core_statuses", {})
    flattened = [status for group in core_statuses.values() for status in group]
    require(len(flattened) == EXPECTED_STATUS_COUNT, f"expected {EXPECTED_STATUS_COUNT} core statuses, got {len(flattened)}")
    require(len(set(flattened)) == len(flattened), "duplicate status ids found in core_statuses")
    require("marchio_boreale" in flattened, "marchio_boreale missing from core_statuses")
    require("freeze" in flattened and "stun" in flattened and "immunity" in flattened, "critical statuses missing")

    priorities = data.get("status_icon_priorities", {})
    for key in ["critical", "high", "medium", "low"]:
        require(key in priorities and priorities[key], f"missing non-empty status_icon_priorities.{key}")
    require("marchio_boreale" in priorities["high"], "marchio_boreale must be high priority")
    require("freeze" in priorities["critical"], "freeze must be critical priority")
    require("stun" in priorities["critical"], "stun must be critical priority")

    icon_rules = data.get("status_icon_asset_rules", {})
    require(icon_rules.get("master_size_px") == 128, "status icon master size must be 128")
    require(set(icon_rules.get("exports_px", [])) == {64, 48, 32, 24}, "status icon exports must be 64/48/32/24")
    require("stack_count" in icon_rules.get("runtime_overlays", []), "stack_count must be runtime overlay")
    require("duration" in icon_rules.get("runtime_overlays", []), "duration must be runtime overlay")
    require("stack_count" in icon_rules.get("forbidden_baked_content", []), "stack_count must be forbidden baked content")
    require("duration" in icon_rules.get("forbidden_baked_content", []), "duration must be forbidden baked content")

    vfx_types = set(data.get("vfx_types", []))
    require(REQUIRED_VFX_TYPES.issubset(vfx_types), "vfx_types missing required modular VFX entries")
    require(set(data.get("vfx_intensity_levels", [])) == {"low", "medium", "high", "premium", "ultimate", "domain"}, "vfx intensity levels mismatch")
    presentation_blocks = set(data.get("presentation_flow_blocks", []))
    require(REQUIRED_PRESENTATION_BLOCKS.issubset(presentation_blocks), "presentation_flow_blocks missing required entries")

    unique = data.get("unique_status_rules", {}).get("marchio_boreale", {})
    require(unique.get("source_locked") is True, "marchio_boreale must be source_locked")
    require(unique.get("owner_hero_id") == "greek_borea", "marchio_boreale owner_hero_id must be greek_borea")
    require(unique.get("stack_rules_required") is True, "marchio_boreale must require stack rules")

    guards = data.get("safety_guards", {})
    for guard in [
        "no_db_writes",
        "no_migrations",
        "no_apply_scripts",
        "no_gacha_changes",
        "no_battle_engine_activation",
        "no_roster_activation",
        "borea_safety_required",
    ]:
        require(guards.get(guard) is True, f"safety guard {guard} must be true")

    criteria = data.get("acceptance_criteria", [])
    require(len(criteria) >= 12, "expected at least 12 acceptance criteria")

    print("PASS: RM1.25-A requirements validated")
    print(f"- official elements: {sorted(elements)}")
    print(f"- core statuses: {len(flattened)}")
    print(f"- vfx types: {len(vfx_types)}")
    print(f"- acceptance criteria: {len(criteria)}")


if __name__ == "__main__":
    main()
