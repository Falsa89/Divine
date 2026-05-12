"""
Divine Waifus - Game Systems Orchestrator
Routes are split into modular files under /routes/
"""
from fastapi import APIRouter

from routes import (
    register_equipment_routes,
    register_combat_routes,
    register_guild_routes,
    register_cosmetics_routes,
    register_social_routes,
    register_raids_routes,
    register_rankings_routes,
    register_economy_routes,
    register_gvg_routes,
    register_artifacts_routes,
    register_hero_progression_routes,
    register_unique_items_routes,
    register_level_sharing_routes,
    register_forge_routes,
    register_soul_forge_routes,
    register_achievement_routes,
    register_push_routes,
    register_sanctuary_routes,
)
from routes.synergies import register_synergy_routes
from routes.server_time import register_server_time_routes
from routes.player_faction_v2 import register_player_faction_v2_routes
from routes.skill_status_vfx_catalogs import register_skill_status_vfx_catalog_routes
from routes.hero_skill_kits_catalogs import register_hero_skill_kits_catalog_routes
from routes.divine_weapons import register_divine_weapons_catalog_routes


def create_game_routes(db, get_current_user, serialize_doc, calculate_hero_power):
    router = APIRouter(prefix="/api")

    register_equipment_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_combat_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_guild_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_cosmetics_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_social_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_raids_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_rankings_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_economy_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_gvg_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_artifacts_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_hero_progression_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_unique_items_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_level_sharing_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_forge_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_soul_forge_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_achievement_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_push_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    register_synergy_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    # RM1.24-A — Player Faction V2 (foundation, separate from V1 users.faction)
    register_player_faction_v2_routes(router, db, get_current_user)
    # RM1.25-C — Skill/Status/Icon/VFX read-only catalog browsing API.
    # NOT connected to battle runtime; pure design catalog exposure.
    register_skill_status_vfx_catalog_routes(router)
    # RM1.26-C — Hero Skill Kit read-only catalog API (5★/6★ inert).
    # NOT connected to battle/HP-bar/VFX runtime. Borea entry exposed
    # in design catalog ONLY (no roster activation).
    register_hero_skill_kits_catalog_routes(router)
    # RM1.27-B — Divine Weapon read-only catalog API (13 records inert).
    # NOT connected to battle/HP-bar/VFX/status/gacha/roster runtime.
    # Borea entry exposed as catalog-only design data; legacy `borea`
    # alias is explicitly rejected with 404.
    register_divine_weapons_catalog_routes(router)
    # Sanctuary (home hero + affinity + constellation) — note: signature differs (no calculate_hero_power)
    register_sanctuary_routes(router, db, get_current_user, serialize_doc)

    # Server time (no auth required; deriva fase dawn/day/sunset/night per la home)
    register_server_time_routes(router)

    return router
