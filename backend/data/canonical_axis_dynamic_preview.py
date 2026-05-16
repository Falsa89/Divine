"""
AXIS-C — Canonical Faction x Element Dynamic Preview Helper (INERT)
─────────────────────────────────────────────────────────────────────
Inert helper that DYNAMICALLY computes the live roster faction/element
sets by reading either (a) the local FastAPI service `/api/heroes`, or
(b) a fallback static source file. Then it compares the live sets to
RM1.34-B matrix and AF2-A gift draft, returns a drift report, and
validates alias coverage against the AXIS-A plan.

ABSOLUTE RULES:
  - This module MUST NEVER be imported by `battle_engine.py`,
    `battle_core.py`, or `combat.tsx`.
  - The helper does NOT mutate any source table (RM1.34-B, AF2-A,
    AXIS-A plan, character bible, baseline).
  - All output is read-only; `runtime_attached=false` on every payload.
  - Best-effort network: if `/api/heroes` is unreachable, the helper
    degrades gracefully to a static-only mode.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from urllib.request import urlopen
from urllib.error import URLError

# Static fallback path (live roster source mirror)
_HEROES_MASTER = Path('/app/data/design/heroes_master.json')

# Cross-reference design files
_AXIS_PLAN = Path(
    '/app/data/design/shared/'
    'canonical_faction_element_axis_resolution_plan_v1.json'
)
_BOSS_MATRIX = Path(
    '/app/data/design/boss_systems/'
    'boss_family_element_faction_matrix_v1.json'
)
_GIFT_DRAFT = Path(
    '/app/data/design/affinity/'
    'affinity_gift_catalog_faction_element_draft_v1.json'
)

_API_URL = 'http://127.0.0.1:8001/api/heroes'

_FORBIDDEN_ALIASES = frozenset({'borea', 'primordial_gaia'})


def _safe_read_json(p: Path) -> dict[str, Any] | list | None:
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return None


def _fetch_live_heroes() -> tuple[list[dict[str, Any]], str]:
    """Try /api/heroes, then heroes_master.json. Return (heroes, source_tag)."""
    try:
        with urlopen(_API_URL, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            heroes = data if isinstance(data, list) else (
                data.get('heroes') or data.get('data') or []
            )
            return heroes, 'api'
    except (URLError, Exception):
        pass
    static = _safe_read_json(_HEROES_MASTER)
    if isinstance(static, list):
        return static, 'static_heroes_master'
    if isinstance(static, dict):
        heroes = static.get('heroes') or static.get('data') or []
        if isinstance(heroes, list):
            return heroes, 'static_heroes_master'
    return [], 'unavailable'


def preview_live_axis_sets() -> dict[str, Any]:
    """Return the live faction/element sets observed today.

    Filters legacy aliases (`borea`, `primordial_gaia`). Includes the
    source tag (api / static_heroes_master / unavailable).
    """
    heroes, source = _fetch_live_heroes()
    factions: set[str] = set()
    elements: set[str] = set()
    skipped = 0
    for h in heroes:
        if not isinstance(h, dict):
            continue
        hid = (h.get('id') or h.get('canonical_id') or '').strip().lower()
        if hid in _FORBIDDEN_ALIASES:
            skipped += 1
            continue
        f = (h.get('faction') or h.get('canonical_faction') or '').strip().lower()
        el = (h.get('element') or h.get('canonical_element') or '').strip().lower()
        if f:
            factions.add(f)
        if el:
            elements.add(el)
    return {
        'enabled': False,
        'runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'preview_only': True,
        'source': source,
        'roster_count': len(heroes),
        'skipped_forbidden_aliases': skipped,
        'live_factions_sorted': sorted(factions),
        'live_elements_sorted': sorted(elements),
        'live_factions_count': len(factions),
        'live_elements_count': len(elements),
    }


def preview_axis_drift_report() -> dict[str, Any]:
    """Compare live axes to RM1.34-B matrix, AF2-A gift draft, and the
    AXIS-A plan. Return a drift report (read-only, no mutation).
    """
    live = preview_live_axis_sets()
    live_factions = set(live.get('live_factions_sorted') or [])
    live_elements = set(live.get('live_elements_sorted') or [])

    # Boss matrix
    bm = _safe_read_json(_BOSS_MATRIX) or {}
    matrix_factions = set(bm.get('faction_groups_included') or [])
    matrix_elements = set(bm.get('elements_included') or [])

    # Gift draft
    gd = _safe_read_json(_GIFT_DRAFT) or {}
    gift_factions = set(gd.get('factions_used') or [])
    gift_elements = set(gd.get('elements_used') or [])

    # Axis plan
    ap = _safe_read_json(_AXIS_PLAN) or {}
    alias_map_elements = ((ap.get('alias_map') or {}).get('elements') or {})
    alias_map_factions = ((ap.get('alias_map') or {}).get('factions') or {})

    factions_in_matrix_not_in_live = sorted(matrix_factions - live_factions)
    elements_in_matrix_not_in_live = sorted(matrix_elements - live_elements)
    factions_in_live_not_in_matrix = sorted(live_factions - matrix_factions)
    elements_in_live_not_in_matrix = sorted(live_elements - matrix_elements)

    tides_status = (
        'design_pending' if 'tides' in matrix_factions and 'tides' not in live_factions
        else ('live' if 'tides' in live_factions else 'absent')
    )

    return {
        'enabled': False,
        'runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'preview_only': True,
        'live': {
            'factions': sorted(live_factions),
            'elements': sorted(live_elements),
            'source': live.get('source'),
        },
        'matrix_rm134b': {
            'factions': sorted(matrix_factions),
            'elements': sorted(matrix_elements),
        },
        'gift_draft_af2a': {
            'factions': sorted(gift_factions),
            'elements': sorted(gift_elements),
        },
        'axis_plan_alias_map': {
            'elements': dict(alias_map_elements),
            'factions': dict(alias_map_factions),
        },
        'drift': {
            'factions_in_matrix_not_in_live': factions_in_matrix_not_in_live,
            'elements_in_matrix_not_in_live': elements_in_matrix_not_in_live,
            'factions_in_live_not_in_matrix': factions_in_live_not_in_matrix,
            'elements_in_live_not_in_matrix': elements_in_live_not_in_matrix,
        },
        'tides_status': tides_status,
        'darkness_to_dark_alias_present': alias_map_elements.get('darkness') == 'dark',
        'mutates_source_tables': False,
        'patches_rm134b': False,
        'patches_af2a': False,
    }


def validate_alias_coverage() -> dict[str, Any]:
    """For each element/faction token that appears in matrix or gift draft
    but is NOT in live roster, verify the alias_map maps it to a live
    canonical token (or, for factions, that it is `design_pending`).

    Return a structured report (pure read-only):
      {
        'fully_covered': bool,
        'uncovered_elements': [...],
        'uncovered_factions': [...] (excluding design_pending),
        'design_pending_factions': [...],
        ...
      }
    """
    drift = preview_axis_drift_report()
    alias_elements: dict[str, str] = (
        drift.get('axis_plan_alias_map', {}).get('elements') or {}
    )
    alias_factions: dict[str, str] = (
        drift.get('axis_plan_alias_map', {}).get('factions') or {}
    )
    live_factions = set(drift.get('live', {}).get('factions') or [])
    live_elements = set(drift.get('live', {}).get('elements') or [])

    uncov_elem: list[str] = []
    for el in (drift.get('drift', {}).get('elements_in_matrix_not_in_live') or []):
        tgt = alias_elements.get(el)
        if not tgt or tgt not in live_elements:
            uncov_elem.append(el)

    uncov_fac: list[str] = []
    design_pending: list[str] = []
    for fac in (drift.get('drift', {}).get('factions_in_matrix_not_in_live') or []):
        # tides explicitly design_pending today
        if fac == 'tides':
            design_pending.append(fac)
            continue
        tgt = alias_factions.get(fac)
        if not tgt or tgt not in live_factions:
            uncov_fac.append(fac)

    fully_covered = not uncov_elem and not uncov_fac
    return {
        'enabled': False,
        'runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'preview_only': True,
        'fully_covered': fully_covered,
        'uncovered_elements': uncov_elem,
        'uncovered_factions': uncov_fac,
        'design_pending_factions': design_pending,
        'live_elements_count': len(live_elements),
        'live_factions_count': len(live_factions),
        'mutates_source_tables': False,
    }


ADAPTER_MANIFEST: dict[str, Any] = {
    'adapter_id': 'canonical_axis_dynamic_preview_axis_c',
    'task_origin': 'AXIS-C',
    'pure_functions': [
        'preview_live_axis_sets',
        'preview_axis_drift_report',
        'validate_alias_coverage',
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
    'reads_api_heroes_for_live_set': True,
    'fallback_static_source': str(_HEROES_MASTER),
}
