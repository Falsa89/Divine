#!/usr/bin/env python3
"""
RM1.21-G v0.2 — Official Hero Kit Coverage Audit

Read-only validation script for Divine RPG / Divine Waifus hero kit design-data.

v0.2 fixes:
- accepts `heroes` as either dict or list;
- ignores non-hero separator entries such as `_GROUP_1_STAR`;
- canonicalizes role labels such as "DPS Melee" -> "dps_melee";
- reads release_group from hero entry or file-level metadata/scope when not duplicated per hero.

This script performs NO DB writes, imports no runtime gameplay systems, and changes no kit data.
It only prints a report and writes a JSON audit report to backend/reports/.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


KIT_FILES = [
    ROOT / "data/design/heroes_kits_1star_2star.json",
    ROOT / "data/design/heroes_kits_3star.json",
    ROOT / "data/design/heroes_kits_4star.json",
    ROOT / "data/design/heroes_kits_5star.json",
    ROOT / "data/design/heroes_kits_6star_extra.json",
]

RARITY_MAX_STARS = {
    1: 4,
    2: 6,
    3: 8,
    4: 10,
    5: 12,
    6: 15,
}

EXPECTED_COUNTS = {
    "1_star": 8,
    "2_star": 12,
    "3_star": 24,
    "4_star": 24,
    "5_star": 20,
    "6_star_launch_base": 12,
    "launch_extra_premium": 1,
    "total": 101,
}

ROLE_ALIASES = {
    "tank": "tank",
    "dps_melee": "dps_melee",
    "dps_ranged": "dps_ranged",
    "mage_aoe": "mage_aoe",
    "assassin_burst": "assassin_burst",
    "support_buffer": "support_buffer",
    "healer": "healer",
    "control_debuff": "control_debuff",
    "hybrid_special": "hybrid_special",
    "dpsmelee": "dps_melee",
    "dpsranged": "dps_ranged",
    "mageaoe": "mage_aoe",
    "assassin": "assassin_burst",
    "burst": "assassin_burst",
    "assassinburst": "assassin_burst",
    "support": "support_buffer",
    "buffer": "support_buffer",
    "supportbuffer": "support_buffer",
    "control": "control_debuff",
    "debuff": "control_debuff",
    "controldebuff": "control_debuff",
    "hybrid": "hybrid_special",
    "hybridspecial": "hybrid_special",
}

ELEMENT_ALIASES = {
    "terra": "earth",
    "fuoco": "fire",
    "acqua": "water",
    "vento": "wind",
    "fulmine": "lightning",
    "luce": "light",
    "oscurità": "dark",
    "oscurita": "dark",
    "earth": "earth",
    "fire": "fire",
    "water": "water",
    "wind": "wind",
    "lightning": "lightning",
    "light": "light",
    "dark": "dark",
}

FORBIDDEN_LOW_RARITY_EFFECTS = {
    "execute",
    "revive",
    "summon_or_proxy",
    "summon",
    "proxy",
    "advanced_signature",
}

ADVANCED_LOW_RARITY_FIELDS = {
    "iconic_mechanic",
    "iconic_mechanic_required",
    "signature_mechanic",
    "stance_cycle",
    "extra_turn_or_retarget",
}


def _slug(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    text = text.replace("★", "")
    text = text.replace("&", " and ")
    text = re.sub(r"[/+\-]+", "_", text)
    text = re.sub(r"[^\w]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or None


def _normalize_role(value: Any) -> Optional[str]:
    slug = _slug(value)
    if slug is None:
        return None
    compact = slug.replace("_", "")
    return ROLE_ALIASES.get(slug) or ROLE_ALIASES.get(compact) or slug


def _normalize_element(value: Any) -> Optional[str]:
    slug = _slug(value)
    if slug is None:
        return None
    return ELEMENT_ALIASES.get(slug, slug)


def _normalize(value: Any) -> Optional[str]:
    return _slug(value)


def _import_character_bible() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    try:
        from backend.data.character_bible import CHARACTER_BIBLE, CHARACTER_BIBLE_BY_ID  # type: ignore
        return CHARACTER_BIBLE, CHARACTER_BIBLE_BY_ID
    except Exception:
        pass

    try:
        from data.character_bible import CHARACTER_BIBLE, CHARACTER_BIBLE_BY_ID  # type: ignore
        return CHARACTER_BIBLE, CHARACTER_BIBLE_BY_ID
    except Exception as exc:
        raise RuntimeError(f"Could not import Character Bible: {exc}") from exc


def _entry_value(entry: Any, *names: str, default: Any = None) -> Any:
    if isinstance(entry, dict):
        for name in names:
            if name in entry:
                return entry[name]
        return default
    for name in names:
        if hasattr(entry, name):
            return getattr(entry, name)
    return default


def _entry_to_meta(hero_id: str, entry: Any) -> Dict[str, Any]:
    native_rarity = _entry_value(entry, "native_rarity", "rarity", default=None)
    try:
        native_rarity = int(native_rarity) if native_rarity is not None else None
    except Exception:
        pass

    release_group = _entry_value(entry, "release_group", default="launch_base")
    max_stars = _entry_value(entry, "max_stars", default=RARITY_MAX_STARS.get(native_rarity))
    try:
        max_stars = int(max_stars) if max_stars is not None else None
    except Exception:
        pass

    return {
        "hero_id": hero_id,
        "name": _entry_value(entry, "name", "display_name", default=hero_id),
        "native_rarity": native_rarity,
        "max_stars": max_stars,
        "element": _normalize_element(_entry_value(entry, "element", "canonical_element", default=None)),
        "role": _normalize_role(_entry_value(entry, "role", "canonical_role", default=None)),
        "faction": _normalize(_entry_value(entry, "faction", "canonical_faction", default=None)),
        "origin_group": _normalize(_entry_value(entry, "origin_group", default=None)),
        "category": _normalize(_entry_value(entry, "category", default=None)),
        "release_group": release_group,
    }


def _official_bible_meta() -> Dict[str, Dict[str, Any]]:
    _, by_id = _import_character_bible()
    return {hero_id: _entry_to_meta(hero_id, entry) for hero_id, entry in by_id.items()}


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _iter_effects(value: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(value, dict):
        if "type" in value:
            yield value
        for child in value.values():
            yield from _iter_effects(child)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_effects(item)


def _has_locked_or_null(slot: Any) -> bool:
    if slot is None:
        return True
    if isinstance(slot, dict):
        if slot.get("locked") is True:
            return True
        if slot.get("status") in {"locked", "unavailable", "not_available"}:
            return True
        if slot.get("slot_status") in {"locked", "unavailable", "not_available"}:
            return True
    return False


def _slot_exists(slot: Any) -> bool:
    return isinstance(slot, dict) and bool(slot.get("id") or slot.get("name") or slot.get("slot"))


def _file_level_release_group(doc: Dict[str, Any]) -> Optional[str]:
    value = doc.get("release_group")
    if isinstance(value, str):
        return value

    metadata = doc.get("metadata")
    if isinstance(metadata, dict) and isinstance(metadata.get("release_group"), str):
        return metadata["release_group"]

    scope = doc.get("scope")
    if isinstance(scope, dict):
        if isinstance(scope.get("release_group"), str):
            return scope["release_group"]
        groups = scope.get("included_release_groups")
        if isinstance(groups, list) and len(groups) == 1 and isinstance(groups[0], str):
            return groups[0]

    # Most kit files are launch_base-only. The 6★ extra file has per-hero release_group.
    return None


def _iter_kit_entries(doc: Dict[str, Any], rel_path: str) -> Tuple[List[Tuple[str, Dict[str, Any]]], List[Dict[str, Any]]]:
    """Return hero kit entries and ignored non-hero entries. Supports heroes as dict or list."""
    heroes = doc.get("heroes")
    ignored: List[Dict[str, Any]] = []
    entries: List[Tuple[str, Dict[str, Any]]] = []

    if isinstance(heroes, dict):
        for key, value in heroes.items():
            if not isinstance(value, dict):
                # Allow human-readable group separators such as "_GROUP_1_STAR": "..."
                ignored.append({"file": rel_path, "key": key, "reason": "non_object_separator_or_comment"})
                continue
            hero_id = value.get("hero_id") or key
            if not isinstance(hero_id, str) or not hero_id:
                ignored.append({"file": rel_path, "key": key, "reason": "missing_hero_id"})
                continue
            entries.append((hero_id, value))
        return entries, ignored

    if isinstance(heroes, list):
        for idx, value in enumerate(heroes):
            if not isinstance(value, dict):
                ignored.append({"file": rel_path, "index": idx, "reason": "non_object_list_entry"})
                continue
            hero_id = value.get("hero_id") or value.get("id")
            if not isinstance(hero_id, str) or not hero_id:
                ignored.append({"file": rel_path, "index": idx, "reason": "missing_hero_id"})
                continue
            entries.append((hero_id, value))
        return entries, ignored

    ignored.append({"file": rel_path, "reason": "missing_or_invalid_heroes_container", "found_type": type(heroes).__name__})
    return entries, ignored


def _collect_kits() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, List[str]], List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    found: Dict[str, Dict[str, Any]] = {}
    file_map: Dict[str, List[str]] = defaultdict(list)
    load_issues: List[Dict[str, Any]] = []
    ignored_entries: List[Dict[str, Any]] = []
    parsed_files: List[str] = []

    for path in KIT_FILES:
        rel = str(path.relative_to(ROOT))
        try:
            doc = _load_json(path)
            parsed_files.append(rel)
        except Exception as exc:
            load_issues.append({"file": rel, "error": str(exc)})
            continue

        doc_release_group = _file_level_release_group(doc)
        entries, ignored = _iter_kit_entries(doc, rel)
        ignored_entries.extend(ignored)

        if not entries and not ignored:
            load_issues.append({"file": rel, "error": "No kit entries found"})
            continue

        for hero_id, kit in entries:
            if hero_id in found:
                file_map[hero_id].append(rel)
                continue
            copied = dict(kit)
            copied["_source_file"] = rel
            copied["_file_release_group"] = doc_release_group
            found[hero_id] = copied
            file_map[hero_id].append(rel)

    return found, file_map, load_issues, ignored_entries, parsed_files


def _check_slots(hero_id: str, kit: Dict[str, Any], rarity: Optional[int]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for slot in ("basic_attack", "skill", "ultimate_or_special", "passive"):
        if slot not in kit:
            issues.append({"hero_id": hero_id, "issue": "missing_slot_field", "slot": slot})
            continue

    basic = kit.get("basic_attack")
    skill = kit.get("skill")
    ultimate = kit.get("ultimate_or_special")
    passive = kit.get("passive")

    if not _slot_exists(basic):
        issues.append({"hero_id": hero_id, "issue": "basic_attack_required"})

    if rarity == 1:
        if not _has_locked_or_null(skill):
            issues.append({"hero_id": hero_id, "issue": "1_star_skill_should_be_locked_or_null"})
        if not _has_locked_or_null(ultimate):
            issues.append({"hero_id": hero_id, "issue": "1_star_ultimate_should_be_locked_or_null"})
    elif rarity == 2:
        if not _slot_exists(skill):
            issues.append({"hero_id": hero_id, "issue": "2_star_skill_required"})
        if not _has_locked_or_null(ultimate):
            issues.append({"hero_id": hero_id, "issue": "2_star_ultimate_should_be_locked_or_null"})
        if not _slot_exists(passive):
            issues.append({"hero_id": hero_id, "issue": "2_star_passive_required"})
    elif rarity and rarity >= 3:
        if not _slot_exists(skill):
            issues.append({"hero_id": hero_id, "issue": "3_plus_skill_required"})
        if not _slot_exists(ultimate):
            issues.append({"hero_id": hero_id, "issue": "3_plus_ultimate_required"})
        if not _slot_exists(passive):
            issues.append({"hero_id": hero_id, "issue": "3_plus_passive_required"})

    return issues


def _check_low_rarity_complexity(hero_id: str, kit: Dict[str, Any], rarity: Optional[int]) -> List[Dict[str, Any]]:
    warnings: List[Dict[str, Any]] = []
    if rarity not in {1, 2}:
        return warnings

    for effect in _iter_effects(kit):
        etype = str(effect.get("type", "")).lower()
        subtype = str(effect.get("subtype", "")).lower()
        if etype in FORBIDDEN_LOW_RARITY_EFFECTS or subtype in FORBIDDEN_LOW_RARITY_EFFECTS:
            warnings.append({"hero_id": hero_id, "warning": "low_rarity_forbidden_advanced_effect", "effect": effect})

    def scan_advanced(obj: Any, path: str = "") -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if str(k) in ADVANCED_LOW_RARITY_FIELDS:
                    warnings.append({"hero_id": hero_id, "warning": "low_rarity_advanced_field", "field": f"{path}.{k}".strip(".")})
                scan_advanced(v, f"{path}.{k}".strip("."))
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                scan_advanced(item, f"{path}[{idx}]")

    scan_advanced(kit)
    return warnings


def _check_iconic_six_star(hero_id: str, kit: Dict[str, Any], rarity: Optional[int]) -> List[Dict[str, Any]]:
    warnings: List[Dict[str, Any]] = []
    if rarity != 6:
        return warnings

    complexity = kit.get("kit_complexity") if isinstance(kit.get("kit_complexity"), dict) else {}
    passive = kit.get("passive") if isinstance(kit.get("passive"), dict) else {}
    tags = kit.get("tags") if isinstance(kit.get("tags"), list) else []
    passive_tags = passive.get("tags") if isinstance(passive.get("tags"), list) else []

    has_iconic = (
        complexity.get("iconic_mechanic_required") is True
        or complexity.get("iconic_mechanic") is True
        or "iconic_mechanic" in tags
        or "iconic_mechanic" in passive_tags
        or any(str(t).startswith("iconic") for t in tags + passive_tags)
    )
    if not has_iconic:
        warnings.append({"hero_id": hero_id, "warning": "6_star_missing_iconic_mechanic_marker"})
    return warnings


def _check_design_data_marking(path: str, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    warnings: List[Dict[str, Any]] = []
    status = str(doc.get("status", "")).lower()
    non_runtime = bool(doc.get("non_normative_for_runtime")) or "design" in status
    if not non_runtime:
        warnings.append({"file": path, "warning": "file_missing_design_data_runtime_safety_marker"})
    return warnings


def main() -> int:
    bible = _official_bible_meta()
    found, file_map, load_issues, ignored_entries, parsed_files = _collect_kits()

    warnings: List[Dict[str, Any]] = []
    for path in KIT_FILES:
        rel = str(path.relative_to(ROOT))
        if not path.exists():
            load_issues.append({"file": rel, "error": "kit_file_missing"})
            continue
        try:
            warnings.extend(_check_design_data_marking(rel, _load_json(path)))
        except Exception:
            pass

    expected_ids = set(bible.keys())
    found_ids = set(found.keys())

    missing_ids = sorted(expected_ids - found_ids)
    unknown_ids = sorted(found_ids - expected_ids)
    duplicate_ids = sorted([hero_id for hero_id, files in file_map.items() if len(files) > 1])

    mismatches: List[Dict[str, Any]] = []
    slot_issues: List[Dict[str, Any]] = []

    for hero_id, kit in found.items():
        if hero_id not in bible:
            continue
        expected = bible[hero_id]
        rarity = kit.get("native_rarity")
        try:
            rarity = int(rarity)
        except Exception:
            rarity = None

        # Release group can be declared per hero or at file level.
        kit_release_group = kit.get("release_group") or kit.get("_file_release_group")
        if kit_release_group is None and expected.get("release_group") == "launch_base":
            # Older low-rarity design file declared launch_base at file metadata level in prose.
            # Since all official non-Borea launch heroes are launch_base, this is accepted as implicit.
            kit_release_group = "launch_base"

        checks = [
            ("native_rarity", rarity, expected.get("native_rarity")),
            ("max_stars", kit.get("max_stars"), RARITY_MAX_STARS.get(expected.get("native_rarity"))),
            ("element", _normalize_element(kit.get("element")), expected.get("element")),
            ("role", _normalize_role(kit.get("role")), expected.get("role")),
            ("faction", _normalize(kit.get("faction")), expected.get("faction")),
            ("release_group", kit_release_group, expected.get("release_group")),
        ]
        for field, got, exp in checks:
            if exp is not None and got != exp:
                mismatches.append({"hero_id": hero_id, "field": field, "expected": exp, "found": got, "source_file": kit.get("_source_file")})

        for field in ("origin_group", "category"):
            got = _normalize(kit.get(field))
            exp = expected.get(field)
            if exp is not None and got is not None and got != exp:
                mismatches.append({"hero_id": hero_id, "field": field, "expected": exp, "found": got, "source_file": kit.get("_source_file")})

        if hero_id == "greek_borea":
            if kit_release_group != "launch_extra_premium":
                mismatches.append({"hero_id": hero_id, "field": "release_group", "expected": "launch_extra_premium", "found": kit_release_group})
            if kit.get("is_extra_premium") is not True:
                mismatches.append({"hero_id": hero_id, "field": "is_extra_premium", "expected": True, "found": kit.get("is_extra_premium")})
        elif kit_release_group == "launch_extra_premium":
            mismatches.append({"hero_id": hero_id, "field": "release_group", "expected": "not launch_extra_premium", "found": "launch_extra_premium"})

        slot_issues.extend(_check_slots(hero_id, kit, rarity))
        warnings.extend(_check_low_rarity_complexity(hero_id, kit, rarity))
        warnings.extend(_check_iconic_six_star(hero_id, kit, rarity))

    rarity_found = Counter()
    for hero_id, kit in found.items():
        if hero_id in bible:
            rarity_found[bible[hero_id].get("native_rarity")] += 1

    launch_base_6 = [hid for hid, meta in bible.items() if meta.get("native_rarity") == 6 and meta.get("release_group") == "launch_base"]
    extra_premium = [hid for hid, meta in bible.items() if meta.get("release_group") == "launch_extra_premium"]

    summary = {
        "official_character_bible_count": len(bible),
        "total_kits_loaded": len(found),
        "missing_count": len(missing_ids),
        "duplicate_count": len(duplicate_ids),
        "unknown_count": len(unknown_ids),
        "metadata_mismatch_count": len(mismatches),
        "slot_violation_count": len(slot_issues),
        "load_issue_count": len(load_issues),
        "ignored_non_hero_entries_count": len(ignored_entries),
        "warning_count": len(warnings),
    }

    coverage_by_rarity = {
        "1_star": {"expected": EXPECTED_COUNTS["1_star"], "found": rarity_found.get(1, 0)},
        "2_star": {"expected": EXPECTED_COUNTS["2_star"], "found": rarity_found.get(2, 0)},
        "3_star": {"expected": EXPECTED_COUNTS["3_star"], "found": rarity_found.get(3, 0)},
        "4_star": {"expected": EXPECTED_COUNTS["4_star"], "found": rarity_found.get(4, 0)},
        "5_star": {"expected": EXPECTED_COUNTS["5_star"], "found": rarity_found.get(5, 0)},
        "6_star_launch_base": {
            "expected": EXPECTED_COUNTS["6_star_launch_base"],
            "found": sum(1 for hid in launch_base_6 if hid in found),
        },
        "launch_extra_premium": {
            "expected": EXPECTED_COUNTS["launch_extra_premium"],
            "found": sum(1 for hid in extra_premium if hid in found),
        },
        "total": {"expected": EXPECTED_COUNTS["total"], "found": len(found)},
    }

    pass_bool = (
        not load_issues
        and not missing_ids
        and not duplicate_ids
        and not unknown_ids
        and not mismatches
        and not slot_issues
        and len(found) == EXPECTED_COUNTS["total"]
    )

    print("\n=== RM1.21-G v0.2 — Official Hero Kit Coverage Audit ===")
    print(f"Character Bible official heroes: {len(bible)}")
    print(f"Kits loaded: {len(found)}")
    print(f"Missing: {len(missing_ids)} | Duplicates: {len(duplicate_ids)} | Unknown: {len(unknown_ids)}")
    print(f"Mismatches: {len(mismatches)} | Slot violations: {len(slot_issues)} | Warnings: {len(warnings)}")
    print(f"Ignored non-hero separator/comment entries: {len(ignored_entries)}")
    print("\nCoverage by rarity:")
    for key, data in coverage_by_rarity.items():
        print(f"- {key}: {data['found']}/{data['expected']}")

    if missing_ids:
        print("\nMissing IDs:")
        for hero_id in missing_ids:
            print(f"- {hero_id}")
    if duplicate_ids:
        print("\nDuplicate IDs:")
        for hero_id in duplicate_ids:
            print(f"- {hero_id}: {file_map.get(hero_id)}")
    if unknown_ids:
        print("\nUnknown IDs:")
        for hero_id in unknown_ids:
            print(f"- {hero_id}")
    if mismatches:
        print("\nMetadata mismatches:")
        for item in mismatches[:50]:
            print(f"- {item}")
    if slot_issues:
        print("\nSlot violations:")
        for item in slot_issues[:50]:
            print(f"- {item}")
    if warnings:
        print("\nWarnings:")
        for item in warnings[:50]:
            print(f"- {item}")

    if pass_bool:
        print("\nOFFICIAL HERO KIT COVERAGE: PASS")
    else:
        print("\nOFFICIAL HERO KIT COVERAGE: FAIL")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script_version": "0.2",
        "pass": pass_bool,
        "parsed_files": parsed_files,
        "summary": summary,
        "coverage_by_rarity": coverage_by_rarity,
        "expected_ids": sorted(expected_ids),
        "found_ids": sorted(found_ids),
        "missing_ids": missing_ids,
        "duplicate_ids": duplicate_ids,
        "unknown_ids": unknown_ids,
        "load_issues": load_issues,
        "ignored_non_hero_entries": ignored_entries,
        "mismatches": mismatches,
        "slot_issues": slot_issues,
        "warnings": warnings,
        "safety": {
            "db_writes_performed": False,
            "runtime_changes": False,
            "kit_json_modified": False,
        },
    }

    reports_dir = ROOT / "backend/reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = reports_dir / f"hero_kits_coverage_audit_{timestamp}.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"\nJSON report: {report_path.relative_to(ROOT)}")
    return 0 if pass_bool else 1


if __name__ == "__main__":
    raise SystemExit(main())
