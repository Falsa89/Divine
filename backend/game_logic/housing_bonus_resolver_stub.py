"""
PROJECT_B Track B — HousingBonusResolver INERT STUB.

Pure function module. **NOT imported** by:
  - /app/backend/server.py
  - /app/backend/game_systems.py
  - /app/backend/battle_engine.py
  - /app/backend/battle_core.py
  - any /app/backend/routes/*
  - any /app/frontend/**

Il resolver e' **inert**: tutti i bonus emessi sono **0** in questa versione
stub. Quando l'Housing MVP sara' implementato in un pack dedicato, lo stub
sara' sostituito (o esteso) con la logica di calcolo cap-aware effettiva.

Canonical caps (da Housing v2 canonical, non applicati live in questo stub):
  - per_room
  - category
  - item
  - bonus
  - mode
  - master_cap
"""
from __future__ import annotations

from typing import Any, Dict, List

# Canonical caps (read-only metadata; NOT enforced live by this stub).
CANONICAL_CAPS: Dict[str, int] = {
    "per_room": 6,
    "category": 4,
    "item": 12,
    "bonus": 8,
    "mode": 2,
    "master_cap": 30,
}

# Canonical output shape (all values forced to 0 in stub).
INERT_BONUS_OUTPUT: Dict[str, int] = {
    "hp_bonus": 0,
    "atk_bonus": 0,
    "def_bonus": 0,
    "healing_bonus": 0,
}

# Visible marker for self-introspection and validator.
INERT_MARKER: str = "HOUSING_BONUS_RESOLVER_STUB_INERT_PROJECT_B_TRACK_B_V1"


def resolve_housing_bonus(user_state: Dict[str, Any]) -> Dict[str, int]:
    """Return a frozen zero-bonus dict regardless of input.

    Args:
        user_state: shape `{user_id, housing_rooms[], objects[], residents[]}`.
                    Validated only for type; values are ignored by the stub.

    Returns:
        A *new* dict equal to ``INERT_BONUS_OUTPUT`` (deep copy semantics for
        ints not required, but the dict object is fresh per call).
    """
    # Defensive type checks for future contract validation.
    if not isinstance(user_state, dict):
        raise TypeError("user_state must be a dict")
    for key in ("housing_rooms", "objects", "residents"):
        if key in user_state and not isinstance(user_state[key], list):
            raise TypeError(f"user_state['{key}'] must be a list if present")
    return dict(INERT_BONUS_OUTPUT)


def validate_caps_definition(caps: Dict[str, int]) -> List[str]:
    """Return list of cap-definition violations; empty list = valid.

    Pure function. Used by `validate_project_b_housing_resolver_stub_inert.py`.
    """
    errors: List[str] = []
    required = set(CANONICAL_CAPS.keys())
    missing = required - set(caps.keys())
    if missing:
        errors.append(f"missing cap keys: {sorted(missing)}")
    for k, v in caps.items():
        if k in CANONICAL_CAPS and (not isinstance(v, int) or v <= 0):
            errors.append(f"cap '{k}' must be positive int, got {v!r}")
    return errors


__all__ = [
    "CANONICAL_CAPS",
    "INERT_BONUS_OUTPUT",
    "INERT_MARKER",
    "resolve_housing_bonus",
    "validate_caps_definition",
]
