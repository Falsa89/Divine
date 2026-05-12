"""
RM1.26-C — Hero Skill Kit Read-Only Catalog Routes
─────────────────────────────────────────────────────────────────────────
5 GET endpoints pubblici per consultare i cataloghi inert hero skill kit
5★/6★. NESSUN write method. NESSUN battle/HP-bar/VFX runtime hookup.

Endpoints:
  GET /api/hero-skill-kits/catalogs/summary
  GET /api/hero-skill-kits/catalogs/schema
  GET /api/hero-skill-kits/catalogs/5star
  GET /api/hero-skill-kits/catalogs/6star
  GET /api/hero-skill-kits/catalogs/by-hero/{hero_id}
"""
from fastapi import HTTPException

from data.hero_skill_kits_loader import (
    get_summary,
    get_schema,
    get_catalog,
    get_5star_entries,
    get_6star_entries,
    find_by_hero_id,
)


def register_hero_skill_kits_catalog_routes(router):
    """Register 5 GET endpoints. Public (no auth)."""

    @router.get("/hero-skill-kits/catalogs/summary")
    async def hsk_summary():
        """Lightweight metrics + runtime flags (all false)."""
        return get_summary()

    @router.get("/hero-skill-kits/catalogs/schema")
    async def hsk_schema():
        """Approved hero skill kit schema v1.json (read-only)."""
        schema = get_schema()
        if schema is None:
            raise HTTPException(500, "Schema file not present on disk")
        return {
            "version": "RM1.26-C",
            "name": "hero_skill_kit_schema_v1",
            "runtime_attached": False,
            "data": schema,
        }

    @router.get("/hero-skill-kits/catalogs/5star")
    async def hsk_5star():
        """20 5★ launch_base entries (inert design catalog)."""
        cat = get_catalog("5star") or {}
        entries = get_5star_entries()
        return {
            "version": "RM1.26-C",
            "name": "hero_skill_kits_5star_full_v1",
            "runtime_attached": False,
            "battle_runtime_attached": False,
            "hp_bar_runtime_attached": False,
            "count": len(entries),
            "metadata": {
                "catalog_id": cat.get("catalog_id"),
                "source_file": cat.get("source_file"),
                "source_schema": cat.get("source_schema"),
                "conversion_schema": cat.get("conversion_schema"),
                "id_policy": cat.get("id_policy"),
                "balance_values_finalized": cat.get("balance_values_finalized"),
                "do_not_treat_as_live_kit": cat.get("do_not_treat_as_live_kit"),
            },
            "entries": entries,
        }

    @router.get("/hero-skill-kits/catalogs/6star")
    async def hsk_6star():
        """13 6★ entries (12 launch_base + 1 launch_extra_premium Borea).
        Inert catalog: Borea NON viene attivata da questa exposure.
        """
        cat = get_catalog("6star") or {}
        entries = get_6star_entries()
        launch_base = [e for e in entries if str(e.get("release_group") or "").lower() != "launch_extra_premium"]
        extra_premium = [e for e in entries if str(e.get("release_group") or "").lower() == "launch_extra_premium"]
        return {
            "version": "RM1.26-C",
            "name": "hero_skill_kits_6star_borea_v1",
            "runtime_attached": False,
            "battle_runtime_attached": False,
            "hp_bar_runtime_attached": False,
            "count": len(entries),
            "count_launch_base": len(launch_base),
            "count_extra_premium": len(extra_premium),
            "metadata": {
                "catalog_id": cat.get("catalog_id"),
                "version": cat.get("version"),
                "balance_values_finalized": cat.get("balance_values_finalized"),
                "do_not_treat_as_live_kit": cat.get("do_not_treat_as_live_kit"),
            },
            "borea_visibility_note": (
                "Borea entry is included in this inert design catalog only. "
                "Roster activation / gacha / battle availability NOT affected."
            ),
            "entries": entries,
        }

    @router.get("/hero-skill-kits/catalogs/by-hero/{hero_id}")
    async def hsk_by_hero(hero_id: str):
        """Lookup hero across 5★ + 6★ catalogs by hero_id (case-insensitive).

        Returns {found_in, entry, ...flags}. 404 se sconosciuto. NESSUN
        side-effect: lookup puro in cache in-memory.
        """
        result = find_by_hero_id(hero_id)
        if result is None:
            raise HTTPException(
                404,
                f"Hero '{hero_id}' not found in 5★ or 6★ catalogs. "
                "Lookup is read-only and does NOT mutate roster/DB.",
            )
        return {
            "version": "RM1.26-C",
            "hero_id_query": hero_id,
            "found_in": result["found_in"],
            "runtime_attached": False,
            "battle_runtime_attached": False,
            "hp_bar_runtime_attached": False,
            "entry": result["entry"],
        }
