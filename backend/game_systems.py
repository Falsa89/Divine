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
    register_reward_claim_routes,
    register_daily_login_claim_routes,
    register_daily_quest_claim_routes,
    register_daily_quest_tracker_routes,
    register_tower_strict_routes,
)
from routes.synergies import register_synergy_routes
from routes.server_time import register_server_time_routes
from routes.player_faction_v2 import register_player_faction_v2_routes
from routes.skill_status_vfx_catalogs import register_skill_status_vfx_catalog_routes
from routes.hero_skill_kits_catalogs import register_hero_skill_kits_catalog_routes
from routes.divine_weapons import register_divine_weapons_catalog_routes
from routes.skill_kit_runtime_debug import register_skill_kit_runtime_debug_routes
from routes.affinity_gifts import register_affinity_gifts_readonly_routes
from routes.affinity_gift_spend import register_affinity_gift_spend_skeleton_routes


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
    # RM1.33-C — Debug-only GET read-through endpoint for the Skill Kit
    # Runtime Adapter preview. Feature flag SKILL_KIT_RUNTIME_ENABLED stays
    # OFF; runtime_candidate is always disabled. NOT used by battle runtime.
    register_skill_kit_runtime_debug_routes(router)
    # AF2-E — Affinity gifts read-only design preview API (3 GET endpoints).
    # Strictly GET-only, no DB, no inventory, no spend, no user state.
    # Borea greek_borea entries remain catalog-only / locked; legacy
    # `borea` / `primordial_gaia` aliases rejected with 404.
    register_affinity_gifts_readonly_routes(router)
    # AF2-G — Disabled POST gift-spend skeleton. Always returns 423; no DB write
    # opens. Feature flag AFFINITY_GIFT_RUNTIME_ENABLED default OFF.
    register_affinity_gift_spend_skeleton_routes(router)
    # Sanctuary (home hero + affinity + constellation) — note: signature differs (no calculate_hero_power)
    register_sanctuary_routes(router, db, get_current_user, serialize_doc)

    # Server time (no auth required; deriva fase dawn/day/sunset/night per la home)
    register_server_time_routes(router)

    # Pack 96 — Controlled reward claim endpoint (live-gated by env kill switch,
    # default OFF). Allowlist + ledger replay-safe + premium grants blocked.
    register_reward_claim_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)

    # Pack 97 — Daily login claim endpoint (first real player-facing source).
    # Live-gated dietro DOPPIO kill switch AND: REWARD_CLAIM_LEDGER_LIVE_ENABLED +
    # DAILY_LOGIN_CLAIM_ENABLED (entrambi default OFF). Server-side deterministic
    # claim_key + unique index per anti-double-grant DB-level.
    register_daily_login_claim_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)

    # Pack 98 — Daily quest completion claim endpoint (second real source).
    # READY_GATED_COMPLETION_REQUIRED: completion proof obbligatorio server-side
    # (test-only via marker `pack_98_test_artifact`). Doppio kill switch AND.
    register_daily_quest_claim_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)

    # Pack 99 — Daily quest runtime tracker (collection `daily_quest_progress`).
    # Endpoint GET /api/daily-quest/progress + POST /api/daily-quest/progress/complete.
    # Kill switch `DAILY_QUEST_TRACKER_ENABLED` default OFF. Completion endpoint
    # test-only finche` non esiste un runtime di gameplay reale (marker
    # `pack_99_test_artifact`). Il claim Pack 98 ora consulta questo tracker.
    register_daily_quest_tracker_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)

    # Pack 101 — Tower strict server-scoped (PSP.tower_progress).
    # Endpoint /api/tower/strict/{health,status,preflight,battle/preview}.
    # Quarantine reward live, no users.* mutation, kill switch
    # `TOWER_STRICT_PREFLIGHT_ENABLED` default OFF. Path legacy tower
    # `/api/tower/battle` e `/api/tower/status` ora 503 di default.
    register_tower_strict_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)

    # Pack 104 — Economy strict server-scoped writes (shop buy / soul forge retire /
    # equipment equip/unequip). Triple kill switch AND di default OFF. Test-only
    # via marker `pack_104_test_artifact`. Server-side catalog/claim_key + ledger
    # idempotency. Solo PSP soft_currencies mutations. No users.* mutation.
    # Forge/Upgrade/Fusion deferred onesto.
    from routes.economy_strict import register_economy_strict_routes
    register_economy_strict_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)

    # Pack 106 — Controlled rewards (mail / achievement / daily-weekly).
    # Quadruple kill switch AND di default OFF. Test-only via marker `pack_106_test_artifact`.
    # Server-side catalog reward + ledger idempotency. PSP soft+materials only.
    # No users.* mutation, no premium/IAP/gacha, no battlepass/event/AFK/PvP/guild live.
    from routes.controlled_rewards import register_controlled_rewards_routes
    register_controlled_rewards_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)

    # Pack 107 — Competitive/Social/Live mode server-scope guards.
    # Audit + honest blocker per Arena/PvP/Guild/Event.
    # READY_GATED_REWARDS_DEFERRED ovunque; reward_live_general resta false.
    from routes.competitive_guards import register_competitive_guards_routes
    register_competitive_guards_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)

    # Pack 108 — Guild Server-Scope Retrofit (read/preview strict) +
    # Frontend Playable Loop Map (Alpha). Tutti i kill switch sono di
    # default OFF. Le route legacy account-wide in `routes/guild.py`
    # sono quarantineate via `GUILD_LEGACY_QUARANTINED=true` (default
    # TRUE). reward_live_general resta false; no users.* mutation.
    from routes.guild_strict import register_guild_strict_routes
    register_guild_strict_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)
    from routes.playable_loop_map import register_playable_loop_map_routes
    register_playable_loop_map_routes(router, db, get_current_user, serialize_doc, calculate_hero_power)

    return router
