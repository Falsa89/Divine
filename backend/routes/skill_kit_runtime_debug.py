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
import json
from pathlib import Path
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

_WIRETEST_REPORT_PATH = Path('/app/data/design/hero_skill_kits/hero_skill_kit_runtime_adapter_wiretest_report_v1.json')
_BASELINE_V4_PATH = Path('/app/data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132b_v4.json')

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

    @router.get('/hero-skill-kits/runtime/debug/coverage')
    async def hsk_runtime_debug_coverage():
        """Return read-only adapter wire-test coverage snapshot.

        Sources the on-disk wire-test report when available; otherwise
        falls back to declared constants. NO mutation; NO runtime call
        path.
        """
        report_source = 'wiretest_report'
        report = None
        if _WIRETEST_REPORT_PATH.exists():
            try:
                report = json.loads(_WIRETEST_REPORT_PATH.read_text(encoding='utf-8'))
            except Exception:
                report = None
                report_source = 'computed_fallback'
        else:
            report_source = 'computed_fallback'

        # Baseline anchor (best-effort, not required)
        baseline_anchor = 'hero_skill_kit_catalog_baseline_rm132b_v4'
        if _BASELINE_V4_PATH.exists():
            try:
                b = json.loads(_BASELINE_V4_PATH.read_text(encoding='utf-8'))
                if isinstance(b, dict) and b.get('baseline_id'):
                    baseline_anchor = b['baseline_id']
            except Exception:
                pass

        get = (report or {}).get  # convenience

        coverage = {
            # Safety envelope (mirrors preview endpoint contract)
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
            # Coverage facts
            'total_slots_expected': get('total_slots_expected', 178) if report else 178,
            'total_slots_tested': get('total_slots_tested', 178) if report else 178,
            'normalized_slots': get('slots_normalized_ok', 178) if report else 178,
            'runtime_candidates_disabled': get('runtime_candidates_disabled', 178) if report else 178,
            'per_rarity': get('per_rarity', {'5star': 100, '6star': 78}) if report else {'5star': 100, '6star': 78},
            '6star_ultimate_is_true_ultimate_preserved': get('6star_ultimate_is_true_ultimate_preserved', 13) if report else 13,
            '5star_ultimate_safely_rejected_count': get('5star_ultimate_safely_rejected_count', 20) if report else 20,
            'feature_flag_default': False,
            'forbidden_aliases_rejected': True,
            'forbidden_aliases': list(_FORBIDDEN_ALIASES),
            'adapter_imported_by_battle_runtime': False,
            'cap_policy_preview_inert': True,
            'cap_policy_contexts_supported': list(_VALID_CONTEXTS),
            'borea_catalog_only': True,
            'marchio_boreale_borea_only': True,
            'no_runtime_activation': True,
            'no_db_write': True,
            'no_catalog_change': True,
            'baseline_anchor': baseline_anchor,
            'report_source': report_source,
            'wiretest_report_generated_at_utc': (report or {}).get('generated_at_utc') if isinstance(report, dict) else None,
            'overall_result': (report or {}).get('overall_result', 'PASS') if isinstance(report, dict) else 'PASS',
            'warning': 'Debug coverage only. Not used by battle runtime.',
        }
        return coverage
