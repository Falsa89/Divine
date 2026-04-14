"""Divine Waifus - Route Modules"""
from .equipment import register_equipment_routes
from .combat import register_combat_routes
from .guild import register_guild_routes
from .cosmetics import register_cosmetics_routes
from .social import register_social_routes
from .raids import register_raids_routes
from .rankings import register_rankings_routes
from .economy import register_economy_routes
from .gvg import register_gvg_routes
from .artifacts import register_artifacts_routes
from .hero_progression import register_hero_progression_routes
from .unique_items import register_unique_items_routes
from .level_sharing import register_level_sharing_routes
from .forge import register_forge_routes
from .soul_forge import register_soul_forge_routes
from .achievements import register_achievement_routes
from .push_notifications import register_push_routes
from .battle import register_battle_routes
from .heroes import register_heroes_routes

__all__ = [
    'register_equipment_routes',
    'register_combat_routes',
    'register_guild_routes',
    'register_cosmetics_routes',
    'register_social_routes',
    'register_raids_routes',
    'register_rankings_routes',
    'register_economy_routes',
    'register_gvg_routes',
    'register_artifacts_routes',
    'register_hero_progression_routes',
    'register_unique_items_routes',
    'register_level_sharing_routes',
    'register_forge_routes',
    'register_soul_forge_routes',
    'register_achievement_routes',
    'register_push_routes',
]
