"""STACK-G-PRE — Inert preview adapter for the future battle cap resolver.

This module exists for future wiring of `global_modifier_cap_resolver`
into the battle runtime. It is **NOT** imported by `battle_engine.py`,
`battle_core.py`, `combat.tsx`, `game_systems.py` or `synergy_system.py`.

The entry point `resolve_battle_cap_preview` always returns
`runtime_attached=False` and performs NO DB writes, NO inventory
mutation, and NO Borea activation. It exists solely so that a future
STACK-G task can swap in a real implementation behind a feature flag.

ABSOLUTE RULES (enforced by the audit):
  - No top-level import of `battle_engine`, `battle_core`, `combat`.
  - No import of any frontend module.
  - No `motor`/`pymongo`/database write call.
  - Returns `runtime_attached=False` until the feature flag
    `STACK_G_BATTLE_RUNTIME_ENABLED` is explicitly approved.
"""
from __future__ import annotations
import os
from typing import Any

# We can read the existing inert resolver design data. We do NOT import
# anything from battle/runtime modules.
try:  # pragma: no cover
    from backend.data import global_modifier_cap_resolver as _resolver  # type: ignore
except Exception:
    _resolver = None

_FORBIDDEN_ALIASES = frozenset({'borea', 'greek_borea', 'primordial_gaia'})
_FEATURE_FLAG_NAME = 'STACK_G_BATTLE_RUNTIME_ENABLED'


def _feature_flag_enabled() -> bool:
    """Always returns False until the user explicitly approves STACK-G."""
    raw = os.environ.get(_FEATURE_FLAG_NAME)
    # Strict allow-list semantics: only one specific token enables it.
    return raw == 'true_explicit_stack_g_battle_runtime_on'


def _safety_envelope() -> dict[str, Any]:
    return {
        'preview_only': True,
        'design_only': True,
        'runtime_attached': False,
        'battle_runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'feature_flag_dependency': _FEATURE_FLAG_NAME,
        'feature_flag_currently_enabled': _feature_flag_enabled(),
        'hidden_aliases_blocked': sorted(_FORBIDDEN_ALIASES),
    }


def resolve_battle_cap_preview(
    hero_id: str,
    element_token: str,
    faction_token: str,
    buff_sources: list[tuple[str, float]] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Returns a fully inert preview of the cap resolver decision.

    Even if a future STACK-G enables the feature flag, this preview
    function alone will never mutate battle/DB state — wiring into the
    battle runtime is a separate, audited task.
    """
    hid = (hero_id or '').strip().lower()
    eid = (element_token or '').strip().lower()
    fid = (faction_token or '').strip().lower()

    borea_filtered = bool(
        hid in _FORBIDDEN_ALIASES
        or fid in _FORBIDDEN_ALIASES
        or eid in _FORBIDDEN_ALIASES
    )
    clipped_sources: list[dict[str, Any]] = []
    applied_cap_pct: float = 0.0

    # Even if the resolver design data is present, we DO NOT compute a
    # live applied cap until STACK-G is approved — we just enumerate
    # the input shape for auditability.
    sources = buff_sources or []
    for s in sources:
        if not isinstance(s, (list, tuple)) or len(s) != 2:
            continue
        sid, mag = s
        clipped_sources.append({
            'source_id': str(sid),
            'magnitude_pct': float(mag) if isinstance(mag, (int, float)) else 0.0,
            'applied': False,
            'reason': 'preview_only_no_battle_runtime',
        })

    return {
        'task_origin': 'STACK-G-PRE',
        'preview_version': 'v1',
        'hero_id': hid,
        'element_token': eid,
        'faction_token': fid,
        'context': context or {},
        'runtime_attached': False,
        'applied_cap_pct': applied_cap_pct,
        'clipped_sources': clipped_sources,
        'borea_filtered': borea_filtered,
        'safety_envelope': _safety_envelope(),
    }


__all__ = ['resolve_battle_cap_preview']
