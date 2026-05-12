"""
RM1.26-C — Hero Skill Kit Read-Only Catalog Loader
─────────────────────────────────────────────────────────────────────────
Carica i cataloghi inert hero skill kit (5★ full + 6★ launch_base + Borea
extra premium + schema) installati in RM1.26-A/B/B2.

PURE READ-ONLY:
  • Nessuna mutation DB
  • Nessuna scrittura su disco
  • NON normalizza i dati caricati in-place
  • NON importato dal battle runtime / engine / HP bar runtime
  • Solo cache in-memory thread-safe lazy-loaded

Consumato esclusivamente da routes/hero_skill_kits_catalogs.py
per esposizione browser/design catalog API.
"""
from __future__ import annotations

import json
import os
from threading import Lock
from typing import Any, Dict, List, Optional

# ── Source files (RM1.26-A/B/B2 installation paths) ─────────────────────
_BASE = "/app/data/design/hero_skill_kits"

_FILES = {
    "schema":   "hero_skill_kit_schema_v1.json",
    "5star":    "hero_skill_kits_5star_full_v1.json",
    "6star":    "hero_skill_kits_6star_borea_v1.json",
    "manifest": "hero_skill_kits_5star_manifest_v1.json",
}

# ── Cache thread-safe ───────────────────────────────────────────────────
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
                # Don't fail catastrophically — file may not exist
                # (es. ambiente di sviluppo parziale).
                _cache[key] = None


def get_catalog(name: str) -> Any:
    if name not in _FILES:
        raise KeyError(f"Unknown catalog: {name}")
    _ensure_loaded()
    return _cache[name]


# ── Entries helpers (no normalization, just .entries accessor) ──────────
def _entries(catalog: Any) -> List[Dict[str, Any]]:
    if isinstance(catalog, dict):
        e = catalog.get("entries")
        if isinstance(e, list):
            return e
    return []


def get_5star_entries() -> List[Dict[str, Any]]:
    return _entries(get_catalog("5star"))


def get_6star_entries() -> List[Dict[str, Any]]:
    return _entries(get_catalog("6star"))


def get_schema() -> Any:
    return get_catalog("schema")


# ── Counters for 6★ split ───────────────────────────────────────────────
def _split_6star() -> Dict[str, List[Dict[str, Any]]]:
    """Return {'launch_base': [...], 'extra_premium': [...]}."""
    launch = []
    premium = []
    for e in get_6star_entries():
        rg = str(e.get("release_group") or "").lower()
        if rg == "launch_extra_premium":
            premium.append(e)
        else:
            launch.append(e)
    return {"launch_base": launch, "extra_premium": premium}


def find_by_hero_id(hero_id: str) -> Optional[Dict[str, Any]]:
    """Search across 5★ + 6★ catalogs by hero_id. Returns enriched payload
    or None. Read-only lookup, no caching beyond per-process JSON cache.
    """
    if not hero_id:
        return None
    needle = str(hero_id).strip().lower()
    for e in get_5star_entries():
        if str(e.get("hero_id") or "").lower() == needle:
            return {"found_in": "5star", "entry": e}
    for e in get_6star_entries():
        if str(e.get("hero_id") or "").lower() == needle:
            rg = str(e.get("release_group") or "").lower()
            tag = ("6star_extra_premium"
                   if rg == "launch_extra_premium"
                   else "6star_launch_base")
            return {"found_in": tag, "entry": e}
    return None


# ── Summary ─────────────────────────────────────────────────────────────
_RUNTIME_FLAGS = {
    "runtime_attached": False,
    "battle_runtime_attached": False,
    "ui_runtime_attached": False,
    "hp_bar_runtime_attached": False,
    "balance_values_finalized": False,
    "do_not_treat_as_live_kit": True,
}


def get_summary() -> Dict[str, Any]:
    """Pure read-only summary derivation."""
    five = get_5star_entries()
    six_split = _split_6star()
    cat_5 = get_catalog("5star") or {}
    cat_6 = get_catalog("6star") or {}
    return {
        "version": "RM1.26-C",
        "five_star_entries_count": len(five),
        "six_star_launch_base_entries_count": len(six_split["launch_base"]),
        "six_star_extra_premium_entries_count": len(six_split["extra_premium"]),
        "six_star_total_entries_count": len(six_split["launch_base"]) + len(six_split["extra_premium"]),
        "total_catalog_entries_count": (
            len(five) + len(six_split["launch_base"]) + len(six_split["extra_premium"])
        ),
        **_RUNTIME_FLAGS,
        "source_directory": _BASE,
        "files": dict(_FILES),
        "catalog_metadata": {
            "5star": {
                "id_policy": cat_5.get("id_policy"),
                "source_schema": cat_5.get("source_schema"),
                "conversion_schema": cat_5.get("conversion_schema"),
            },
            "6star": {
                "catalog_id": cat_6.get("catalog_id"),
                "version": cat_6.get("version"),
            },
        },
        "notes": (
            "Hero skill kit catalogs are inert/read-only and NOT connected "
            "to battle runtime, HP bar runtime, status runtime or VFX runtime."
        ),
    }
