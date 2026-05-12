#!/usr/bin/env python3
"""Validate RM1.25-C read-only catalog API requirements file."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/app") if Path("/app").exists() else Path(__file__).resolve().parents[2]
REQ = ROOT / "data" / "design" / "skill_status_vfx_readonly_api_requirements.json"

EXPECTED_FILES = {
    "skill_slot_progression_v1.json",
    "status_effect_catalog_v1.json",
    "status_icon_registry_v1.json",
    "vfx_modular_catalog_v1.json",
    "skill_schema_examples_v1.json",
}

EXPECTED_ENDPOINTS = {
    "/api/skill-status-vfx/catalogs/summary",
    "/api/skill-status-vfx/catalogs/skill-progression",
    "/api/skill-status-vfx/catalogs/status-effects",
    "/api/skill-status-vfx/catalogs/status-icons",
    "/api/skill-status-vfx/catalogs/vfx",
    "/api/skill-status-vfx/catalogs/skill-examples",
}

FORBIDDEN_KEYWORDS = [
    "battle_engine.py changes",
    "battle balance changes",
    "live skill activation",
    "live status activation",
    "live VFX activation",
    "status icon UI activation",
    "frontend HP bar changes",
    "Borea activation",
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    if not REQ.exists():
        fail(f"requirements file not found: {REQ}")

    data = json.loads(REQ.read_text(encoding="utf-8"))

    if data.get("task_id") != "RM1.25-C":
        fail("task_id must be RM1.25-C")

    source_files = set(data.get("source_catalogs", {}).get("files", []))
    if source_files != EXPECTED_FILES:
        fail(f"source catalog files mismatch: {sorted(source_files)}")

    endpoints = {entry.get("path") for entry in data.get("api_endpoints", [])}
    missing = EXPECTED_ENDPOINTS - endpoints
    extra = endpoints - EXPECTED_ENDPOINTS
    if missing or extra:
        fail(f"endpoint mismatch; missing={sorted(missing)} extra={sorted(extra)}")

    for entry in data.get("api_endpoints", []):
        if entry.get("method") != "GET":
            fail(f"endpoint {entry.get('path')} must be GET")
        if entry.get("auth_required") is not False:
            fail(f"endpoint {entry.get('path')} must be public/read-only for catalog inspection")

    forbidden = data.get("implementation_scope", {}).get("forbidden", [])
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword not in forbidden:
            fail(f"forbidden scope missing: {keyword}")

    counts = data.get("expected_catalog_counts_from_rm125b", {})
    expected_counts = {
        "official_elements": 7,
        "core_statuses": 40,
        "status_icons": 40,
        "vfx_types": 12,
        "vfx_entries": 163,
        "skill_examples_min": 4,
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            fail(f"expected count {key}={expected}, got {counts.get(key)}")

    acceptance = data.get("acceptance_criteria", [])
    if len(acceptance) < 12:
        fail("acceptance criteria too short")
    for needle in ["No DB writes", "No battle_engine.py changes", "GET /api/heroes remains 100", "Borea remains hidden/pending"]:
        if needle not in acceptance:
            fail(f"missing acceptance criterion: {needle}")

    loader = data.get("loader_requirements", {})
    if loader.get("read_only") is not True:
        fail("loader must be read_only")
    if loader.get("must_not_import_battle_engine") is not True:
        fail("loader must not import battle_engine")

    print("PASS: RM1.25-C read-only catalog API requirements validated")
    print(f"- source catalogs: {len(source_files)}")
    print(f"- endpoints: {len(endpoints)}")
    print(f"- expected core statuses: {counts['core_statuses']}")
    print(f"- expected VFX entries: {counts['vfx_entries']}")
    print(f"- acceptance criteria: {len(acceptance)}")


if __name__ == "__main__":
    main()
