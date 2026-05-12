"""
RM1.25-C — Skill / Status / Icon / VFX Read-Only Catalog Loader
─────────────────────────────────────────────────────────────────────────
Carica i 5 cataloghi metadata inerti installati in RM1.25-B e li tiene
in memoria con cache process-wide. PURE READ-ONLY: nessuna mutation DB,
nessun side-effect runtime, nessun import nel battle engine.

I cataloghi NON sono collegati al combat runtime: questo loader è
consumato solamente da `routes/skill_status_vfx_catalogs.py` (read-only
API) per fini di design/UI catalog browsing.

CACHE: lazy-loaded al primo accesso, mantenuto in memoria fino a restart
del processo. NESSUNA scrittura su disco.
"""
from __future__ import annotations

import json
import os
from threading import Lock
from typing import Any, Dict

# ── Path costants (read-only) ───────────────────────────────────────────
_CATALOG_DIR = "/app/data/design/skill_status_vfx_catalogs"

_FILES = {
    "skill_progression":   "skill_slot_progression_v1.json",
    "status_effects":      "status_effect_catalog_v1.json",
    "status_icons":        "status_icon_registry_v1.json",
    "vfx":                 "vfx_modular_catalog_v1.json",
    "skill_examples":      "skill_schema_examples_v1.json",
}

# ── In-memory cache ─────────────────────────────────────────────────────
_cache: Dict[str, Any] = {}
_cache_lock = Lock()


def _read_json_file(path: str) -> Any:
    """Read a JSON file from disk. Read-only. No write."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Catalog file missing: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _ensure_loaded() -> None:
    """Lazy-load all catalogs into memory (thread-safe)."""
    with _cache_lock:
        if _cache:
            return
        for key, fname in _FILES.items():
            _cache[key] = _read_json_file(os.path.join(_CATALOG_DIR, fname))


def get_catalog(name: str) -> Any:
    """Return cached catalog by short name."""
    if name not in _FILES:
        raise KeyError(f"Unknown catalog: {name}. Allowed: {sorted(_FILES.keys())}")
    _ensure_loaded()
    return _cache[name]


def get_skill_progression() -> Any:
    return get_catalog("skill_progression")


def get_status_effects() -> Any:
    return get_catalog("status_effects")


def get_status_icons() -> Any:
    return get_catalog("status_icons")


def get_vfx() -> Any:
    return get_catalog("vfx")


def get_skill_examples() -> Any:
    return get_catalog("skill_examples")


# ── Summary metrics (light derivations only, no mutation) ───────────────
_OFFICIAL_ELEMENTS = ["dark", "earth", "fire", "light", "lightning", "water", "wind"]


def _count_statuses(catalog: Any) -> int:
    """Count statuses across catalog. Supports list of objects or dict of objects."""
    if isinstance(catalog, list):
        return len(catalog)
    if isinstance(catalog, dict):
        # Common shape: {"statuses":[...]} or {"<id>": {...}, ...}
        if "statuses" in catalog and isinstance(catalog["statuses"], list):
            return len(catalog["statuses"])
        # Pure id->entry mapping
        return len([k for k, v in catalog.items() if isinstance(v, dict)])
    return 0


def _count_status_icons(catalog: Any) -> int:
    if isinstance(catalog, dict):
        if "icons" in catalog and isinstance(catalog["icons"], list):
            return len(catalog["icons"])
        if "icons" in catalog and isinstance(catalog["icons"], dict):
            return len(catalog["icons"])
        return len([k for k, v in catalog.items() if isinstance(v, dict)])
    if isinstance(catalog, list):
        return len(catalog)
    return 0


def _vfx_metrics(catalog: Any) -> Dict[str, int]:
    """Returns {types:int, entries:int}."""
    types_count = 0
    entries_count = 0
    if isinstance(catalog, dict):
        # Shape A: {"vfx_types": [...], "vfx_entries": [...]}  (RM1.25-B canonical)
        for tk in ("vfx_types", "types"):
            if tk in catalog and isinstance(catalog[tk], list):
                types_count = len(catalog[tk])
                break
        for ek in ("vfx_entries", "entries"):
            if ek in catalog and isinstance(catalog[ek], list):
                entries_count = len(catalog[ek])
                break
        # Shape B fallback: {"<type>": [entries...], ...}
        if not entries_count:
            grouped_entries = 0
            inferred_types = 0
            for k, v in catalog.items():
                if isinstance(v, list):
                    inferred_types += 1
                    grouped_entries += len(v)
                elif isinstance(v, dict):
                    grouped_entries += 1
            if grouped_entries:
                entries_count = grouped_entries
                if not types_count:
                    types_count = inferred_types
    elif isinstance(catalog, list):
        entries_count = len(catalog)
    return {"types": types_count, "entries": entries_count}


def _count_skill_examples(catalog: Any) -> int:
    if isinstance(catalog, list):
        return len(catalog)
    if isinstance(catalog, dict):
        if "examples" in catalog and isinstance(catalog["examples"], list):
            return len(catalog["examples"])
        return len([k for k, v in catalog.items() if isinstance(v, dict)])
    return 0


def get_summary() -> Dict[str, Any]:
    """Return a lightweight summary of catalog metrics.

    PURE READ-ONLY derivation. Does NOT mutate the catalogs.
    """
    _ensure_loaded()
    statuses_count = _count_statuses(_cache["status_effects"])
    icons_count = _count_status_icons(_cache["status_icons"])
    vfx_metrics = _vfx_metrics(_cache["vfx"])
    skill_examples_count = _count_skill_examples(_cache["skill_examples"])

    return {
        "version": "RM1.25-C",
        "official_elements": _OFFICIAL_ELEMENTS,
        "official_elements_count": len(_OFFICIAL_ELEMENTS),
        "core_statuses_count": statuses_count,
        "status_icons_count": icons_count,
        "vfx_types_count": vfx_metrics["types"],
        "vfx_entries_count": vfx_metrics["entries"],
        "skill_examples_count": skill_examples_count,
        "battle_runtime_attached": False,
        "ui_runtime_attached": False,
        "source": "/app/data/design/skill_status_vfx_catalogs/",
        "files": dict(_FILES),
        "notes": (
            "Read-only catalog metadata. NOT connected to battle runtime. "
            "Not driving live skills/statuses/VFX/icons."
        ),
    }
