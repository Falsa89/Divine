"""PROJECT_D Track C — Status Effect Runtime Adapter Stub (INERT).

*** NON DEVE ESSERE IMPORTATO A RUNTIME. ***

Fornisce contratti di mapping per il futuro adapter status → battle engine. Il
modulo è puro e safe-to-unit-test offline; nessun side-effect, nessun import
di battle_engine/battle_core/combat.

Mapping contracts (validati dal validator):
  - status_id          : str
  - category           : in CANONICAL_CATEGORIES
  - polarity           : in {"positive", "negative", "neutral"}
  - stacking           : in {"none", "refresh", "stack_capped"}
  - boss_behavior      : in {"normal", "reduced", "immune"}
  - source_lock        : bool
  - display_hint       : str (es. "buff_icon", "debuff_icon", "dot_icon", "shield_icon")
"""
from __future__ import annotations

from typing import Any

CANONICAL_CATEGORIES = (
    "buff_offensive", "buff_defensive", "buff_support",
    "debuff_offensive", "debuff_defensive",
    "control", "dot", "hot", "shield", "meta",
)

CANONICAL_POLARITIES = ("positive", "negative", "neutral")
CANONICAL_STACKING = ("none", "refresh", "stack_capped")
CANONICAL_BOSS_BEHAVIORS = ("normal", "reduced", "immune")
CANONICAL_DISPLAY_HINTS = (
    "buff_icon", "debuff_icon", "dot_icon", "hot_icon",
    "shield_icon", "control_icon", "meta_icon",
)

# Adapter contract version. NON applicato live in V_D.
ADAPTER_CONTRACT_VERSION = "status_effect_runtime_adapter_stub_v1"


def build_status_mapping(status_id: str,
                        category: str,
                        polarity: str,
                        stacking: str,
                        boss_behavior: str,
                        source_lock: bool,
                        display_hint: str) -> dict:
    """Build a pure status mapping dict. Pure, no side-effect.

    Raises ValueError if any field is outside canonical sets.
    """
    if not isinstance(status_id, str) or not status_id:
        raise ValueError("status_id must be a non-empty str")
    if category not in CANONICAL_CATEGORIES:
        raise ValueError(f"category {category!r} not in CANONICAL_CATEGORIES")
    if polarity not in CANONICAL_POLARITIES:
        raise ValueError(f"polarity {polarity!r} not in CANONICAL_POLARITIES")
    if stacking not in CANONICAL_STACKING:
        raise ValueError(f"stacking {stacking!r} not in CANONICAL_STACKING")
    if boss_behavior not in CANONICAL_BOSS_BEHAVIORS:
        raise ValueError(f"boss_behavior {boss_behavior!r} not in CANONICAL_BOSS_BEHAVIORS")
    if not isinstance(source_lock, bool):
        raise ValueError("source_lock must be bool")
    if display_hint not in CANONICAL_DISPLAY_HINTS:
        raise ValueError(f"display_hint {display_hint!r} not in CANONICAL_DISPLAY_HINTS")
    return {
        "status_id": status_id,
        "category": category,
        "polarity": polarity,
        "stacking": stacking,
        "boss_behavior": boss_behavior,
        "source_lock": source_lock,
        "display_hint": display_hint,
        "contract_version": ADAPTER_CONTRACT_VERSION,
        "runtime_active": False,
    }


def validate_canonical_sets() -> bool:
    """Verifica strutturale delle 5 famiglie canoniche. Pure."""
    if len(CANONICAL_CATEGORIES) != 10: return False
    if len(CANONICAL_POLARITIES) != 3: return False
    if len(CANONICAL_STACKING) != 3: return False
    if len(CANONICAL_BOSS_BEHAVIORS) != 3: return False
    if len(CANONICAL_DISPLAY_HINTS) != 7: return False
    return True
