"""
status_second_slice_runtime_seam.py — PROJECT_T Track B INERT RUNTIME SEAM
=========================================================================

This module is the **minimal inert second-slice runtime seam** authorized by PROJECT_T.

DESIGN PRINCIPLES (must not be violated):

1. **Default no-op (identity)**: `apply_prefight_second_slice_preview()` returns the input
   `team_payload` UNCHANGED unless the flag `STATUS_RUNTIME_SECOND_SLICE_ENABLED`
   is exactly the literal `'true'` AND `dry_run=True` is passed by the caller.
2. **Single import in battle_engine**: bound to a try/except identity fallback so
   `battle_engine.py` never crashes if this module is unavailable.
3. **Calls only the pure resolver**: `status_second_slice_resolver_pure.resolve_second_slice`
   (deterministic, side-effect free). The seam itself adds NO logic beyond a defensive
   shallow-copy attach of a preview envelope.
4. **No DoT / no tick loop / no hard CC / no Borea Marchio live logic**.
5. **No DB / no external IO**. Pure Python, lazy import of the resolver.
6. **Rollback-safe**: removing this file (see
   `/app/backend/scripts/rollback_project_t_status_second_slice_battle_engine_wiring.py`)
   plus reverting the 2 single-point edits in `battle_engine.py` returns to the pre-pack
   state. The defensive fallback in `battle_engine.py` makes the module-removal-alone
   safe (battle_engine still binds an identity function).

Live activation is NOT authorized by this pack. PROJECT_U is the canary env flip pack;
PROJECT_V is dev-live; PROJECT_W is prod (each with explicit signatures).
"""
from __future__ import annotations

import os
from typing import Any, Iterable, Mapping

FLAG_NAME = 'STATUS_RUNTIME_SECOND_SLICE_ENABLED'
SEAM_VERSION = 'project_t_status_second_slice_runtime_seam_v1'


def is_seam_active() -> bool:
    """Returns True only if the canary flag is exactly the literal 'true'.

    Any other value (unset, '', 'false', '0', 'TRUE' [different case], etc.)
    returns False. Same gating policy as the first-slice seam.
    """
    return os.environ.get(FLAG_NAME, '').strip() == 'true'


def apply_prefight_second_slice_preview(
    team_payload: Any,
    active_statuses: Iterable[Mapping] | None = None,
    mode: str = 'campaign',
    *,
    dry_run: bool = False,
) -> Any:
    """Pre-fight second-slice status preview seam (INERT by default).

    Contract:
    - If flag is OFF: returns `team_payload` unchanged (identity).
    - If flag is ON but `dry_run=False`: returns `team_payload` unchanged.
      LIVE behavior is intentionally NOT activated by this pack.
    - If flag is ON AND `dry_run=True`: computes the second-slice deltas via the
      pure resolver and ATTACHES a `status_second_slice_preview` key to a
      shallow copy of the payload. The original `team_payload` is NOT mutated.
      No stats are actually changed: this is a *preview only*.
    """
    # Default no-op (identity) path.
    if not is_seam_active():
        return team_payload
    if not dry_run:
        # Flag ON but no dry-run: live activation is not authorized by PROJECT_T.
        return team_payload

    # Dry-run preview branch — explicit, isolated, never reached by live battle.
    resolve_second_slice = None
    for _impl in (
        lambda: __import__('game_logic.status_second_slice_resolver_pure', fromlist=['resolve_second_slice']).resolve_second_slice,
        lambda: __import__('status_second_slice_resolver_pure', fromlist=['resolve_second_slice']).resolve_second_slice,
    ):
        try:
            resolve_second_slice = _impl()
            break
        except Exception:
            continue
    if resolve_second_slice is None:
        # Last-resort: absolute path loader.
        try:
            import importlib.util as _ilu
            _spec = _ilu.spec_from_file_location(
                '_status_second_slice_resolver_pure_seam_local',
                '/app/backend/game_logic/status_second_slice_resolver_pure.py',
            )
            _mod = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            resolve_second_slice = _mod.resolve_second_slice
        except Exception:
            return team_payload

    deltas = resolve_second_slice(active_statuses or [], mode)

    if isinstance(team_payload, dict):
        preview = dict(team_payload)
        preview['status_second_slice_preview'] = deltas
        preview['__second_slice_seam_version'] = SEAM_VERSION
        return preview
    return {
        'original_payload': team_payload,
        'status_second_slice_preview': deltas,
        '__second_slice_seam_version': SEAM_VERSION,
    }


__all__ = [
    'FLAG_NAME',
    'SEAM_VERSION',
    'is_seam_active',
    'apply_prefight_second_slice_preview',
]
