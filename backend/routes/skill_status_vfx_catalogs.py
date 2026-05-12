"""
RM1.25-C — Skill / Status / Icon / VFX Read-Only Catalog Routes
─────────────────────────────────────────────────────────────────────────
Endpoint pubblici read-only che espongono i 5 cataloghi metadata inerti
(installati in RM1.25-B) per consumo da pannelli design/UI di catalogo.

PRINCIPI:
 • PURE READ-ONLY — nessuna mutation DB
 • NESSUN collegamento al battle runtime / engine
 • NESSUNA scrittura sui file di catalogo
 • NESSUN side-effect oltre alla cache in memoria del loader

Endpoints registrati (tutti GET):
  /api/skill-status-vfx/catalogs/summary
  /api/skill-status-vfx/catalogs/skill-progression
  /api/skill-status-vfx/catalogs/status-effects
  /api/skill-status-vfx/catalogs/status-icons
  /api/skill-status-vfx/catalogs/vfx
  /api/skill-status-vfx/catalogs/skill-examples
"""
from fastapi import HTTPException

from data.skill_status_vfx_loader import (
    get_summary,
    get_skill_progression,
    get_status_effects,
    get_status_icons,
    get_vfx,
    get_skill_examples,
)


def register_skill_status_vfx_catalog_routes(router):
    """Register read-only catalog endpoints. Public (no auth)."""

    @router.get("/skill-status-vfx/catalogs/summary")
    async def ssv_summary():
        """Lightweight metrics summary across the 5 catalogs.

        Read-only. No DB. No battle attach.
        """
        try:
            return get_summary()
        except FileNotFoundError as e:
            raise HTTPException(500, str(e)) from e

    @router.get("/skill-status-vfx/catalogs/skill-progression")
    async def ssv_skill_progression():
        try:
            return {
                "version": "RM1.25-C",
                "name": "skill_slot_progression_v1",
                "battle_runtime_attached": False,
                "data": get_skill_progression(),
            }
        except FileNotFoundError as e:
            raise HTTPException(500, str(e)) from e

    @router.get("/skill-status-vfx/catalogs/status-effects")
    async def ssv_status_effects():
        try:
            return {
                "version": "RM1.25-C",
                "name": "status_effect_catalog_v1",
                "battle_runtime_attached": False,
                "data": get_status_effects(),
            }
        except FileNotFoundError as e:
            raise HTTPException(500, str(e)) from e

    @router.get("/skill-status-vfx/catalogs/status-icons")
    async def ssv_status_icons():
        try:
            return {
                "version": "RM1.25-C",
                "name": "status_icon_registry_v1",
                "ui_runtime_attached": False,
                "data": get_status_icons(),
            }
        except FileNotFoundError as e:
            raise HTTPException(500, str(e)) from e

    @router.get("/skill-status-vfx/catalogs/vfx")
    async def ssv_vfx():
        try:
            return {
                "version": "RM1.25-C",
                "name": "vfx_modular_catalog_v1",
                "vfx_runtime_attached": False,
                "data": get_vfx(),
            }
        except FileNotFoundError as e:
            raise HTTPException(500, str(e)) from e

    @router.get("/skill-status-vfx/catalogs/skill-examples")
    async def ssv_skill_examples():
        try:
            return {
                "version": "RM1.25-C",
                "name": "skill_schema_examples_v1",
                "battle_runtime_attached": False,
                "data": get_skill_examples(),
            }
        except FileNotFoundError as e:
            raise HTTPException(500, str(e)) from e
