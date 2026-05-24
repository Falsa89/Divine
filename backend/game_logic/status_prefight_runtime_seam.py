"""
status_prefight_runtime_seam.py — PROJECT_L Track B INERT RUNTIME SEAM
=====================================================================

This module is the **minimal inert runtime seam** authorized by PROJECT_L.

DESIGN PRINCIPLES (must not be violated):

1. **Default no-op**: `apply_prefight_status_slice_preview()` returns the input
   `team_payload` UNCHANGED unless the flag `STATUS_RUNTIME_BUFF_SLICE_ENABLED`
   is exactly `'true'` AND `dry_run=True` is passed by the caller.
2. **Not imported live**: this module is NOT imported by `battle_engine.py`,
   `battle_core.py` nor any route in `/app/backend/routes/`. It is reachable
   only by tests, validators and explicit canary fixtures.
3. **No DoT / no tick loop**: this module only applies the FIRST SLICE
   pre-fight buff envelope (`buff_offensive`, `buff_defensive`) once, on the
   pre-fight static stats. It does NOT introduce any tick, round, healing or
   damage formula change.
4. **No DB / no external IO**: pure Python; nothing here calls the database,
   the network, or any battle simulation function.
5. **Rollback-safe**: deleting this file (see
   `/app/backend/scripts/rollback_project_l_minimal_battle_runtime_seam.py`)
   restores the previous state with zero side-effects, because nothing imports
   it at runtime.

The seam is exposed for future activation: when (and only when) PROJECT_M
introduces flagged canary execution, a single explicit, audited import inside
`battle_engine.simulate_battle()` will be authorized.
"""

from __future__ import annotations

import os
from typing import Any, Iterable, Mapping

# Lazy import: kept inside the function body so module loading remains pure
# and side-effect free (no implicit registrations).

FLAG_NAME = 'STATUS_RUNTIME_BUFF_SLICE_ENABLED'
SEAM_VERSION = 'project_l_status_prefight_runtime_seam_v1'


def is_seam_active() -> bool:
    """Returns True only if the canary flag is exactly the literal 'true'.

    Any other value (unset, '', 'false', '0', 'TRUE' [different case], etc.)
    returns False. This is the same gating policy used by
    `status_first_slice_resolver_pure.is_runtime_active()`.
    """
    return os.environ.get(FLAG_NAME, '').strip() == 'true'


def apply_prefight_status_slice_preview(
    team_payload: Any,
    active_statuses: Iterable[Mapping] | None = None,
    *,
    dry_run: bool = False,
) -> Any:
    """Pre-fight first-slice status preview seam (INERT by default).

    Contract:
    - If flag is OFF: returns `team_payload` unchanged (identity).
    - If flag is ON but `dry_run=False`: returns `team_payload` unchanged
      (LIVE behavior is intentionally NOT activated by this pack — only
      PROJECT_M may flip this).
    - If flag is ON AND `dry_run=True`: computes the buff envelope via the
      pure resolver and ATTACHES a `status_envelope_preview` key to a
      shallow copy of the payload. The original `team_payload` is NOT
      mutated. No stats are actually changed: this is a *preview only*.

    Parameters
    ----------
    team_payload
        Arbitrary opaque payload (dict, list, or any object). Returned as-is
        unless the dry-run preview branch is active.
    active_statuses
        Iterable of status dicts compatible with
        `status_first_slice_resolver_pure.resolve_buff_envelope`.
    dry_run
        Must be passed explicitly by tests/fixtures. Live runtime callers
        MUST NOT pass `dry_run=True`. Live runtime is not authorized in
        PROJECT_L; this gate will be enforced again by PROJECT_M.
    """
    # Default no-op path: anything but (flag ON AND dry_run) returns input.
    if not is_seam_active():
        return team_payload
    if not dry_run:
        # Flag ON but no dry-run requested: live activation is not authorized
        # by PROJECT_L. Return unchanged to preserve battle behavior.
        return team_payload

    # Dry-run preview branch — explicit, isolated, never reached by live battle.
    # Try multiple import styles so the seam is callable both as a package
    # module (live runtime) and as a stand-alone module (tests / validators
    # using `importlib.util.spec_from_file_location`). The seam MUST NOT crash
    # live callers under any circumstance.
    resolve_buff_envelope = None
    for _impl in (
        lambda: __import__('game_logic.status_first_slice_resolver_pure', fromlist=['resolve_buff_envelope']).resolve_buff_envelope,
        lambda: __import__('status_first_slice_resolver_pure', fromlist=['resolve_buff_envelope']).resolve_buff_envelope,
    ):
        try:
            resolve_buff_envelope = _impl()
            break
        except Exception:
            continue
    if resolve_buff_envelope is None:
        # Last-resort: load resolver by absolute path without registering it
        # globally. This keeps the seam self-contained.
        try:
            import importlib.util as _ilu
            _spec = _ilu.spec_from_file_location(
                '_status_first_slice_resolver_pure_seam_local',
                '/app/backend/game_logic/status_first_slice_resolver_pure.py',
            )
            _mod = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            resolve_buff_envelope = _mod.resolve_buff_envelope
        except Exception:
            return team_payload
    envelope = resolve_buff_envelope(active_statuses or [])

    # Build a shallow copy so the caller's payload is not mutated.
    if isinstance(team_payload, dict):
        preview = dict(team_payload)
        preview['status_envelope_preview'] = envelope
        preview['__seam_version'] = SEAM_VERSION
        return preview
    # Non-dict payloads: wrap into a preview envelope dict (never mutate).
    return {
        'original_payload': team_payload,
        'status_envelope_preview': envelope,
        '__seam_version': SEAM_VERSION,
    }


__all__ = [
    'FLAG_NAME',
    'SEAM_VERSION',
    'is_seam_active',
    'apply_prefight_status_slice_preview',
]
