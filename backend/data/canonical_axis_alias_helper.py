"""
AXIS-B — Canonical Faction x Element Alias Helper (INERT, read-through)
─────────────────────────────────────────────────────────────────────
Inert helper that exposes the alias_map documented in
`canonical_faction_element_axis_resolution_plan_v1.json` (AXIS-A) to
future inert resolvers (CS2-B, AF2 future inventory resolver, STACK-B,
etc.).

ABSOLUTE RULES:
  - This module MUST NEVER be imported by `battle_engine.py`,
    `battle_core.py`, or `combat.tsx`.
  - The helper does NOT mutate any source table (RM1.34-B matrix,
    AF2-A gift draft, character bible, baseline).
  - `tides` is reported as design_pending / not_live until live roster
    confirms.
  - No DB. No API. No UI. Pure read-only normalization helpers.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

_PLAN_PATH = Path(
    '/app/data/design/shared/canonical_faction_element_axis_resolution_plan_v1.json'
)

# Static fallback aliases mirror the AXIS-A plan. The plan file is the
# source of truth at load time; if absent we degrade gracefully.
_FALLBACK_ELEMENT_ALIAS = {
    'darkness': 'dark',
    'dark': 'dark',
    'oscurita': 'dark',
    'shadow': 'dark',
}
_FALLBACK_FACTION_ALIAS = {
    'yokai': 'japanese_yokai',
    'creatures': 'creature_beast',
    'beasts': 'creature_beast',
    'celtics': 'celtic',
}

# Canonical live-roster tokens (mirror AXIS-A plan recommendation).
_LIVE_ROSTER_FACTIONS = {
    'angelic', 'arcane', 'celtic', 'creature_beast', 'cursed',
    'demonic', 'egyptian', 'greek', 'japanese_yokai',
    'mesopotamian', 'norse', 'primordial',
}
_LIVE_ROSTER_ELEMENTS = {
    'dark', 'earth', 'fire', 'light', 'lightning', 'water', 'wind',
}

# Factions present in RM1.34-B but absent from roster (design_pending)
_DESIGN_PENDING_FACTIONS = {'tides'}


def _load_plan() -> dict[str, Any]:
    try:
        return json.loads(_PLAN_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {}


def get_axis_alias_map() -> dict[str, dict[str, str]]:
    """Return the alias map. Loads from AXIS-A plan if available,
    otherwise returns the static fallback.

    Returns:
      {'elements': {...}, 'factions': {...}}
    """
    plan = _load_plan()
    am = plan.get('alias_map') or {}
    elements = dict(am.get('elements') or _FALLBACK_ELEMENT_ALIAS)
    factions = dict(am.get('factions') or _FALLBACK_FACTION_ALIAS)
    # Defensive: always ensure 'darkness'->'dark' and 'dark'->'dark' present
    elements.setdefault('darkness', 'dark')
    elements.setdefault('dark', 'dark')
    return {'elements': elements, 'factions': factions}


def normalize_element_axis(value: Any) -> dict[str, Any]:
    """Normalize an element token to the canonical live-roster spelling.

    Returns a dict describing the resolution:
      {
        'input': <original>,
        'canonical': <normalized or None>,
        'in_roster': bool,
        'design_pending': bool,
        'status': 'live' | 'aliased_to_live' | 'unknown',
      }
    Never raises. Never mutates anything.
    """
    out: dict[str, Any] = {
        'input': value,
        'canonical': None,
        'in_roster': False,
        'design_pending': False,
        'status': 'unknown',
    }
    if not isinstance(value, str) or not value:
        return out
    key = value.strip().lower()
    if key in _LIVE_ROSTER_ELEMENTS:
        out.update({'canonical': key, 'in_roster': True, 'status': 'live'})
        return out
    alias_map = get_axis_alias_map().get('elements') or {}
    target = alias_map.get(key)
    if target and target in _LIVE_ROSTER_ELEMENTS:
        out.update({
            'canonical': target,
            'in_roster': True,
            'status': 'aliased_to_live',
        })
        return out
    return out


def normalize_faction_axis(value: Any) -> dict[str, Any]:
    """Normalize a faction token. Handles design_pending tokens such as `tides`.

    Returns a dict:
      {
        'input': <original>,
        'canonical': <normalized or None>,
        'in_roster': bool,
        'design_pending': bool,
        'status': 'live' | 'aliased_to_live' | 'design_pending' | 'unknown',
      }
    """
    out: dict[str, Any] = {
        'input': value,
        'canonical': None,
        'in_roster': False,
        'design_pending': False,
        'status': 'unknown',
    }
    if not isinstance(value, str) or not value:
        return out
    key = value.strip().lower()
    if key in _LIVE_ROSTER_FACTIONS:
        out.update({'canonical': key, 'in_roster': True, 'status': 'live'})
        return out
    if key in _DESIGN_PENDING_FACTIONS:
        out.update({
            'canonical': None,
            'in_roster': False,
            'design_pending': True,
            'status': 'design_pending',
        })
        return out
    alias_map = get_axis_alias_map().get('factions') or {}
    target = alias_map.get(key)
    if target and target in _LIVE_ROSTER_FACTIONS:
        out.update({
            'canonical': target,
            'in_roster': True,
            'status': 'aliased_to_live',
        })
        return out
    return out


def validate_axis_value(value: Any, axis_type: str) -> dict[str, Any]:
    """Convenience entry point. axis_type in {'element', 'faction'}.

    Returns the corresponding normalize_*_axis() result plus a top-level
    `valid` bool that is True only if the value resolves to a live or
    aliased-to-live canonical token.
    """
    axis_type = (axis_type or '').strip().lower()
    if axis_type == 'element':
        r = normalize_element_axis(value)
    elif axis_type == 'faction':
        r = normalize_faction_axis(value)
    else:
        r = {'input': value, 'canonical': None, 'in_roster': False,
             'design_pending': False, 'status': 'unknown_axis_type'}
    r['valid'] = bool(
        r.get('canonical') and r.get('in_roster')
        and r.get('status') in ('live', 'aliased_to_live')
    )
    return r


def preview_axis_alignment() -> dict[str, Any]:
    """Return an inert summary of how the helper sees the world.

    Echoes the live-roster canonical tokens, the alias map, and the
    design_pending factions. Suitable for documentation / audit only.
    """
    am = get_axis_alias_map()
    return {
        'enabled': False,
        'runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'preview_only': True,
        'design_only': True,
        'live_roster_elements_canonical': sorted(_LIVE_ROSTER_ELEMENTS),
        'live_roster_factions_canonical': sorted(_LIVE_ROSTER_FACTIONS),
        'design_pending_factions': sorted(_DESIGN_PENDING_FACTIONS),
        'alias_map': am,
        'plan_loaded': bool(_load_plan()),
        'plan_path': str(_PLAN_PATH),
        'mutates_source_tables': False,
        'patches_rm134b': False,
        'patches_af2a': False,
    }


# Adapter manifest
ADAPTER_MANIFEST: dict[str, Any] = {
    'adapter_id': 'canonical_axis_alias_helper_axis_b',
    'task_origin': 'AXIS-B',
    'pure_functions': [
        'get_axis_alias_map',
        'normalize_element_axis',
        'normalize_faction_axis',
        'validate_axis_value',
        'preview_axis_alignment',
    ],
    'writes_to_db': False,
    'writes_to_catalogs': False,
    'writes_to_runtime': False,
    'imported_by_battle_engine': False,
    'imported_by_battle_core': False,
    'imported_by_combat_tsx': False,
    'applied_to_combat': False,
    'no_borea_activation': True,
    'mutates_source_tables': False,
    'patches_rm134b': False,
    'patches_af2a': False,
    'live_roster_elements_canonical': sorted(_LIVE_ROSTER_ELEMENTS),
    'live_roster_factions_canonical': sorted(_LIVE_ROSTER_FACTIONS),
    'design_pending_factions': sorted(_DESIGN_PENDING_FACTIONS),
}
