#!/usr/bin/env python
"""
RM1.26-B2 — Build inert 5★ skill kit catalog from approved canonical source.

Source: /app/data/design/heroes_kits_5star.json (legacy 4-slot schema:
        basic_attack, skill, passive, ultimate_or_special; status=draft_official_design_data,
        non_normative_for_runtime=true)

Output: /app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json
        (5-slot schema v1.1: basic, passive_base, skill_1, passive_advanced, skill_2)

Behavior:
  • Pure read-write only on the OUTPUT catalog file.
  • Reads canonical source ONLY. NO DB. NO runtime changes.
  • Slot remap:
      basic_attack         → basic
      skill                → skill_1
      passive              → passive_base
      ultimate_or_special  → skill_2  (with legacy metadata flags)
  • passive_advanced: NOT in source → emitted with design_status=missing_from_approved_source.
  • No invention: missing per-skill fields are left null/missing_from_source.
  • All final_numbers: null.
  • All entry/catalog runtime flags: false.
"""
import json
import os
from datetime import datetime, timezone

SOURCE_PATH = "/app/data/design/heroes_kits_5star.json"
OUTPUT_PATH = "/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json"

# ── Slot map: legacy_slot_key_in_source → target_slot_key ───────────────
SLOT_REMAP = {
    "basic_attack":        "basic",
    "skill":               "skill_1",
    "passive":             "passive_base",
    "ultimate_or_special": "skill_2",
}

PASSIVE_ADVANCED_KEY = "passive_advanced"
LEGACY_ULTIMATE_KEY = "ultimate_or_special"
NEW_ULTIMATE_TARGET = "skill_2"


def _derive_status_tags(legacy_skill: dict) -> list:
    """Best-effort: collect effect.type strings as status-like tags.
    NOT inventing. Just surfacing what's already in the source.
    """
    out = []
    for eff in (legacy_skill.get("effects") or []):
        if isinstance(eff, dict) and eff.get("type"):
            t = str(eff["type"])
            if t and t not in out:
                out.append(t)
    return out


def _derive_vfx_tags(legacy_skill: dict) -> list:
    """vfx_tags are NOT separately tracked in source — reuse 'tags' as
    raw VFX-hint pool. Not invented: passed-through.
    """
    return list(legacy_skill.get("tags") or [])


def _convert_skill(legacy_skill: dict, target_slot: str, *,
                   is_legacy_ultimate: bool) -> dict:
    """Convert a single legacy 4-slot skill block to v1.1 entry.

    final_numbers: null per RM1.26-B/B2 contract.
    legacy_source: preserved verbatim for traceability (read-only).
    """
    skill_out = {
        "slot": target_slot,
        "skill_id": legacy_skill.get("id") or None,
        "display_name": legacy_skill.get("name") or None,
        "design_summary": legacy_skill.get("description") or None,
        "targeting_summary": legacy_skill.get("target_type") or None,
        "status_tags": _derive_status_tags(legacy_skill),
        "vfx_tags": _derive_vfx_tags(legacy_skill),
        "animation_intent": legacy_skill.get("animation_state") or None,
        "final_numbers": None,
        "design_status": "converted_from_approved_source",
        "source_status": "ok",
    }
    # ── Legacy ultimate handling: explicit metadata so the catalog never
    #    leaks an "active ultimate" for 5★ in the new schema.
    if is_legacy_ultimate:
        skill_out["legacy_source_slot"] = LEGACY_ULTIMATE_KEY
        skill_out["is_true_ultimate"] = False
        skill_out["converted_to_slot"] = NEW_ULTIMATE_TARGET
    # ── Verbatim legacy block kept for audit (read-only, never imported
    #    at runtime). Useful per balancing pipeline successivo.
    skill_out["legacy_source"] = {
        "slot": legacy_skill.get("slot"),
        "id": legacy_skill.get("id"),
        "name": legacy_skill.get("name"),
        "description": legacy_skill.get("description"),
        "type": legacy_skill.get("type"),
        "target_type": legacy_skill.get("target_type"),
        "damage_type": legacy_skill.get("damage_type"),
        "scaling_stat": legacy_skill.get("scaling_stat"),
        "multiplier": legacy_skill.get("multiplier"),
        "cooldown_turns": legacy_skill.get("cooldown_turns"),
        "energy_cost": legacy_skill.get("energy_cost"),
        "effects": legacy_skill.get("effects"),
        "animation_state": legacy_skill.get("animation_state"),
        "tags": legacy_skill.get("tags"),
        "runtime_legacy_mapping": legacy_skill.get("runtime_legacy_mapping"),
    }
    return skill_out


def _passive_advanced_placeholder() -> dict:
    """Slot required by v1.1 progression but ABSENT from legacy source.
    No invention: marked as missing_from_approved_source.
    """
    return {
        "slot": PASSIVE_ADVANCED_KEY,
        "skill_id": None,
        "display_name": None,
        "design_summary": None,
        "targeting_summary": None,
        "status_tags": [],
        "vfx_tags": [],
        "animation_intent": None,
        "final_numbers": None,
        "design_status": "missing_from_approved_source",
        "source_status": "TODO_SOURCE_REQUIRED",
        "notes": (
            "Passive advanced required by v1.1 slot progression but not "
            "present as separate field in legacy approved 5★ source."
        ),
        "legacy_source": None,
    }


