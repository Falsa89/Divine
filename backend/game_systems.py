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
    # Sanctuary (home hero + affinity + constellation) — note: signature differs (no calculate_hero_power)
    register_sanctuary_routes(router, db, get_current_user, serialize_doc)

    return router
