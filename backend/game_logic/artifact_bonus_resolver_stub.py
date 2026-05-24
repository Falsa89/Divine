"""
PROJECT_C Track H — Artifact Bonus Resolver Stub (PURE, INERT).

NON deve essere importato a runtime in V_C. Lo scopo è fornire un punto di
estensione contrattuale per il futuro applicativo di bonus artefatti, mantenendo
un ritorno zero-bonus stabile.

Contratti:
- `resolve_artifact_bonus(user_artifacts: list) -> dict`
    Ritorna sempre `{hp_pct, atk_pct, def_pct, crit_pct, source='resolver_stub_inert'}`
    in V_C, indipendentemente dall'input.
- `validate_caps_definition() -> bool`
    Ritorna True. Caps dichiarate solo come documentazione interna (no apply).
"""
from __future__ import annotations

from typing import Iterable

# Caps documentate (anti-power-creep). NON applicate a runtime in V_C.
ARTIFACT_BONUS_CAPS = {
    "hp_pct": {"min": -50, "max": 50},
    "atk_pct": {"min": -50, "max": 50},
    "def_pct": {"min": -50, "max": 50},
    "crit_pct": {"min": -50, "max": 50},
}

ZERO_BONUS_ENVELOPE = {
    "hp_pct": 0,
    "atk_pct": 0,
    "def_pct": 0,
    "crit_pct": 0,
    "source": "resolver_stub_inert",
}


def resolve_artifact_bonus(user_artifacts: Iterable | None = None) -> dict:
    """Ritorna sempre l'envelope zero-bonus in V_C. Input ignorato per contratto.

    Args:
        user_artifacts: lista (ignorata in V_C) della dotazione artefatti del giocatore.

    Returns:
        dict: envelope contrattuale a zero-bonus con source='resolver_stub_inert'.
    """
    # Defensivamente accettiamo anche None / non-iterable senza sollevare.
    _ = user_artifacts  # placeholder per futuro logic v_e+
    return dict(ZERO_BONUS_ENVELOPE)


def validate_caps_definition() -> bool:
    """Verifica strutturale delle caps documentate. Pure, no side-effect."""
    for key, bounds in ARTIFACT_BONUS_CAPS.items():
        if not isinstance(key, str) or not key.endswith("_pct"):
            return False
        if "min" not in bounds or "max" not in bounds:
            return False
        if bounds["min"] >= bounds["max"]:
            return False
    return True
