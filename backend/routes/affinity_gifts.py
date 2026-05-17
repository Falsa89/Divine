"""
AF2-E — Affinity Gifts Read-Only Endpoint
─────────────────────────────────────────────────────────────────────
Strictly GET-only / read-only / inert API surface that exposes the
AF2-A `affinity_gift_catalog_faction_element_draft_v1.json` design
catalog as a preview.

ABSOLUTE RULES:
  - GET methods only. No POST/PUT/PATCH/DELETE.
  - No DB writes. No inventory mutation. No spend / claim / give.
  - No user state. No auth required (public read-only).
  - No live runtime. `runtime_attached=false` on every payload.
  - Borea: greek_borea records are preserved with `borea_locked=true`;
    legacy `borea` / `primordial_gaia` rejected with 404.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException


_CATALOG_PATH = Path(
    '/app/data/design/affinity/affinity_gift_catalog_faction_element_draft_v1.json'
)
_ECONOMY_PATH = Path(
    '/app/data/design/affinity/affinity_phase2_economy_cap_policy_draft_v1.json'
)

_FORBIDDEN_ALIASES = frozenset({'borea', 'primordial_gaia', 'greek_borea'})

# AXIS-F — canonical element axis & alias map (mirrors the alias helper)
_CANONICAL_ELEMENTS = frozenset({'fire', 'water', 'earth', 'wind',
                                 'lightning', 'light', 'dark'})
_ELEMENT_ALIASES: dict[str, str] = {
    'darkness': 'dark',  # legacy alias preserved post RM1.34-B-PATCH-A
}
# Factions deferred from the canonical matrix (RM1.34-B-PATCH-B).
# These respond 404 with `deferred_not_live` instead of `forbidden`.
_DEFERRED_FACTIONS = frozenset({'tides'})


def _safety_envelope() -> dict[str, Any]:
    return {
        'read_only': True,
        'design_only': True,
        'runtime_attached': False,
        'battle_runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'inventory_enabled': False,
        'gift_spend_enabled': False,
        'gift_claim_enabled': False,
        'affinity_points_write_enabled': False,
        'stat_buffs_enabled': False,
        'borea_activation': False,
        'feature_flag_dependency': 'AFFINITY_GIFT_RUNTIME_ENABLED',
        'feature_flag_currently_enabled': False,
        'hidden_aliases_blocked': sorted(_FORBIDDEN_ALIASES),
    }


def _load_catalog() -> dict[str, Any]:
    if not _CATALOG_PATH.exists():
        raise HTTPException(500, 'affinity gift catalog draft file not present')
    try:
        return json.loads(_CATALOG_PATH.read_text(encoding='utf-8'))
    except Exception as e:
        raise HTTPException(500, f'affinity gift catalog draft parse error: {e!r}')


def _load_economy() -> dict[str, Any] | None:
    if not _ECONOMY_PATH.exists():
        return None
    try:
        return json.loads(_ECONOMY_PATH.read_text(encoding='utf-8'))
    except Exception:
        return None


def register_affinity_gifts_readonly_routes(router):
    """Register 3 GET-only endpoints under the existing /api router prefix.

    All endpoints are public (no auth) because they expose only design
    catalog data (no user state). Each response includes a uniform
    `safety_envelope`.
    """

    @router.get("/affinity/gifts")
    async def affinity_gifts_full():
        """Return the full design-only gift catalog preview.

        Strictly read-only. Includes safety_envelope + entries.
        """
        cat = _load_catalog()
        entries = cat.get('entries') or []
        return {
            'task_origin': 'AF2-E',
            'catalog_id': cat.get('catalog_id'),
            'baseline_anchor': cat.get('baseline_anchor'),
            'design_only': True,
            'runtime_attached': False,
            'db_write': False,
            'factions_count': cat.get('factions_count'),
            'elements_count': cat.get('elements_count'),
            'expected_universal_entries': cat.get('expected_universal_entries'),
            'expected_faction_element_entries': cat.get('expected_faction_element_entries'),
            'total_entries': cat.get('total_entries'),
            'factions_used': cat.get('factions_used') or [],
            'elements_used': cat.get('elements_used') or [],
            'constraints': cat.get('constraints') or {},
            'entries': entries,
            'safety_envelope': _safety_envelope(),
        }

    @router.get("/affinity/gifts/summary")
    async def affinity_gifts_summary():
        """Lightweight metrics + safety envelope. No entries."""
        cat = _load_catalog()
        economy = _load_economy() or {}
        return {
            'task_origin': 'AF2-E',
            'catalog_id': cat.get('catalog_id'),
            'baseline_anchor': cat.get('baseline_anchor'),
            'design_only': True,
            'runtime_attached': False,
            'factions_count': cat.get('factions_count'),
            'elements_count': cat.get('elements_count'),
            'total_entries': cat.get('total_entries'),
            'economy_policy_id': economy.get('policy_id'),
            'economy_pvp_cap_per_source_pct': (
                (economy.get('cap_policy') or {}).get('pvp_cap_per_source_pct')
            ),
            'economy_pvp_cap_total_pct': (
                (economy.get('cap_policy') or {}).get('pvp_cap_total_pct')
            ),
            'safety_envelope': _safety_envelope(),
        }

    @router.get("/affinity/gifts/by-faction/{faction_id}")
    async def affinity_gifts_by_faction(faction_id: str):
        """Return gift catalog entries filtered by faction. Read-only."""
        fid = (faction_id or '').strip().lower()
        if not fid:
            raise HTTPException(400, 'faction_id required')
        if fid in _FORBIDDEN_ALIASES:
            # Borea legacy aliases are explicitly rejected
            raise HTTPException(404, 'forbidden alias')
        if fid in _DEFERRED_FACTIONS:
            # AXIS-F — tides deferred from canonical matrix (RM1.34-B-PATCH-B)
            raise HTTPException(
                404,
                f'faction "{fid}" deferred_not_live (RM1.34-B-PATCH-B); '
                'restore_condition: Character Bible / live roster confirms '
                'canonical faction'
            )
        cat = _load_catalog()
        if fid not in (cat.get('factions_used') or []):
            raise HTTPException(404, f'faction "{fid}" not in catalog draft')
        entries = [
            e for e in (cat.get('entries') or [])
            if isinstance(e, dict) and e.get('faction_token') == fid
        ]
        return {
            'task_origin': 'AXIS-F',
            'faction_id': fid,
            'design_only': True,
            'runtime_attached': False,
            'count': len(entries),
            'entries': entries,
            'safety_envelope': _safety_envelope(),
        }

    @router.get("/affinity/gifts/by-element/{element_id}")
    async def affinity_gifts_by_element(element_id: str):
        """AXIS-F — Return gift catalog entries filtered by canonical
        element. Read-only.

        Supports the `darkness -> dark` alias (post RM1.34-B-PATCH-A).
        Returns 404 with `axis_type_mismatch` if the token is actually
        a faction (e.g. `tides`) instead of an element.
        """
        eid = (element_id or '').strip().lower()
        if not eid:
            raise HTTPException(400, 'element_id required')
        if eid in _FORBIDDEN_ALIASES:
            raise HTTPException(404, 'forbidden alias')

        alias_applied = False
        canonical = eid
        if eid in _ELEMENT_ALIASES:
            canonical = _ELEMENT_ALIASES[eid]
            alias_applied = True

        # axis_type_mismatch: token is a faction, not an element
        if canonical in _DEFERRED_FACTIONS \
                or canonical in ('greek', 'norse', 'egyptian',
                                 'japanese_yokai', 'celtic', 'angelic',
                                 'demonic', 'cursed', 'creature_beast',
                                 'primordial', 'arcane', 'mesopotamian',
                                 'tides'):
            raise HTTPException(
                404,
                f'element "{eid}" axis_type_mismatch: token is a faction, '
                'not a canonical element'
            )

        if canonical not in _CANONICAL_ELEMENTS:
            raise HTTPException(
                404,
                f'element "{eid}" not in canonical element set '
                f'{sorted(_CANONICAL_ELEMENTS)}'
            )

        cat = _load_catalog()
        if canonical not in (cat.get('elements_used') or []):
            raise HTTPException(
                404,
                f'element "{canonical}" not in catalog draft elements_used'
            )

        entries = [
            e for e in (cat.get('entries') or [])
            if isinstance(e, dict) and e.get('element_token') == canonical
        ]
        return {
            'task_origin': 'AXIS-F',
            'element_id': eid,
            'canonical': canonical,
            'alias_applied': alias_applied,
            'design_only': True,
            'runtime_attached': False,
            'count': len(entries),
            'entries': entries,
            'safety_envelope': _safety_envelope(),
        }
