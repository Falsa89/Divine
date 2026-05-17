"""
AXIS-E — Canonical Axis Read-Through Helper (INERT)
───────────────────────────────────────────────────────────────────
Thin pure-Python read-through helper that future inert resolvers
(CS2-B, AF2 future inventory resolver, STACK-B) can call to look up
canonical Faction / Element tokens. Always degrades safely and NEVER
mutates source tables.

ABSOLUTE RULES:
  - Pure read-through. Composes AXIS-B helper + AXIS-C dynamic preview.
  - MUST NEVER be imported by battle_engine.py / battle_core.py / combat.tsx.
  - Does NOT patch RM1.34-B matrix, AF2-A gift draft, AXIS-A plan, baseline.
  - `tides` faction returns design_pending; `darkness` element returns dark.
  - Bulk APIs available for resolvers: `resolve_elements_bulk`,
    `resolve_factions_bulk`.
"""
from __future__ import annotations
from typing import Any, Iterable

# Re-use AXIS-B inert primitives (alias map + per-token normalize).
from data import canonical_axis_alias_helper as _b  # type: ignore


def resolve_element(token: Any) -> dict[str, Any]:
    """Read-through resolution for a single element token.

    Wraps AXIS-B `normalize_element_axis`. Returns the per-token result
    augmented with `valid` (true iff resolves to live/aliased-to-live).
    """
    r = _b.normalize_element_axis(token)
    r = dict(r)
    r['valid'] = bool(
        r.get('canonical') and r.get('in_roster')
        and r.get('status') in ('live', 'aliased_to_live')
    )
    return r


def resolve_faction(token: Any) -> dict[str, Any]:
    """Read-through resolution for a single faction token.

    Wraps AXIS-B `normalize_faction_axis`. Returns the per-token result
    augmented with `valid` (true iff live or aliased-to-live; false for
    `design_pending` such as tides).
    """
    r = _b.normalize_faction_axis(token)
    r = dict(r)
    r['valid'] = bool(
        r.get('canonical') and r.get('in_roster')
        and r.get('status') in ('live', 'aliased_to_live')
    )
    return r


def resolve_elements_bulk(tokens: Iterable[Any]) -> dict[str, Any]:
    """Resolve many element tokens at once."""
    items = [resolve_element(t) for t in tokens]
    return {
        'enabled': False,
        'runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'preview_only': True,
        'count_input': len(items),
        'count_valid': sum(1 for i in items if i.get('valid')),
        'count_unknown': sum(1 for i in items if i.get('status') == 'unknown'),
        'count_design_pending': 0,
        'items': items,
    }


def resolve_factions_bulk(tokens: Iterable[Any]) -> dict[str, Any]:
    """Resolve many faction tokens at once. Reports `design_pending` for tides."""
    items = [resolve_faction(t) for t in tokens]
    return {
        'enabled': False,
        'runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'preview_only': True,
        'count_input': len(items),
        'count_valid': sum(1 for i in items if i.get('valid')),
        'count_design_pending': sum(
            1 for i in items if i.get('status') == 'design_pending'
        ),
        'count_unknown': sum(1 for i in items if i.get('status') == 'unknown'),
        'items': items,
    }


def axis_health() -> dict[str, Any]:
    """Composite health check meant to be called by future inert resolvers.

    Returns a strict inert envelope with the per-axis pass/fail flags.
    Tides reported as design_pending (NOT valid).
    """
    # Element sanity
    darkness = resolve_element('darkness')
    dark = resolve_element('dark')
    fire = resolve_element('fire')
    # Faction sanity
    greek = resolve_faction('greek')
    tides = resolve_faction('tides')
    return {
        'enabled': False,
        'runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'preview_only': True,
        'darkness_resolves_to_dark': darkness.get('canonical') == 'dark',
        'dark_resolves_to_dark': dark.get('canonical') == 'dark',
        'fire_resolves_to_fire': fire.get('canonical') == 'fire',
        'greek_resolves_to_greek': greek.get('canonical') == 'greek',
        'tides_is_design_pending': tides.get('status') == 'design_pending',
        'mutates_source_tables': False,
    }


ADAPTER_MANIFEST: dict[str, Any] = {
    'adapter_id': 'canonical_axis_read_through_helper_axis_e',
    'task_origin': 'AXIS-E',
    'pure_functions': [
        'resolve_element', 'resolve_faction',
        'resolve_elements_bulk', 'resolve_factions_bulk',
        'axis_health',
    ],
    'composes_axis_b': True,
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
}
