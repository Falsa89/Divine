#!/usr/bin/env python3
"""PROJECT S — STATUS SECOND SLICE PURE RESOLVER (inert isolated module).

Purpose
-------
Isolated, deterministic, side-effect-free resolver for the second status slice.
In-scope status families:
    - debuff_offensive
    - debuff_defensive
    - speed_up
    - speed_down

Out-of-scope status families (silently ignored):
    DoT/tick, Poison/Burn/Bleed, Freeze/Stun/Sleep/Hard CC,
    Shield/Barrier, HoT, Revive, Immunity/Cleanse runtime,
    Borea Marchio live logic, Boss-special status logic.

Hard guarantees
---------------
* deterministic     : same input -> identical output, no random.
* side-effect free  : no I/O, no DB, no HTTP, no logging.
* no mutable global state.
* no battle_engine / battle_core / requests / pymongo / motor / fastapi import.
* malformed / negative / NaN inputs are safely clamped.
* output is always a dict of stat_pct deltas (floats), clamped to caps.

This module is NOT imported by battle runtime. It exists only for:
* Project S validator scripts;
* future Project T single-point wiring (flag-gated).
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

__all__ = (
    'IN_SCOPE_FAMILIES',
    'OUT_OF_SCOPE_FAMILIES',
    'PER_STATUS_CAPS_PCT',
    'AGGREGATE_CAPS_PCT',
    'MODE_MULTIPLIERS',
    'STAT_TARGET_BY_FAMILY',
    'resolve_second_slice',
    'validate_invariants_static',
)

IN_SCOPE_FAMILIES = ('debuff_offensive', 'debuff_defensive', 'speed_up', 'speed_down')

OUT_OF_SCOPE_FAMILIES = (
    'dot', 'poison', 'burn', 'bleed',
    'freeze', 'stun', 'sleep', 'hard_cc',
    'shield', 'barrier', 'hot', 'revive',
    'immunity', 'cleanse', 'borea_marchio',
    'boss_special',
)

PER_STATUS_CAPS_PCT: Mapping[str, float] = {
    'debuff_offensive': 30.0,
    'debuff_defensive': 30.0,
    'speed_up':         25.0,
    'speed_down':       25.0,
}

AGGREGATE_CAPS_PCT: Mapping[str, float] = {
    'offensive_debuff': 40.0,
    'defensive_debuff': 40.0,
    'speed':            30.0,
}

MODE_MULTIPLIERS: Mapping[str, float] = {
    'campaign': 1.00,
    'pvp':      0.75,
    'boss':     0.50,
}

STAT_TARGET_BY_FAMILY: Mapping[str, str] = {
    'debuff_offensive': 'atk_pct',
    'debuff_defensive': 'def_pct',
    'speed_up':         'speed_pct',
    'speed_down':       'speed_pct',
}

_EMPTY_DELTAS = {'atk_pct': 0.0, 'def_pct': 0.0, 'speed_pct': 0.0}


def _safe_nonneg_pct(value: Any) -> float:
    """Coerce to a finite non-negative float; malformed/negative/NaN -> 0.0."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return 0.0
    if f != f:  # NaN check
        return 0.0
    if f < 0.0:
        return 0.0
    if f > 1e6:  # absurdly large -> clamp to large but finite
        return 1e6
    return f


def _clamp(v: float, lo: float, hi: float) -> float:
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


