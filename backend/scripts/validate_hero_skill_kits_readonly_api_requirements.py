#!/usr/bin/env python3
"""Validate RM1.26-C Hero Skill Kit Read-Only Catalog API requirements pack."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("APP_ROOT", "/app"))
REQ_PATH = ROOT / "data/design/hero_skill_kits/hero_skill_kits_readonly_api_requirements_v1.json"
DOC_PATH = ROOT / "docs/divine/24_HERO_SKILL_KITS_READONLY_API_PLAN.md"

EXPECTED_ENDPOINTS = {
    "GET /api/hero-skill-kits/catalogs/summary",
    "GET /api/hero-skill-kits/catalogs/schema",
    "GET /api/hero-skill-kits/catalogs/5star",
    "GET /api/hero-skill-kits/catalogs/6star",
    "GET /api/hero-skill-kits/catalogs/by-hero/{hero_id}",
}
EXPECTED_COUNTS = {
    "five_star_entries": 20,
    "six_star_launch_base_entries": 12,
    "six_star_extra_premium_entries": 1,
    "six_star_total_entries": 13,
    "total_catalog_entries": 33,
}
EXPECTED_FLAGS = {
    "runtime_attached": False,
    "battle_runtime_attached": False,
    "ui_runtime_attached": False,
    "hp_bar_runtime_attached": False,
    "balance_values_finalized": False,
    "do_not_treat_as_live_kit": True,
}
EXPECTED_5STAR_SLOTS = ["basic", "passive_base", "skill_1", "passive_advanced", "skill_2"]
EXPECTED_6STAR_SLOTS = ["basic", "passive_base", "skill_1", "passive_advanced", "skill_2", "ultimate"]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    if not REQ_PATH.exists():
        fail(f"requirements file missing: {REQ_PATH}")
    if not DOC_PATH.exists():
        fail(f"plan doc missing: {DOC_PATH}")

    data = json.loads(REQ_PATH.read_text(encoding="utf-8"))

    if data.get("task_id") != "RM1.26-C":
        fail("task_id must be RM1.26-C")

    endpoints = {f"{e.get('method')} {e.get('path')}" for e in data.get("endpoints", [])}
    missing_endpoints = sorted(EXPECTED_ENDPOINTS - endpoints)
    if missing_endpoints:
        fail(f"missing endpoints: {missing_endpoints}")

    counts = data.get("expected_counts", {})
    for key, expected in EXPECTED_COUNTS.items():
        if counts.get(key) != expected:
            fail(f"expected_counts.{key} expected {expected}, got {counts.get(key)!r}")

    flags = data.get("required_payload_flags", {})
    for key, expected in EXPECTED_FLAGS.items():
        if flags.get(key) is not expected:
            fail(f"required_payload_flags.{key} expected {expected}, got {flags.get(key)!r}")

    slots = data.get("expected_slots", {})
    if slots.get("five_star") != EXPECTED_5STAR_SLOTS:
        fail(f"five_star slots mismatch: {slots.get('five_star')!r}")
    if slots.get("six_star") != EXPECTED_6STAR_SLOTS:
        fail(f"six_star slots mismatch: {slots.get('six_star')!r}")

    source_catalogs = data.get("source_catalogs", {})
    for key in ["schema", "five_star_full", "six_star_borea"]:
        path = source_catalogs.get(key)
        if not path or not path.startswith("/app/data/design/hero_skill_kits/"):
            fail(f"source_catalogs.{key} must point to /app/data/design/hero_skill_kits/: {path!r}")

    absolute_rules = data.get("absolute_rules", [])
    required_rules = [
        "No DB writes",
        "No battle_engine.py changes",
        "Do not activate Borea",
        "Do not modify Character Bible",
        "Only GET endpoints are allowed",
        "No POST/PUT/PATCH/DELETE endpoints",
    ]
    for rule in required_rules:
        if rule not in absolute_rules:
            fail(f"missing absolute rule: {rule}")

    acceptance = data.get("acceptance_criteria", [])
    if len(acceptance) < 20:
        fail(f"expected at least 20 acceptance criteria, got {len(acceptance)}")

    print("PASS: RM1.26-C hero skill kit read-only API requirements validated")
    print(f"- endpoints: {len(endpoints)}")
    print(f"- expected 5★ entries: {counts.get('five_star_entries')}")
    print(f"- expected 6★ launch_base entries: {counts.get('six_star_launch_base_entries')}")
    print(f"- expected 6★ extra premium entries: {counts.get('six_star_extra_premium_entries')}")
    print(f"- expected total catalog entries: {counts.get('total_catalog_entries')}")
    print(f"- required runtime flags: {len(EXPECTED_FLAGS)}")
    print(f"- acceptance criteria: {len(acceptance)}")


if __name__ == "__main__":
    main()
