"""PROJECT_J Track B — Status First Slice Pure Resolver (INERT, NOT WIRED).

Pure, deterministic, side-effect free resolver for `buff_offensive` and
`buff_defensive` statuses on a battle entity. Maps a list of active statuses
to a stat-delta envelope.

INVARIANTS (enforced by Track C validators):
  * Pure function (no global state, no I/O, no DB write).
  * Deterministic: identical input ALWAYS produces identical output.
  * Side-effect free: does NOT mutate inputs.
  * NOT imported by battle_engine.py / battle_core.py / combat.tsx (this pack).
  * Envelope respects master cap + per-category cap (clamped).
  * Categories accepted: ONLY {'buff_offensive', 'buff_defensive'}; others ignored
    (out of slice scope).
  * Default flag `STATUS_RUNTIME_BUFF_SLICE_ENABLED` is OFF.
  * `is_runtime_active()` returns False unless flag is exactly 'true'.

FUTURE: a separate activation pack will wire this resolver into the pre-fight
stat layer (NOT tick loop) behind `STATUS_RUNTIME_BUFF_SLICE_ENABLED=true`.
The tick loop is explicitly OUT OF SCOPE for this slice.
"""
import os
from typing import Iterable

SLICE_VERSION = "project_j_first_slice_v1"
FLAG_NAME = "STATUS_RUNTIME_BUFF_SLICE_ENABLED"
ALLOWED_CATEGORIES = frozenset({"buff_offensive", "buff_defensive"})

# Master caps (mirror project_g_housing cap snapshot v1 stat ceilings to stay
# consistent with the global stat layer envelope philosophy).
MASTER_CAP_PCT = {
    "atk_pct": 0.30,
    "def_pct": 0.30,
    "hp_pct": 0.30,
    "crit_pct": 0.15,
}
PER_CATEGORY_CAP_PCT = {
    "buff_offensive": {"atk_pct": 0.30, "crit_pct": 0.15},
    "buff_defensive": {"def_pct": 0.30, "hp_pct": 0.30},
}
STAT_KEYS_ZERO = ("atk_pct", "def_pct", "hp_pct", "crit_pct")


def is_runtime_active() -> bool:
    """Return True iff `STATUS_RUNTIME_BUFF_SLICE_ENABLED` is exactly 'true' (case-insensitive)."""
    return os.environ.get(FLAG_NAME, "").strip().lower() == "true"


def _zero_envelope() -> dict:
    return {k: 0.0 for k in STAT_KEYS_ZERO}


def resolve_buff_envelope(active_statuses: Iterable[dict]) -> dict:
    """Resolve a list of active buff_offensive/buff_defensive statuses into a
    deterministic stat-delta envelope. PURE / DETERMINISTIC / SIDE-EFFECT FREE.

    Args:
        active_statuses: iterable of dicts with at least keys:
            - category: 'buff_offensive' | 'buff_defensive'
            - stat:     'atk_pct' | 'def_pct' | 'hp_pct' | 'crit_pct'
            - value:    float (already multiplied by stacks if applicable)

    Returns:
        Envelope dict with stat keys mapped to clamped floats.
        Stats outside the allowed categories are ignored.
    """
    envelope = _zero_envelope()
    if active_statuses is None:
        return envelope
    # Aggregate per (category, stat)
    per_cat: dict = {c: dict.fromkeys(STAT_KEYS_ZERO, 0.0) for c in ALLOWED_CATEGORIES}
    for s in active_statuses:
        if not isinstance(s, dict):
            continue
        cat = s.get("category")
        stat = s.get("stat")
        try:
            val = float(s.get("value", 0.0))
        except (TypeError, ValueError):
            continue
        if cat not in ALLOWED_CATEGORIES:
            continue
        if stat not in STAT_KEYS_ZERO:
            continue
        per_cat[cat][stat] += max(0.0, val)
    # Apply per-category caps
    for cat, stats in per_cat.items():
        cat_caps = PER_CATEGORY_CAP_PCT.get(cat, {})
        for stat in STAT_KEYS_ZERO:
            cap = cat_caps.get(stat)
            if cap is None:
                stats[stat] = 0.0  # stat outside category scope contributes 0
            else:
                stats[stat] = min(stats[stat], cap)
    # Sum across categories then clamp to master cap
    for stat in STAT_KEYS_ZERO:
        total = sum(per_cat[c][stat] for c in ALLOWED_CATEGORIES)
        envelope[stat] = min(total, MASTER_CAP_PCT[stat])
    return envelope


def validate_invariants_static() -> bool:
    """Sanity check used by the Track C validator. Pure boolean."""
    if not isinstance(ALLOWED_CATEGORIES, frozenset): return False
    if ALLOWED_CATEGORIES != frozenset({"buff_offensive", "buff_defensive"}): return False
    for stat in STAT_KEYS_ZERO:
        if stat not in MASTER_CAP_PCT: return False
        if MASTER_CAP_PCT[stat] <= 0.0: return False
    # Per-category cap may NOT exceed master cap
    for cat, caps in PER_CATEGORY_CAP_PCT.items():
        for stat, cap in caps.items():
            if cap > MASTER_CAP_PCT[stat]: return False
    return True


__all__ = [
    "SLICE_VERSION",
    "FLAG_NAME",
    "ALLOWED_CATEGORIES",
    "MASTER_CAP_PCT",
    "PER_CATEGORY_CAP_PCT",
    "is_runtime_active",
    "resolve_buff_envelope",
    "validate_invariants_static",
]