def resolve_second_slice(active_statuses: Iterable[Any], mode: str = 'campaign') -> dict:
    """Pure resolver.

    Parameters
    ----------
    active_statuses : iterable of mapping-like entries with keys:
        - 'family' : one of IN_SCOPE_FAMILIES (others ignored)
        - 'value_pct' : non-negative float magnitude (malformed -> 0)
    mode : 'campaign' (default) | 'pvp' | 'boss' (unknown -> 'campaign')

    Returns
    -------
    dict with keys: 'atk_pct', 'def_pct', 'speed_pct' — each a float.
        * offensive/defensive debuffs emit NEGATIVE deltas (mitigation reduces atk/def of victim).
        * speed delta is net (speed_up - speed_down) clamped to ±aggregate speed cap.
        * mode multiplier is applied last (pvp 0.75x, boss 0.50x).
    """
    if not isinstance(active_statuses, (list, tuple)):
        # Non-iterable defensive guard — also covers None.
        if active_statuses is None:
            return dict(_EMPTY_DELTAS)
        try:
            active_statuses = list(active_statuses)
        except TypeError:
            return dict(_EMPTY_DELTAS)

    mode_mult = MODE_MULTIPLIERS.get(mode if isinstance(mode, str) else 'campaign', 1.0)

    family_totals = {fam: 0.0 for fam in IN_SCOPE_FAMILIES}

    for entry in active_statuses:
        if not isinstance(entry, Mapping):
            continue
        fam = entry.get('family')
        if fam not in IN_SCOPE_FAMILIES:
            # out-of-scope silently ignored
            continue
        per_cap = PER_STATUS_CAPS_PCT[fam]
        v = _safe_nonneg_pct(entry.get('value_pct', 0.0))
        v = _clamp(v, 0.0, per_cap)
        family_totals[fam] += v

    # Aggregate caps (additive within family, hard-capped)
    off_total  = _clamp(family_totals['debuff_offensive'], 0.0, AGGREGATE_CAPS_PCT['offensive_debuff'])
    def_total  = _clamp(family_totals['debuff_defensive'], 0.0, AGGREGATE_CAPS_PCT['defensive_debuff'])
    speed_up_t = _clamp(family_totals['speed_up'],         0.0, AGGREGATE_CAPS_PCT['speed'])
    speed_dn_t = _clamp(family_totals['speed_down'],       0.0, AGGREGATE_CAPS_PCT['speed'])

    # Opposing pair cancel for speed; net then clamped to ±aggregate cap.
    net_speed = _clamp(speed_up_t - speed_dn_t, -AGGREGATE_CAPS_PCT['speed'], AGGREGATE_CAPS_PCT['speed'])

    deltas = {
        'atk_pct':   -off_total * mode_mult,  # debuff -> negative
        'def_pct':   -def_total * mode_mult,  # debuff -> negative
        'speed_pct':  net_speed * mode_mult,  # signed
    }
    return deltas


def validate_invariants_static() -> bool:
    """Static self-check: returns True iff all internal invariants hold.

    Used by Project S validators; does not access runtime.
    """
    # Caps and families must align
    if set(PER_STATUS_CAPS_PCT.keys()) != set(IN_SCOPE_FAMILIES):
        return False
    if set(STAT_TARGET_BY_FAMILY.keys()) != set(IN_SCOPE_FAMILIES):
        return False
    # Per-status caps must be ≤ aggregate caps (so per-status cannot exceed aggregate alone)
    if PER_STATUS_CAPS_PCT['debuff_offensive'] > AGGREGATE_CAPS_PCT['offensive_debuff']:
        return False
    if PER_STATUS_CAPS_PCT['debuff_defensive'] > AGGREGATE_CAPS_PCT['defensive_debuff']:
        return False
    if PER_STATUS_CAPS_PCT['speed_up'] > AGGREGATE_CAPS_PCT['speed']:
        return False
    if PER_STATUS_CAPS_PCT['speed_down'] > AGGREGATE_CAPS_PCT['speed']:
        return False
    # Mode multipliers bounds
    if MODE_MULTIPLIERS.get('pvp', 1.0) > 0.75:
        return False
    if MODE_MULTIPLIERS.get('boss', 1.0) > 0.50:
        return False
    if MODE_MULTIPLIERS.get('campaign', 0.0) != 1.0:
        return False
    # No out-of-scope family must accidentally be in scope
    if set(IN_SCOPE_FAMILIES) & set(OUT_OF_SCOPE_FAMILIES):
        return False
    # Smoke: empty list -> zero deltas
    out = resolve_second_slice([], 'campaign')
    if out != _EMPTY_DELTAS:
        return False
    # Smoke: None -> zero deltas (defensive)
    if resolve_second_slice(None) != _EMPTY_DELTAS:  # type: ignore[arg-type]
        return False
    # Smoke: malformed entry ignored
    if resolve_second_slice([{'family': 'dot', 'value_pct': 50}]) != _EMPTY_DELTAS:
        return False
    # Smoke: single offensive debuff clamped to per-status cap
    out = resolve_second_slice([{'family': 'debuff_offensive', 'value_pct': 9999}], 'campaign')
    if round(out['atk_pct'], 6) != -PER_STATUS_CAPS_PCT['debuff_offensive']:
        return False
    return True
