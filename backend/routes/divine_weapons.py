"""
RM1.27-B — Divine Weapon Read-Only Catalog Routes
────────────────────────────────────────────────────────────────────────────
6 GET endpoints to consult inert Divine Weapon catalogs (RM1.27-A).
NO write methods. NO battle / HP bar / VFX / gacha / roster runtime hookup.

Endpoints:
  GET /api/divine-weapons/catalogs/summary
  GET /api/divine-weapons/catalogs/schema
  GET /api/divine-weapons/catalogs/requirements
  GET /api/divine-weapons/catalogs/all
  GET /api/divine-weapons/catalogs/by-hero/{hero_id}
  GET /api/divine-weapons/catalogs/by-weapon/{divine_weapon_id}

Borea safety:
  - greek_borea may be returned as catalog-only design data.
  - legacy `borea` must NOT resolve as alias (returns 404).
  - Returning catalog data does NOT trigger roster / gacha / battle / Borea
    activation.
"""
from fastapi import HTTPException

from data.divine_weapons_loader import (
    get_summary,
    get_schema,
    get_requirements,
    get_catalog,
    get_records,
    find_by_hero_id,
    find_by_weapon_id,
    _is_forbidden_alias,
)


def register_divine_weapons_catalog_routes(router):
    """Register 6 GET endpoints. Public (no auth)."""

    @router.get("/divine-weapons/catalogs/summary")
    async def dw_summary():
        """Lightweight metrics + runtime flags (all false). Read-only."""
        return get_summary()

    @router.get("/divine-weapons/catalogs/schema")
    async def dw_schema():
        """Approved divine_weapon_schema_v1.json (read-only)."""
        schema = get_schema()
        if schema is None:
            raise HTTPException(500, "Schema file not present on disk")
        return {
            "version": "RM1.27-B",
            "name": "divine_weapon_schema_v1",
            "runtime_attached": False,
            "battle_runtime_attached": False,
            "hp_bar_runtime_attached": False,
            "vfx_runtime_attached": False,
            "data": schema,
        }

    @router.get("/divine-weapons/catalogs/requirements")
    async def dw_requirements():
        """Approved divine_weapon_requirements_v1.json (read-only)."""
        reqs = get_requirements()
        if reqs is None:
            raise HTTPException(500, "Requirements file not present on disk")
        return {
            "version": "RM1.27-B",
            "name": "divine_weapon_requirements_v1",
            "runtime_attached": False,
            "battle_runtime_attached": False,
            "hp_bar_runtime_attached": False,
            "vfx_runtime_attached": False,
            "data": reqs,
        }

    @router.get("/divine-weapons/catalogs/all")
    async def dw_all():
        """All 13 Divine Weapon records (12 launch_base + 1 Borea extra premium).

        Inert catalog: Borea exposure here does NOT activate Borea.
        """
        cat = get_catalog() or {}
        records = get_records()
        launch_base = [r for r in records if str(r.get("release_group") or "").lower() == "launch_base"]
        extra_premium = [r for r in records if str(r.get("release_group") or "").lower() == "launch_extra_premium"]
        return {
            "version": "RM1.27-B",
            "name": "divine_weapons_catalog_v1",
            "runtime_attached": False,
            "battle_runtime_attached": False,
            "hp_bar_runtime_attached": False,
            "vfx_runtime_attached": False,
            "gacha_attached": False,
            "roster_activation_attached": False,
            "borea_activation_allowed": False,
            "balance_values_finalized": False,
            "do_not_treat_as_live_power": True,
            "count": len(records),
            "count_launch_base": len(launch_base),
            "count_launch_extra_premium": len(extra_premium),
            "metadata": {
                "catalog_id": cat.get("catalog_id"),
                "version": cat.get("version"),
                "schema_ref": cat.get("schema_ref"),
                "requirements_ref": cat.get("requirements_ref"),
                "id_override_notes": cat.get("id_override_notes"),
            },
            "borea_visibility_note": (
                "Borea (greek_borea) is exposed in this inert catalog only. "
                "Roster activation / gacha / battle availability is NOT affected."
            ),
            "records": records,
        }

    @router.get("/divine-weapons/catalogs/by-hero/{hero_id}")
    async def dw_by_hero(hero_id: str):
        """Strict hero_id lookup. Case-insensitive on full id only.

        404 on unknown hero or legacy `borea` alias.
        Returning catalog data does NOT activate Borea.
        """
        # Explicit forbidden alias check (legacy `borea`).
        if _is_forbidden_alias(hero_id):
            raise HTTPException(
                404,
                f"Hero '{hero_id}' is a non-canonical legacy alias and does NOT "
                "resolve. Use canonical hero_id 'greek_borea' for the Divine "
                "Weapon catalog lookup. Lookup is read-only and does NOT "
                "mutate roster/DB.",
            )
        record = find_by_hero_id(hero_id)
        if record is None:
            raise HTTPException(
                404,
                f"Hero '{hero_id}' not found in Divine Weapon catalog. "
                "Lookup is read-only and does NOT mutate roster/DB.",
            )
        return {
            "version": "RM1.27-B",
            "hero_id_query": hero_id,
            "runtime_attached": False,
            "battle_runtime_attached": False,
            "hp_bar_runtime_attached": False,
            "vfx_runtime_attached": False,
            "gacha_attached": False,
            "roster_activation_attached": False,
            "borea_activation_allowed": False,
            "catalog_only_note": (
                "Returning this record does NOT imply roster / gacha / battle "
                "/ Borea activation. Catalog-only read."
            ),
            "record": record,
        }

    @router.get("/divine-weapons/catalogs/by-weapon/{divine_weapon_id}")
    async def dw_by_weapon(divine_weapon_id: str):
        """Strict divine_weapon_id lookup. Case-insensitive.

        404 on unknown weapon.
        """
        record = find_by_weapon_id(divine_weapon_id)
        if record is None:
            raise HTTPException(
                404,
                f"Divine Weapon '{divine_weapon_id}' not found in catalog. "
                "Lookup is read-only and does NOT mutate roster/DB.",
            )
        return {
            "version": "RM1.27-B",
            "divine_weapon_id_query": divine_weapon_id,
            "runtime_attached": False,
            "battle_runtime_attached": False,
            "hp_bar_runtime_attached": False,
            "vfx_runtime_attached": False,
            "gacha_attached": False,
            "roster_activation_attached": False,
            "borea_activation_allowed": False,
            "catalog_only_note": (
                "Returning this record does NOT imply roster / gacha / battle "
                "/ Borea activation. Catalog-only read."
            ),
            "record": record,
        }