def _convert_hero(hid: str, h: dict) -> dict:
    """Build one entry for the new catalog."""
    skill_package = {}
    missing_fields = []

    # Mappa i 4 slot legacy presenti — INSERIMENTO IN ORDINE CANONICO v1.1:
    # [basic, passive_base, skill_1, passive_advanced, skill_2]
    SLOT_INSERTION_ORDER = [
        "basic", "passive_base", "skill_1", "passive_advanced", "skill_2",
    ]
    REVERSE_REMAP = {v: k for k, v in SLOT_REMAP.items()}
    for target_slot in SLOT_INSERTION_ORDER:
        if target_slot == PASSIVE_ADVANCED_KEY:
            skill_package[PASSIVE_ADVANCED_KEY] = _passive_advanced_placeholder()
            continue
        legacy_key = REVERSE_REMAP.get(target_slot)
        legacy_block = h.get(legacy_key) if legacy_key else None
        if legacy_block is None:
            skill_package[target_slot] = {
                "slot": target_slot,
                "design_status": "missing_from_approved_source",
                "source_status": "TODO_SOURCE_REQUIRED",
                "final_numbers": None,
                "notes": f"Legacy slot '{legacy_key}' absent in source for {hid}.",
            }
            missing_fields.append(f"{hid}:{legacy_key}")
        else:
            is_legacy_ult = (legacy_key == LEGACY_ULTIMATE_KEY)
            skill_package[target_slot] = _convert_skill(
                legacy_block, target_slot, is_legacy_ultimate=is_legacy_ult,
            )

    entry = {
        "hero_id": h.get("hero_id") or hid,
        "display_name": h.get("name"),
        "native_rarity": int(h.get("native_rarity") or 5),
        "element": h.get("element"),
        "role": h.get("role"),
        "faction": h.get("faction"),
        "origin_group": h.get("origin_group"),
        "category": h.get("category"),
        "release_group": h.get("release_group") or "launch_base",
        "runtime_attached": False,
        "balance_values_finalized": False,
        "stat_profile_source": h.get("stat_profile"),
        "kit_complexity_source": h.get("kit_complexity"),
        "expected_slots": [
            "basic", "passive_base", "skill_1", "passive_advanced", "skill_2",
        ],
        "skill_package": skill_package,
        "missing_fields_audit": missing_fields,
    }
    return entry


def main() -> int:
    if not os.path.exists(SOURCE_PATH):
        print(f"ERROR: source missing: {SOURCE_PATH}")
        return 2

    src = json.load(open(SOURCE_PATH, "r", encoding="utf-8"))
    heroes_src = src.get("heroes") or {}
    if len(heroes_src) != 20:
        print(f"ERROR: source must contain 20 5★ heroes, got {len(heroes_src)}")
        return 3

    # Build entries in stable order
    entries = []
    legacy_ult_conversions = 0
    passive_adv_missing = 0
    for hid in sorted(heroes_src.keys()):
        entry = _convert_hero(hid, heroes_src[hid])
        # Count metadata
        sp = entry["skill_package"]
        if sp.get("skill_2", {}).get("legacy_source_slot") == LEGACY_ULTIMATE_KEY:
            legacy_ult_conversions += 1
        if sp.get("passive_advanced", {}).get("design_status") == "missing_from_approved_source":
            passive_adv_missing += 1
        entries.append(entry)

    out = {
        "catalog_id": "hero_skill_kits_5star_full_v1",
        "version": "1.0.0",
        "task": "RM1.26-B2",
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "runtime_attached": False,
        "balance_values_finalized": False,
        "do_not_treat_as_live_kit": True,
        "scope": {
            "native_rarity": 5,
            "release_groups": ["launch_base"],
            "expected_hero_count": 20,
            "actual_hero_count": len(entries),
        },
        "source_file": SOURCE_PATH,
        "source_schema": "legacy_5star_4_slot",
        "conversion_schema": "skill_data_schema_v1.1_5star",
        "id_policy": "character_bible_confirmed_old_ids",
        "slot_remap": SLOT_REMAP,
        "design_rules": {
            "no_ultimate_for_5star": True,
            "passive_advanced_not_invented": True,
            "final_numbers_not_finalized": True,
            "no_divine_weapon_for_5star": True,
            "no_true_domain_for_5star": True,
        },
        "stats": {
            "legacy_ultimate_to_skill_2_conversions": legacy_ult_conversions,
            "passive_advanced_missing_count": passive_adv_missing,
        },
        "entries": entries,
        "notes": (
            "Inert design catalog. Read-only. NOT connected to combat runtime. "
            "Generated by /app/backend/scripts/build_hero_skill_kits_5star_full.py "
            "from the approved consolidated 5★ source. No skill invention. "
            "passive_advanced slot present but marked missing_from_approved_source. "
            "Legacy ultimate_or_special remapped to skill_2 with is_true_ultimate=false."
        ),
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"OK: wrote {OUTPUT_PATH}")
    print(f"  entries: {len(entries)}")
    print(f"  legacy ultimate→skill_2 conversions: {legacy_ult_conversions}")
    print(f"  passive_advanced missing count: {passive_adv_missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
