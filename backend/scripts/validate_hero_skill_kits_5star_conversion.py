#!/usr/bin/env python3
"""
RM1.26-B validator — 5★ skill kit conversion requirements.

This script validates:
1. the requirements pack itself;
2. the optional output full 5★ catalog if it exists.

If the output catalog is not present, this script still passes the requirements
validation and reports that conversion has not yet produced a full catalog.
This supports the required STOP behavior when the approved 5★ source is missing.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path("/app")
REQ_PATH = ROOT / "data/design/hero_skill_kits/hero_skill_kits_5star_conversion_requirements_v1.json"
OUTPUT_PATH = ROOT / "data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json"

EXPECTED_SLOTS = ["basic", "passive_base", "skill_1", "passive_advanced", "skill_2"]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_requirements(req: dict[str, Any]) -> list[str]:
    if req.get("task_id") != "RM1.26-B":
        fail("requirements task_id must be RM1.26-B")
    if not req.get("core_correction", {}).get("do_not_reauthor_5star_kits"):
        fail("core correction do_not_reauthor_5star_kits must be true")
    if not req.get("core_correction", {}).get("source_of_truth_required"):
        fail("source_of_truth_required must be true")

    heroes = req.get("required_5star_heroes")
    if not isinstance(heroes, list) or len(heroes) != 20:
        fail("required_5star_heroes must contain exactly 20 entries")
    ids = [h.get("hero_id") for h in heroes]
    if len(set(ids)) != 20:
        fail("required_5star_heroes must contain 20 unique hero_id values")

    if req.get("required_slots_for_5star") != EXPECTED_SLOTS:
        fail(f"required_slots_for_5star must be {EXPECTED_SLOTS}")

    forbidden = req.get("source_policy", {}).get("forbidden", [])
    for term in ["inventing missing skill names", "rewriting/rebalancing 5-star kits", "using memory to fill missing details"]:
        if term not in forbidden:
            fail(f"source_policy.forbidden missing required term: {term}")

    return ids


def extract_entries(catalog: Any) -> list[dict[str, Any]]:
    if isinstance(catalog, dict):
        for key in ("heroes", "entries", "hero_skill_kits", "kits"):
            val = catalog.get(key)
            if isinstance(val, list):
                return val
    if isinstance(catalog, list):
        return catalog
    fail("output catalog must be a list or contain heroes/entries/hero_skill_kits/kits list")


def validate_output_catalog(expected_ids: list[str]) -> None:
    if not OUTPUT_PATH.exists():
        print("INFO: output full 5★ catalog not present.")
        print("INFO: This is acceptable only if the approved consolidated 5★ source was missing and the task stopped.")
        return

    catalog = load_json(OUTPUT_PATH)

    if isinstance(catalog, dict):
        if catalog.get("runtime_attached") is not False:
            fail("output catalog runtime_attached must be false")
        if catalog.get("balance_values_finalized") is not False:
            fail("output catalog balance_values_finalized must be false")
        if catalog.get("do_not_treat_as_live_kit") is not True:
            fail("output catalog do_not_treat_as_live_kit must be true")

    entries = extract_entries(catalog)
    if len(entries) != 20:
        fail(f"output catalog must contain exactly 20 entries, found {len(entries)}")

    ids = [e.get("hero_id") for e in entries]
    if set(ids) != set(expected_ids):
        missing = sorted(set(expected_ids) - set(ids))
        extra = sorted(set(ids) - set(expected_ids))
        fail(f"output hero_id mismatch. missing={missing} extra={extra}")

    for entry in entries:
        hero_id = entry.get("hero_id")
        if entry.get("runtime_attached") is not False:
            fail(f"{hero_id}: runtime_attached must be false")
        if entry.get("balance_values_finalized") is not False:
            fail(f"{hero_id}: balance_values_finalized must be false")

        if "ultimate" in entry or "ultimate" in entry.get("skill_package", {}):
            fail(f"{hero_id}: native 5★ must not include ultimate")

        if entry.get("divine_weapon_hooks"):
            fail(f"{hero_id}: native 5★ must not include native 6★ divine_weapon_hooks")
        if entry.get("domain_hooks"):
            fail(f"{hero_id}: native 5★ must not include true 6★ domain_hooks")

        pkg = entry.get("skill_package")
        if not isinstance(pkg, dict):
            fail(f"{hero_id}: missing skill_package dict")
        slots = list(pkg.keys())
        if slots != EXPECTED_SLOTS:
            fail(f"{hero_id}: skill_package slots must be {EXPECTED_SLOTS}, found {slots}")

        for slot, skill in pkg.items():
            if not isinstance(skill, dict):
                fail(f"{hero_id}.{slot}: skill must be dict")
            if skill.get("final_numbers") is not None:
                fail(f"{hero_id}.{slot}: final_numbers must be null")
            if skill.get("slot") not in (None, slot):
                fail(f"{hero_id}.{slot}: slot field mismatch")
            for required in ["display_name", "design_summary"]:
                if required not in skill:
                    fail(f"{hero_id}.{slot}: missing required field {required}")

    print("INFO: output full 5★ catalog present and structurally valid.")


def main() -> None:
    if not REQ_PATH.exists():
        fail(f"requirements file missing: {REQ_PATH}")

    req = load_json(REQ_PATH)
    expected_ids = validate_requirements(req)
    validate_output_catalog(expected_ids)

    print("PASS: RM1.26-B 5★ conversion requirements validated")
    print(f"- required 5★ heroes: {len(expected_ids)}")
    print(f"- expected slots: {EXPECTED_SLOTS}")
    print(f"- output catalog path: {OUTPUT_PATH}")
    print(f"- output catalog present: {OUTPUT_PATH.exists()}")
    print("- source policy: do not invent; stop if approved source missing")


if __name__ == "__main__":
    main()
