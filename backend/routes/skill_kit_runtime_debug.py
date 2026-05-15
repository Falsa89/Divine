"""
RM1.33-C — Debug-only Read-Through Endpoint for the Runtime Adapter
──────────────────────────────────────────────────────────────────────
GET-only debug endpoint that previews what the Skill Kit Runtime
Adapter (RM1.33-A) and Cap Policy Adapter would read for a given
(hero_id, slot, context). The endpoint is strictly:

  - GET only (no POST/PUT/PATCH/DELETE).
  - Read-only (no DB / no catalog / no runtime mutation).
  - Feature flag SKILL_KIT_RUNTIME_ENABLED must stay OFF; the runtime
    candidate field will always be disabled here.
  - Borea (greek_borea) is exposed only as catalog-only preview with
    `no_activation=true`; legacy aliases (borea / primordial_gaia /
    greek_boreas / olympian_borea) return 404 — NO fallback.
  - 5★ ultimate requests safely 404 (invalid_slot_for_5star).

Endpoint:
  GET /api/hero-skill-kits/runtime/debug/preview
  query: hero_id (required), slot (required), context (optional, default 'pve')
"""
from __future__ import annotations
from typing import Optional

from fastapi import HTTPException, Query

from data.skill_kit_runtime_adapter import (
    is_skill_kit_runtime_enabled,
    load_skill_kit_for_hero,
    normalize_skill_slot,
    get_skill_runtime_candidate,
)
from data.skill_kit_cap_policy_adapter import (
    preview_cap_policy_for_skill,
)

_VALID_CONTEXTS = ('pvp', 'boss', 'pve')
_FORBIDDEN_ALIASES = ('borea', 'primordial_gaia', 'greek_boreas', 'olympian_borea')


def _safety_envelope() -> dict:
    return {
        'debug_only': True,
        'read_only': True,
        'method': 'GET',
        'runtime_enabled': bool(is_skill_kit_runtime_enabled()),
        'feature_flag_name': 'SKILL_KIT_RUNTIME_ENABLED',
        'applied_to_combat': False,
        'runtime_attached': False,
        'battle_runtime_attached': False,
        'db_write': False,
        'catalog_write': False,
        'roster_write': False,
        'gacha_write': False,
        'ui_runtime_control': False,
        'warning': 'Preview only. Not used by battle runtime.',
    }


def register_skill_kit_runtime_debug_routes(router):
    """Register the single GET debug route. Public (no auth, no mutation)."""

    @router.get('/hero-skill-kits/runtime/debug/preview')
    async def hsk_runtime_debug_preview(
        hero_id: Optional[str] = Query(default=None, description='Hero ID, required.'),
        slot: Optional[str] = Query(default=None, description='Slot name, required.'),
        context: str = Query(default='pve', description='pvp | boss | pve'),
    ):
        # 1) Validate params (HTTP 400 on missing / invalid context)
        if not hero_id or not isinstance(hero_id, str) or not hero_id.strip():
            raise HTTPException(status_code=400, detail={
                'error': 'missing_param',
                'param': 'hero_id',
                'safety_envelope': _safety_envelope(),
            })
        if not slot or not isinstance(slot, str) or not slot.strip():
            raise HTTPException(status_code=400, detail={
                'error': 'missing_param',
                'param': 'slot',
                'safety_envelope': _safety_envelope(),
            })
        if context not in _VALID_CONTEXTS:
            raise HTTPException(status_code=400, detail={
                'error': 'invalid_context',
                'allowed_contexts': list(_VALID_CONTEXTS),
                'received': context,
                'safety_envelope': _safety_envelope(),
            })

        # 2) Forbidden aliases — explicit 404, NO fallback.
        if hero_id in _FORBIDDEN_ALIASES:
            raise HTTPException(status_code=404, detail={
                'error': 'forbidden_legacy_hero_id',
                'hero_id': hero_id,
                'allowed': 'use canonical hero_id (e.g. greek_borea exists only as catalog-only design data)',
                'fallback_disabled': True,
                'safety_envelope': _safety_envelope(),
            })

        # 3) Catalog load — if not found, 404.
        kit = load_skill_kit_for_hero(hero_id)
        if isinstance(kit, dict) and kit.get('is_disabled_runtime_result') is True:
            raise HTTPException(status_code=404, detail={
                'error': 'hero_not_in_catalog',
                'hero_id': hero_id,
                'reason': kit.get('reason'),
                'safety_envelope': _safety_envelope(),
            })

        rarity = kit.get('rarity')  # '5star' | '6star'

        # 4) Normalize slot — safe-reject 5★ ultimate / invalid slot.
        normalized = normalize_skill_slot(hero_id, slot)
        if isinstance(normalized, dict) and normalized.get('is_disabled_runtime_result') is True:
            reason = normalized.get('reason') or 'invalid_slot'
            raise HTTPException(status_code=404, detail={
                'error': 'invalid_slot',
                'hero_id': hero_id,
                'slot': slot,
                'rarity': rarity,
                'reason': reason,
                'fallback_disabled': True,
                'safety_envelope': _safety_envelope(),
            })

        # 5) Cap policy preview + runtime candidate (always disabled).
        cap_preview = preview_cap_policy_for_skill(hero_id, slot, context)
        runtime_candidate = get_skill_runtime_candidate(hero_id, slot)

        # 6) Borea-specific catalog-only preview annotations.
        borea_preview = None
        if hero_id == 'greek_borea':
            entry = kit.get('entry') if isinstance(kit, dict) else None
            release_group = (entry or {}).get('release_group')
            borea_preview = {
                'catalog_only': True,
                'release_group': release_group,
                'not_visible_in_heroes': True,
                'no_activation': True,
                'borea_activation_allowed': False,
                'marchio_boreale_owner_only': True,
            }

        return {
            'hero_id': hero_id,
            'slot': slot,
            'context': context,
            'rarity': rarity,
            'normalized_skill_slot': normalized,
            'cap_policy_preview': cap_preview,
            'runtime_candidate': runtime_candidate,
            'borea_preview': borea_preview,
            'safety_envelope': _safety_envelope(),
        }
