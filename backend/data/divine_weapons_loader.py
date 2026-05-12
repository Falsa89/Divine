"""
RM1.27-B — Divine Weapon Read-Only Catalog Loader
────────────────────────────────────────────────────────────────────────────
Load inert/read-only Divine Weapon catalogs installed by RM1.27-A.

PURE READ-ONLY:
  • No DB mutation
  • No disk writes
  • No data normalization in-place
  • NOT imported by battle runtime / engine / HP bar runtime
  • Only in-memory thread-safe lazy cache

Consumed exclusively by routes/divine_weapons.py for read-only catalog
design API exposure. Returning catalog data does NOT imply roster /
gacha / battle / Borea activation.
"""
from __future__ import annotations

import json
import os
from threading import Lock
from typing import Any, Dict, List, Optional

# ── Source files (RM1.27-A installation paths) ──────────────────────────
_BASE = "/app/data/design/divine_weapons"

_FILES = {
    "schema":       "divine_weapon_schema_v1.json",
    "catalog":      "divine_weapons_catalog_v1.json",
    "requirements": "divine_weapon_requirements_v1.json",
}

# Legacy hero IDs that MUST NOT resolve as aliases. Returning catalog data
# for legacy `borea` is forbidden: the legacy hero is non-official and
# must remain disconnected from the canonical greek_borea Divine Weapon.
_FORBIDDEN_HERO_ID_ALIASES = {"borea"}

# ── Cache thread-safe ─────────────────────────────────────────────────
_cache: Dict[str, Any] = {}
_cache_lock = Lock()


def _read_json(path: str) -> Any:
    """Read-only JSON read."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _ensure_loaded() -> None:
    with _cache_lock:
        if _cache:
            return
        for key, fname in _FILES.items():
            full = os.path.join(_BASE, fname)
            if os.path.exists(full):
                _cache[key] = _read_json(full)
            else:
                # Don't fail catastrophically — file may not exist in a
                # partial dev environment.
                _cache[key] = None


def get_file(name: str) -> Any:
    if name not in _FILES:
        raise KeyError(f"Unknown divine weapon file: {name}")
    _ensure_loaded()
    return _cache[name]


def get_schema() -> Any:
    return get_file("schema")


def get_requirements() -> Any:
    return get_file("requirements")


def get_catalog() -> Any:
    return get_file("catalog")


def get_records() -> List[Dict[str, Any]]:
    cat = get_catalog()
    if isinstance(cat, dict):
        recs = cat.get("records")
        if isinstance(recs, list):
            return recs
    return []


def _is_forbidden_alias(query: str) -> bool:
    """Return True if the given hero_id is a forbidden legacy alias.

    Legacy `borea` must NOT resolve to `greek_borea`. Case-insensitive
    match against the configured blocklist.
    """
    if not query:
        return False
    return str(query).strip().lower() in _FORBIDDEN_HERO_ID_ALIASES


def find_by_hero_id(hero_id: str) -> Optional[Dict[str, Any]]:
    """Strict hero_id lookup. Case-insensitive on full id only.

    Returns the record dict or None. Read-only lookup. No side effects.
    """
    if not hero_id or _is_forbidden_alias(hero_id):
        return None
    needle = str(hero_id).strip().lower()
    for r in get_records():
        if str(r.get("hero_id") or "").lower() == needle:
            return r
    return None


def find_by_weapon_id(divine_weapon_id: str) -> Optional[Dict[str, Any]]:
    """Strict divine_weapon_id lookup. Case-insensitive.

    Returns the record dict or None. Read-only lookup.
    """
    if not divine_weapon_id:
        return None
    needle = str(divine_weapon_id).strip().lower()
    for r in get_records():
        if str(r.get("divine_weapon_id") or "").lower() == needle:
            return r
    return None


def _split_release_groups() -> Dict[str, List[Dict[str, Any]]]:
    base: List[Dict[str, Any]] = []
    extra: List[Dict[str, Any]] = []
    for r in get_records():
        rg = str(r.get("release_group") or "").lower()
        if rg == "launch_extra_premium":
            extra.append(r)
        elif rg == "launch_base":
            base.append(r)
    return {"launch_base": base, "launch_extra_premium": extra}


# ── Universal runtime safety flags (always false on this loader) ──────────────
_RUNTIME_FLAGS = {
    "runtime_attached": False,
    "battle_runtime_attached": False,
    "hp_bar_runtime_attached": False,
    "vfx_runtime_attached": False,
    "gacha_attached": False,
    "roster_activation_attached": False,
    "borea_activation_allowed": False,
    "balance_values_finalized": False,
    "do_not_treat_as_live_power": True,
}


def get_summary() -> Dict[str, Any]:
    """Pure read-only summary derivation. NO mutation."""
    records = get_records()
    split = _split_release_groups()
    cat = get_catalog() or {}
    schema = get_schema() or {}
    reqs = get_requirements() or {}

    base_count = len(split["launch_base"])
    extra_count = len(split["launch_extra_premium"])
    borea_record = next(
        (r for r in records if str(r.get("hero_id") or "").lower() == "greek_borea"),
        None,
    )
    borea_safety = {
        "hero_id": "greek_borea",
        "legacy_borea_allowed": False,
        "release_group": (borea_record.get("release_group") if borea_record else None),
        "divine_weapon_id": (borea_record.get("divine_weapon_id") if borea_record else None),
        "catalog_status": (borea_record.get("catalog_status") if borea_record else None),
        "borea_activation_allowed": (
            borea_record.get("safety_flags", {}).get("borea_activation_allowed")
            if borea_record
            else None
        ),
        "note": (
            "Borea is exposed only as catalog-only design data. "
            "Roster / gacha / battle visibility is NOT affected."
        ),
    }

    progression_summary = (
        schema.get("progression_state_definition", {}).get(
            "required_state_keys_in_order"
        )
        or []
    )

    return {
        "version": "RM1.27-B",
        "name": "divine_weapons_catalog_v1",
        "total_divine_weapons": len(records),
        "launch_base_count": base_count,
        "launch_extra_premium_count": extra_count,
        "native_rarity_required": 6,
        "catalog_status": cat.get("catalog_id") and "catalog_only" or "catalog_only",
        **_RUNTIME_FLAGS,
        "required_hero_star_level_to_break_seal": (
            reqs.get("unlock_requirements_contract", {}).get(
                "required_hero_star_level"
            )
            or 10
        ),
        "progression_states": progression_summary,
        "borea_safety": borea_safety,
        "source_directory": _BASE,
        "files": dict(_FILES),
        "notes": (
            "Divine Weapon catalog is inert/read-only and NOT connected to "
            "battle runtime, HP bar runtime, status runtime, VFX runtime, "
            "gacha, or roster activation. Returning Borea catalog data does "
            "NOT activate Borea."
        ),
    }
