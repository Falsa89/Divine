"""Pre-QA Stabilization 117B — Hero Upgrade Readiness helper (read-only).

Questo modulo NON scrive nulla nel DB. NON consuma materiali. NON applica upgrade.
Classifica per-hero le categorie di upgrade possibili, ma in Pack 117B rimane
CONSERVATIVO: nessun `can_upgrade_now=true` viene mai dichiarato perché le
fonti economia/materiali/inventory non sono server-scoped runtime-safe (vedi
blocker `ECONOMY_SOURCE_NOT_SAFE_FOR_READINESS` documentato in readiness map
117A).

Formula contract:
  SOURCE_VERSION = 'hero_upgrade_readiness_v1_preqa_read_only'

Nessun toggle attiva mutation. Nessuna chiamata ad endpoint upgrade/claim.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

HERO_UPGRADE_READINESS_SOURCE_VERSION = 'hero_upgrade_readiness_v1_preqa_read_only'

# Categorie canonical di upgrade. Tutte deferred in 117B.
CANONICAL_UPGRADE_CATEGORIES: tuple = (
    'level_exp',
    'star_up',
    'ascension',
    'skill_upgrade',
    'quality_frame_elevation',
    'constellations',
    'reincarnation',
    'gear_level',
    'gear_quality_fusion',
    'gem_socket',
    'rune_equip',
    'artifact_global',
    'divine_weapon',
)

# Mappa categoria → ragione di blocco (motivazione conservativa).
CATEGORY_BLOCKED_REASONS: Dict[str, str] = {
    'level_exp': 'EXP_SOURCE_NOT_SAFE_FOR_READINESS',
    'star_up': 'ECONOMY_SOURCE_NOT_SAFE_FOR_READINESS',
    'ascension': 'ECONOMY_SOURCE_NOT_SAFE_FOR_READINESS',
    'skill_upgrade': 'SKILL_UPGRADE_RESOLVER_NOT_RUNTIME_SAFE_YET',
    'quality_frame_elevation': 'QUALITY_FRAME_SOURCE_NOT_RUNTIME_SAFE_YET',
    'constellations': 'CONSTELLATIONS_CANONICAL_ENDPOINT_REQUIRED',
    'reincarnation': 'ECONOMY_SOURCE_NOT_SAFE_FOR_READINESS',
    'gear_level': 'GEAR_INVENTORY_CONTRACT_REQUIRED',
    'gear_quality_fusion': 'GEAR_INVENTORY_CONTRACT_REQUIRED',
    'gem_socket': 'GEAR_INVENTORY_CONTRACT_REQUIRED',
    'rune_equip': 'RUNE_INVENTORY_CONTRACT_REQUIRED',
    'artifact_global': 'ARTIFACT_GLOBAL_CANONICAL_ENDPOINT_REQUIRED',
    'divine_weapon': 'DIVINE_WEAPON_RESOLVER_NOT_RUNTIME_SAFE_YET',
}


def build_metadata() -> Dict[str, Any]:
    return {
        'status': 'ok',
        'source_version': HERO_UPGRADE_READINESS_SOURCE_VERSION,
        'safe_read_only': True,
        'no_db_writes': True,
        'no_upgrade_activation': True,
        'no_material_consume': True,
        'no_claim_activation': True,
        'no_reward_activation': True,
        'server_scoped': True,
        'all_categories_deferred_in_117b': True,
        'canonical_upgrade_categories': list(CANONICAL_UPGRADE_CATEGORIES),
        'global_blocker': 'ECONOMY_SOURCE_NOT_SAFE_FOR_READINESS',
    }


def build_per_hero_readiness(user_hero: Dict[str, Any]) -> Dict[str, Any]:
    """Costruisce envelope read-only per un user_hero document.

    Conservativo: `can_upgrade_now=false` sempre, `red_dot_candidate=false`
    sempre. Le categorie sono enumerate con `blocked_reasons`.
    """
    uh = user_hero or {}
    user_hero_id = uh.get('id') or uh.get('_id')
    hero_id = uh.get('hero_id')
    upgrade_categories: List[Dict[str, Any]] = []
    for cat in CANONICAL_UPGRADE_CATEGORIES:
        upgrade_categories.append({
            'category': cat,
            'can_upgrade_now': False,
            'safe_read_only': True,
            'confidence': 'low_until_resolver',
            'requires_future_resolver': True,
            'blocked_reason': CATEGORY_BLOCKED_REASONS.get(
                cat, 'ECONOMY_SOURCE_NOT_SAFE_FOR_READINESS'),
        })
    blocked_reasons = sorted({c['blocked_reason'] for c in upgrade_categories})
    return {
        'user_hero_id': str(user_hero_id) if user_hero_id is not None else None,
        'hero_id': hero_id,
        'can_upgrade_now': False,
        'safe_read_only': True,
        'confidence': 'low_until_resolver',
        'upgrade_categories': upgrade_categories,
        'blocked_reasons': blocked_reasons,
        'requires_future_resolver': True,
        'red_dot_candidate': False,
        'source_version': HERO_UPGRADE_READINESS_SOURCE_VERSION,
    }


def build_envelope_no_psp(server_id: str) -> Dict[str, Any]:
    """Envelope per uid+sid senza PSP. Read-only."""
    return {
        'status': 'blocked_no_psp_for_server',
        'server_id': server_id,
        'source_version': HERO_UPGRADE_READINESS_SOURCE_VERSION,
        'safe_read_only': True,
        'no_db_writes': True,
        'no_upgrade_activation': True,
        'no_material_consume': True,
        'no_claim_activation': True,
        'global_blocker': 'PLAYER_SERVER_PROFILE_REQUIRED',
        'heroes': [],
        'heroes_count': 0,
        'any_red_dot_candidate': False,
    }
